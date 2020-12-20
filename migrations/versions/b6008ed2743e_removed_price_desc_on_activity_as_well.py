"""removed price_desc on activity as well

Revision ID: b6008ed2743e
Revises: ef0aeb3dc591
Create Date: 2020-12-20 16:27:31.783058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6008ed2743e'
down_revision = 'ef0aeb3dc591'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activity', 'price_desc')
    op.drop_column('submissions', 'price_desc')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('submissions', sa.Column('price_desc', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('activity', sa.Column('price_desc', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
