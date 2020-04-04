from aiohttp import web

from views import VisitedDomains, VisitedLinks


urls = [web.view("/visited_links", VisitedLinks), web.view("/visited_domains", VisitedDomains)]
