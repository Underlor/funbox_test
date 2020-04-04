from time import time
from urllib.parse import urlencode

import pytest

from app import create_app


@pytest.fixture
def cli(loop, aiohttp_client):
    app = create_app()
    return loop.run_until_complete(aiohttp_client(app))


@pytest.mark.parametrize(
    "links,result",
    [
        [("ya.ru", "yandex.ru", "funbox.ru"), ("ya.ru", "yandex.ru", "funbox.ru")],
        [("ya.ru",), ("ya.ru",)],
        [("ya.ru", "///awd/awd/"), ("ya.ru",)],
        [("ya.ru", "https://ya.ru", 'https://ya.ru?q=123"'), ("ya.ru",)],
    ],
)
async def test_add_domains(cli, links, result):
    resp = await cli.post("/visited_links", json={"links": links})
    assert resp.status == 200

    response = await resp.json()
    assert response["status"] == "ok"

    items = await cli.app["redis"].zrange("links", encoding="utf-8")
    for item in items:
        assert item.split("|")[0] in result


async def test_add_domains_empty_json(cli):
    resp = await cli.post("/visited_links", json={})
    assert resp.status == 400


async def test_add_domains_links_not_list(cli):
    resp = await cli.post("/visited_links", json={"links": "123123"})
    assert resp.status == 400


@pytest.mark.parametrize(
    "links,result", [[(), []], [("ya.ru", "yandex.ru", "funbox.ru"), ["ya.ru", "yandex.ru", "funbox.ru"]]]
)
async def test_visited_domains(cli, links, result):
    for link in links:
        ts = time()
        await cli.app["redis"].zadd("links", ts, f"{link}|{ts}")

    url = f"/visited_domains?{urlencode({'from': '-inf', 'to': 'inf'})}"
    resp = await cli.get(url)
    assert resp.status == 200

    response = await resp.json()
    assert response["status"] == "ok"
    for domain in response["domains"]:
        assert domain in result


@pytest.mark.parametrize(
    "request_params", [{}, {"from": 123}, {"to": 123}, {"from": 123, "to": "dwad"}, {"from": "cawd", "to": 123}]
)
async def test_visited_domains_bad_params(cli, request_params):
    url = f"/visited_domains?{urlencode(request_params)}"
    resp = await cli.get(url)
    assert resp.status == 400
