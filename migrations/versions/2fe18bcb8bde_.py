"""empty message

Revision ID: 2fe18bcb8bde
Revises: 7a2f27ca6ab8
Create Date: 2018-11-05 22:02:15.252642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fe18bcb8bde'
down_revision = '7a2f27ca6ab8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('_indexer', sa.UnicodeText(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', '_indexer')
    # ### end Alembic commands ###
