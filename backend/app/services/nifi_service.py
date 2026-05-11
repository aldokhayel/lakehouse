"""NiFi REST API client — async httpx, self-signed cert, single-user JWT auth."""

import httpx
from datetime import datetime, timedelta
from typing import Any
from app.config import settings

_TOKEN_TTL_HOURS = 11  # NiFi default token lifetime is 12h; refresh at 11h


class NiFiService:
    def __init__(self) -> None:
        self.base_url = f"https://{settings.nifi_host}:{settings.nifi_port}/nifi-api"
        self._token: str | None = None
        self._token_expiry: datetime | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_token_valid(self) -> bool:
        return (
            self._token is not None
            and self._token_expiry is not None
            and datetime.utcnow() < self._token_expiry
        )

    async def _get_token(self) -> str:
        if self._is_token_valid():
            return self._token  # type: ignore[return-value]
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/access/token",
                content=f"username={settings.nifi_username}&password={settings.nifi_password}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            self._token = resp.text.strip()
            self._token_expiry = datetime.utcnow() + timedelta(hours=_TOKEN_TTL_HOURS)
            return self._token

    async def _client(self) -> dict[str, Any]:
        """Return auth headers for use in a request."""
        token = await self._get_token()
        return {"Authorization": f"Bearer {token}"}

    async def _get(self, path: str) -> dict:
        headers = await self._client()
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.get(f"{self.base_url}{path}", headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def _put(self, path: str, body: dict) -> dict:
        headers = await self._client()
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.put(
                f"{self.base_url}{path}", headers=headers, json=body
            )
            resp.raise_for_status()
            return resp.json()

    async def _post_json(self, path: str, body: dict) -> dict:
        headers = await self._client()
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}{path}", headers=headers, json=body
            )
            resp.raise_for_status()
            return resp.json()

    async def _post_multipart(self, path: str, files: dict) -> dict:
        headers = await self._client()
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}{path}", headers=headers, files=files
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_status(self) -> dict:
        """Return NiFi system diagnostics."""
        return await self._get("/system-diagnostics")

    async def is_healthy(self) -> bool:
        try:
            await self.get_status()
            return True
        except Exception:
            return False

    async def get_root_id(self) -> str:
        """Return the root process group UUID."""
        data = await self._get("/process-groups/root")
        return data["id"]

    async def list_flows(self) -> list[dict]:
        """List top-level process groups (each represents one flow)."""
        root_id = await self.get_root_id()
        data = await self._get(f"/process-groups/{root_id}/process-groups")
        return data.get("processGroups", [])

    async def deploy_flow(self, template_xml: str) -> dict:
        """Upload a template XML and instantiate it in the root process group."""
        root_id = await self.get_root_id()
        # Upload template
        upload_result = await self._post_multipart(
            f"/process-groups/{root_id}/templates/upload",
            files={"template": ("flow.xml", template_xml.encode(), "application/xml")},
        )
        template_id = upload_result["template"]["id"]
        # Instantiate template
        instance = await self._post_json(
            f"/process-groups/{root_id}/template-instance",
            {"templateId": template_id, "originX": 0.0, "originY": 0.0},
        )
        return instance

    async def start_flow(self, process_group_id: str) -> dict:
        """Set all processors in a process group to RUNNING."""
        return await self._put(
            f"/flow/process-groups/{process_group_id}",
            {"id": process_group_id, "state": "RUNNING"},
        )

    async def stop_flow(self, process_group_id: str) -> dict:
        """Set all processors in a process group to STOPPED."""
        return await self._put(
            f"/flow/process-groups/{process_group_id}",
            {"id": process_group_id, "state": "STOPPED"},
        )

    async def get_flow_status(self, process_group_id: str) -> dict:
        """Return status of a specific process group."""
        return await self._get(f"/flow/process-groups/{process_group_id}")

    async def list_templates(self) -> list[dict]:
        """List all uploaded templates."""
        data = await self._get("/templates")
        return data.get("templates", [])


nifi_service = NiFiService()
