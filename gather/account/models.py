# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib

from datetime import datetime, timedelta
from flask import current_app
from werkzeug import security
from gather.extensions import db

ROLES = {
    "banned": 0,
    "user": 1,
    "staff": 6,
    "admin": 9
}


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default="user")

    website = db.Column(db.String(100), nullable=True, default="")
    description = db.Column(db.String(500), nullable=True, default="")
    css = db.Column(db.String(), nullable=True, default="")

    created = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(20), nullable=True, default="")

    api_token = db.Column(db.String(40))
    feeling_lucky = db.Column(db.Boolean, default=False, nullable=True)

    def __init__(self, **kwargs):
        self.token = self.create_token(16)

        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)

        if 'username' in kwargs:
            username = kwargs.pop('username')
            self.username = username.lower()

        if 'email' in kwargs:
            email = kwargs.pop('email')
            self.email = email.lower()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<Account: %s>' % self.username

    def avatar(self, size=48):
        size *= 2  # Retina
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s" % (md5email, size)
        return current_app.config['GRAVATAR_BASE_URL'] + query

    @staticmethod
    def create_password(raw):
        passwd = '%s%s' % (raw, current_app.config['PASSWORD_SECRET'])
        return security.generate_password_hash(passwd)

    @staticmethod
    def create_token(length=16):
        return security.gen_salt(length)

    @property
    def is_staff(self):
        return self.is_admin or self.role == "staff"

    @property
    def is_admin(self):
        return self.id == 1 or self.role == "admin"

    def check_password(self, raw):
        passwd = '%s%s' % (raw, current_app.config['PASSWORD_SECRET'])
        return security.check_password_hash(self.password, passwd)

    def change_password(self, raw):
        self.password = self.create_password(raw)
        self.token = self.create_token()

    def generate_api_token(self):
        token = security.gen_salt(40)
        while Account.query.filter_by(api_token=token).count():
            token = security.gen_salt(40)
        self.api_token = token
        self.save()
        return self

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def clean_junk_users(cls):
        a_month_ago = datetime.utcnow() - timedelta(days=30)
        from gather.topic.models import Topic, Reply
        for user in cls.query.all():
            if user.created >= a_month_ago:
                pass
            if not Topic.query.filter_by(author=user).count():
                if not Reply.query.filter_by(author=user).count():
                    db.session.delete(user)
        db.session.commit()
