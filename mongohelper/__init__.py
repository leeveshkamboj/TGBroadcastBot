import logging
from umongo import Instance
from motor.motor_asyncio import AsyncIOMotorClient
import os

DATABASE_URI = os.environ.get("DATABASE_URL", None)
DATABASE_NAME = os.environ.get("DATABASE_NAME", "broadcast")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
database = client[DATABASE_NAME]
instance = Instance.from_db(database)