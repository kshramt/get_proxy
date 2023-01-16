import httpx
import pytest

import src.apps as target


@pytest.mark.asyncio
async def test__users__user_id__data__id() -> None:
    async with httpx.AsyncClient(app=target.app, base_url="http://test") as client:
        resp = await client.get("/admin/health")
        assert resp.status_code == 204
