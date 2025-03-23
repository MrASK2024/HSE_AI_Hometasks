from sqlalchemy import Table, Column, Integer, DateTime, MetaData, String
metadata = MetaData()

shorten_links = Table(
    "shorten_links",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String, unique=True, nullable=False),
    Column("short_link", String, unique=True, nullable=False),
    Column("creation_date", DateTime, nullable=False),
    Column("last_use_date", DateTime),
    Column("expires_at", DateTime),
    Column("user_id", String, nullable=True),
)