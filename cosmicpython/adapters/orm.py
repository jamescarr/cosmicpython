from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import clear_mappers, registry, relationship, sessionmaker

from cosmicpython.domain import models

mapper_registry = registry()
metadata = mapper_registry.metadata


def create_mapping(model, table_definition, **kwargs):
    mapper_registry.map_imperatively(model, table_definition, **kwargs)


order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255), ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255), unique=True, index=True),
)
allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    create_mapping(models.OrderLine, order_lines)
    create_mapping(
        models.Batch,
        batches,
        properties={
            "_allocations": relationship(
                models.OrderLine,
                backref="batch",
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    create_mapping(
        models.Product,
        products,
        properties={
            # Relationship to all the batches that have this product's SKU
            "batches": relationship(models.Batch, backref="product")
        },
    )
