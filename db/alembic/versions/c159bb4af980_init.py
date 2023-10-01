"""init

Revision ID: c159bb4af980
Revises: 
Create Date: 2023-10-01 20:24:22.140145+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c159bb4af980"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hello",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("msg", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "server_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("autoresponse_on", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=6), nullable=False),
        sa.Column("family_friendly", sa.Boolean(), nullable=False),
        sa.Column("sniped", sa.Boolean(), nullable=False),
        sa.Column("block_dms", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "autoresponse",
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("msg", sa.String(), nullable=False),
        sa.Column("response", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["server_id"],
            ["server_settings.id"],
        ),
        sa.PrimaryKeyConstraint("server_id", "msg"),
    )
    op.create_table(
        "snipe",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("msg", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("nsfw", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["user_settings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_server",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("blacklist", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["server_id"],
            ["server_settings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_settings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_server")
    op.drop_table("snipe")
    op.drop_table("autoresponse")
    op.drop_table("user_settings")
    op.drop_table("server_settings")
    op.drop_table("hello")
    # ### end Alembic commands ###