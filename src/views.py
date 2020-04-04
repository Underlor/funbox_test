import re
from time import time

from aiohttp import web


class VisitedLinks(web.View):
    async def post(self):
        data = await self.request.json()
        if "links" not in data:
            return web.json_response({"status": 'Bad data format. "links" list not found in request'}, status=400)

        links = data.get("links")
        if not isinstance(links, list):
            return web.json_response({"status": 'Bad data format. "links" must be list'}, status=400)

        redis = self.request.app["redis"]
        domain_re = re.compile(r"^(?:https?://)?(?:[^@/\n]+@)?(?:www\.)?([^:/?\n]+)")

        errors = []
        for link in links:
            ts = time()

            domain = domain_re.match(link)
            if domain:
                await redis.zadd("links", ts, f"{domain.group(1)}|{ts}")
            else:
                errors.append(f'Item "{link}" could not recognised')
        return web.json_response({"status": "ok", "errors": errors, "now": time()})


class VisitedDomains(web.View):
    async def get(self):
        try:
            from_dt = float(self.request.rel_url.query.get("from"))
        except (ValueError, TypeError):
            return web.json_response(
                {
                    "status": 'Bad request. Param "from" must be int or float',
                    "params": dict(self.request.rel_url.query),
                },
                status=400,
            )

        try:
            to_dt = float(self.request.rel_url.query.get("to"))
        except (ValueError, TypeError):
            return web.json_response(
                {
                    "status": 'Bad request. Param "to" must be int or float',
                    "params": dict(self.request.rel_url.query),
                },
                status=400,
            )

        redis = self.request.app["redis"]
        result = await redis.zrangebyscore("links", from_dt, to_dt, encoding="utf-8")
        unique_result = set([item.split("|")[0] for item in result])
        return web.json_response({"status": "ok", "domains": list(unique_result)})
