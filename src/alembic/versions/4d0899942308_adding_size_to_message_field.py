"""adding size to message field

Revision ID: 4d0899942308
Revises: 415869681065
Create Date: 2024-05-24 23:50:19.633814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '4d0899942308'
down_revision: Union[str, None] = '415869681065'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chats_history', 'message',
               existing_type=mysql.VARCHAR(length=1000),
               type_=sa.String(length=10000),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chats_history', 'message',
               existing_type=sa.String(length=10000),
               type_=mysql.VARCHAR(length=1000),
               existing_nullable=False)
    # ### end Alembic commands ###
