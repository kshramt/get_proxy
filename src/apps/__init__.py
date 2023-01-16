import asyncio
import gzip
import json
import traceback
from typing import Final, TypedDict

import fastapi
import starlette

from .. import browsers

app: Final = fastapi.FastAPI()


class SuccessDict(TypedDict):
    source: str
    error: None


class ErrorDict(TypedDict):
    source: None
    error: str


@app.get("/")
async def get_index(uri: str) -> fastapi.Response:
    result = await get_content(uri)
    b = gzip.compress(json.dumps(result, ensure_ascii=False).encode())
    return fastapi.Response(content=b, media_type="application/octet-stream")


async def get_content(uri: str) -> SuccessDict | ErrorDict:
    async with browsers.get_page() as page:
        try:
            await page.goto(uri)
            content = await page.content()
            return SuccessDict(source=content, error=None)
        except asyncio.CancelledError:
            raise
        except Exception:
            return ErrorDict(source=None, error=traceback.format_exc())


@app.get("/admin/health", status_code=starlette.status.HTTP_204_NO_CONTENT)
async def get_admin_health() -> fastapi.Response:
    return fastapi.Response(status_code=starlette.status.HTTP_204_NO_CONTENT)
