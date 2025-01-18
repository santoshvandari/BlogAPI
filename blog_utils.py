import random
from slugify import slugify
from motor.motor_asyncio import AsyncIOMotorDatabase


def rand_random_string():
    return str(random.randint(100000,999999))

async def slug_genertor(title:str,db:AsyncIOMotorDatabase):
    slug = slugify(title)
    if await db["blogs"].find_one({"slug":slug}):
        slug = slug + " " + rand_random_string()
        slug = slugify(slug)
    return slug