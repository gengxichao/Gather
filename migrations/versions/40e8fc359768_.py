"""empty message

Revision ID: 40e8fc359768
Revises: 3d569239043f
Create Date: 2014-03-14 23:58:52.158538

"""

# revision identifiers, used by Alembic.
revision = '40e8fc359768'
down_revision = '26dfc02ce3ff'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('node', sa.Column('parent_node_id', sa.Integer(), nullable=True))
    op.create_index('ix_node_parent_node_id', 'node', ['parent_node_id'], unique=False)
    op.create_unique_constraint('uc_user_read_topic', 'read_topic', ['user_id', 'topic_id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uc_user_read_topic', 'read_topic')
    op.drop_index('ix_node_parent_node_id', table_name='node')
    op.drop_column('node', 'parent_node_id')
    ### end Alembic commands ###
