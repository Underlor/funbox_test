import aioredis


async def init_redis(app):
    app["redis"] = await aioredis.create_redis_pool(app["config"].REDIS_URL)
    yield
    if app["config"].FLUSH_DB:
        await app["redis"].flushdb()
    app["redis"].close()
    await app["redis"].wait_closed()
