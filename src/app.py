from aiohttp import web

from config import CONFIG
from urls import urls
from utils import init_redis


def create_app():
    app = web.Application()
    app.add_routes(urls)
    app["config"] = CONFIG()
    app.cleanup_ctx.append(init_redis)
    return app


if __name__ == "__main__":
    application = create_app()
    web.run_app(application, port=application["config"].LISTEN_PORT)
