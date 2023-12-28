"""bd

Revision ID: 7fc2fa24a5d6
Revises: a8f35c8b2a58
Create Date: 2023-12-26 14:00:08.619426

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7fc2fa24a5d6'
down_revision = 'a8f35c8b2a58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_user_last_message', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('date_last_message', sa.String(length=50), nullable=False))
        batch_op.create_foreign_key(None, 'user', ['id_user_last_message'], ['id'])

    with op.batch_alter_table('mensajes', schema=None) as batch_op:
        batch_op.drop_column('mensaje')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('estado')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('estado', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))

    with op.batch_alter_table('mensajes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mensaje', mysql.VARCHAR(length=1000), nullable=False))

    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('date_last_message')
        batch_op.drop_column('id_user_last_message')

    # ### end Alembic commands ###