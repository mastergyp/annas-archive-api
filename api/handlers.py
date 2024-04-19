import logging
import threading
from dataclasses import asdict
from http import HTTPStatus

from sanic import ServerError
from sanic.request import Request
from sanic.response import json
from seleniumbase import get_driver

from . import extractors
from .middlewares.caching import cache
from .middlewares.querycheck import query_checker
from .models import args


@cache
async def recents(_):
    try:
        recent_downloads = await extractors.recents.get_recent_downloads()
    except Exception as err:
        logging.error("loading recents", err)
        return json(
            body={"error": "failed to load recent downloads"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    response = json([asdict(r) for r in recent_downloads])
    return response


@query_checker(["q"])
@cache
async def search(request: Request, q: str):
    try:
        language = args.Language(request.args.get("lang", ""))
    except ValueError:
        return json({"error": "invalid language code"}, HTTPStatus.BAD_REQUEST)
    try:
        extension = args.FileType(request.args.get("ext", ""))
    except ValueError:
        return json({"error": "invalid file extension"}, HTTPStatus.BAD_REQUEST)
    try:
        order_by = args.OrderBy(request.args.get("sort", ""))
    except ValueError:
        return json({"error": "invalid sort mode"}, HTTPStatus.BAD_REQUEST)
    try:
        result = await extractors.search.get_search_results(
            query=q,
            language=language,
            file_type=extension,
            order_by=order_by,
        )
    except Exception as err:
        logging.error("searching", err)
        return json(
            body={"error": "failed to load search results"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    response = json([asdict(r) for r in result])
    return response


@query_checker(["id"])
@cache
async def download(_, id: str):
    try:
        download_data = await extractors.download.get_download(id)
    except Exception as err:
        logging.error("loading download information", err)
        return json(
            body={"error": "failed to load download data"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return json(asdict(download_data))


@query_checker(["url"])
@cache
async def bypass(_, url: str):
    try:
        driver = get_driver("chrome", headless=True, undetectable=True)

        # Run fix_cf_just_moment in a separate thread
        thread = threading.Thread(target=extractors.auto.fix_cf_just_moment, args=(url, driver))
        thread.start()
        thread.join()  # Wait for the thread to finish

        xpath = "/html/body/main/p[2]/a"
        element = driver.find_element(by="xpath", value=xpath)  # 使用 XPath 查找元素
        data = {"url": element.get_attribute("href")}
        driver.quit()
        return json(data)
    except Exception as e:
        logging.error(f"Error in bypass function: {e}")
        raise ServerError("An error occurred while processing your request.")