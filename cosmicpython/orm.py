from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import registry, sessionmaker, clear_mappers


from cosmicpython import models

mapper_registry = registry()
metadata = mapper_registry.metadata

def create_mapping(model, table_definition):
    mapper_registry.map_imperatively(model, table_definition)


create_mapping(models.OrderLine, Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
))



create_mapping(models.Batch, Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
))




