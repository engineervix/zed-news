from tortoise import Tortoise

from app.core.utilities import DATABASE_URL

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL.replace("postgres://", "psycopg://")},
    "apps": {
        "models": {
            "models": [
                "app.core.db.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initializes the database"""
    await Tortoise.init(
        db_url=DATABASE_URL.replace("postgres://", "psycopg://"),
        modules={"models": ["app.core.db.models"]},
    )
    await Tortoise.generate_schemas(safe=True)
