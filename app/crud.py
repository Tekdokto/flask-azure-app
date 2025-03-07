import asyncio
from . import db, redis_client
from .utils import logger

async def get_from_cache(cache_key):
    """Retrieve an item from Redis cache asynchronously."""
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit: {cache_key}")
            return eval(cached_data)  # Convert string to dictionary
        logger.info(f"Cache miss: {cache_key}")
        return None
    except Exception as e:
        logger.error(f"Redis GET error for key {cache_key}: {e}")
        return None

async def set_to_cache(cache_key, data, expiration=300):
    """Store an item in Redis cache asynchronously."""
    try:
        redis_client.setex(cache_key, expiration, str(data))
        logger.info(f"Cache set: {cache_key} (expires in {expiration}s)")
    except Exception as e:
        logger.error(f"Redis SET error for key {cache_key}: {e}")

async def delete_from_cache(cache_key):
    """Remove an item from Redis cache asynchronously."""
    try:
        redis_client.delete(cache_key)
        logger.info(f"Cache deleted: {cache_key}")
    except Exception as e:
        logger.error(f"Redis DELETE error for key {cache_key}: {e}")

async def get_by_id(model, id):
    """Retrieve a database record by ID with caching."""
    cache_key = f"{model.__name__.lower()}_{id}"
    
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    try:
        record = await asyncio.to_thread(model.query.get, id)  # Non-blocking DB call
        if record:
            record_dict = record.to_dict()
            await set_to_cache(cache_key, record_dict)
            return record_dict
    except Exception as e:
        logger.error(f"Database GET error for {model.__name__} ID {id}: {e}")

    return None

async def get_all(model):
    """Retrieve all records from the database with caching."""
    cache_key = f"all_{model.__name__.lower()}s"
    
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    try:
        records = await asyncio.to_thread(model.query.all)
        records_list = [record.to_dict() for record in records]
        await set_to_cache(cache_key, records_list, expiration=60)  # Cache for 60 seconds
        return records_list
    except Exception as e:
        logger.error(f"Database GET error for all {model.__name__} records: {e}")

    return []

async def create_record(model, data):
    """Create and save a new record to the database."""
    try:
        new_record = model(**data)
        db.session.add(new_record)
        db.session.commit()
        logger.info(f"Created new {model.__name__} record: {new_record.id}")
        return new_record.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database CREATE error for {model.__name__}: {e}")
        return None

async def update_record(model, id, data):
    """Update an existing database record."""
    try:
        record = await asyncio.to_thread(model.query.get, id)
        if not record:
            return None

        for key, value in data.items():
            setattr(record, key, value)

        db.session.commit()
        cache_key = f"{model.__name__.lower()}_{id}"
        await set_to_cache(cache_key, record.to_dict())
        logger.info(f"Updated {model.__name__} ID {id}")
        return record.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database UPDATE error for {model.__name__} ID {id}: {e}")
        return None

async def delete_record(model, id):
    """Delete a record from the database and remove from cache."""
    try:
        record = await asyncio.to_thread(model.query.get, id)
        if not record:
            return None

        db.session.delete(record)
        db.session.commit()
        cache_key = f"{model.__name__.lower()}_{id}"
        await delete_from_cache(cache_key)
        logger.info(f"Deleted {model.__name__} ID {id}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database DELETE error for {model.__name__} ID {id}: {e}")
        return None
