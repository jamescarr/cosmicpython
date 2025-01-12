from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import registry, sessionmaker, clear_mappers, relationship


from cosmicpython import models

mapper_registry = registry()
metadata = mapper_registry.metadata

def create_mapping(model, table_definition, **kwargs):
    mapper_registry.map_imperatively(
        model,
        table_definition,
        **kwargs)


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
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

def start_mappers():
    lines_mapper = create_mapping(models.OrderLine, order_lines)
    create_mapping(
        models.Batch,
        batches,
        properties={
            "_allocations": relationship(
                models.OrderLine, backref="batch", secondary=allocations, collection_class=set,
            )
        },
    )


