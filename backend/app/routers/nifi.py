"""NiFi integration endpoints — full Phase 3 implementation."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nifi_service import nifi_service

router = APIRouter(prefix="/nifi", tags=["nifi"])

# Built-in template name → filename mapping (files live in the NiFi container)
_BUILTIN_TEMPLATES_DIR = Path("/opt/nifi-templates")
_BUILTIN_TEMPLATE_NAMES = {
    "api-to-minio",
    "postgres-to-minio",
    "mssql-to-minio",
    "mongodb-to-minio",
}


def _ok(data=None, message: str = "OK") -> dict:
    return {"status": "success", "data": data, "message": message}


def _err(message: str, data=None) -> dict:
    return {"status": "error", "data": data, "message": message}


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class DeployFlowRequest(BaseModel):
    """Body for POST /api/nifi/flows.

    Supply exactly one of:
    - template_xml: raw NiFi template XML string
    - template_name: one of the built-in template names (e.g. "api-to-minio")
    """

    template_xml: Optional[str] = None
    template_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/status")
async def get_nifi_status():
    """Return NiFi system diagnostics."""
    try:
        data = await nifi_service.get_status()
        return _ok(data=data, message="NiFi is reachable")
    except Exception as exc:
        return _err(f"NiFi unreachable: {exc}")


@router.get("/flows")
async def list_flows():
    """List all top-level process groups (flows) in NiFi."""
    try:
        flows = await nifi_service.list_flows()
        return _ok(data=flows, message=f"{len(flows)} flow(s) found")
    except Exception as exc:
        return _err(f"Failed to list flows: {exc}")


@router.post("/flows")
async def deploy_flow(body: DeployFlowRequest):
    """Deploy a new flow from raw XML or a built-in template name.

    Body (JSON):
        { "template_xml": "<xml>..." }          # raw XML
        { "template_name": "api-to-minio" }     # built-in template
    """
    try:
        # Resolve the XML source
        if body.template_xml:
            xml_content = body.template_xml
        elif body.template_name:
            name = body.template_name
            if name not in _BUILTIN_TEMPLATE_NAMES:
                return _err(
                    f"Unknown template_name '{name}'. "
                    f"Valid options: {sorted(_BUILTIN_TEMPLATE_NAMES)}"
                )
            template_path = _BUILTIN_TEMPLATES_DIR / f"{name}.xml"
            if not template_path.exists():
                return _err(
                    f"Template file not found in container: {template_path}. "
                    "Ensure the NiFi image was built with the flow-templates/ directory."
                )
            xml_content = template_path.read_text()
        else:
            return _err(
                "Provide either 'template_xml' (raw XML) or 'template_name' (built-in template)."
            )

        result = await nifi_service.deploy_flow(xml_content)
        return _ok(data=result, message="Flow deployed and instantiated successfully")
    except Exception as exc:
        return _err(f"Failed to deploy flow: {exc}")


@router.post("/flows/{flow_id}/start")
async def start_flow(flow_id: str):
    """Start all processors in a process group."""
    try:
        result = await nifi_service.start_flow(flow_id)
        return _ok(data=result, message=f"Flow {flow_id} started")
    except Exception as exc:
        return _err(f"Failed to start flow {flow_id}: {exc}")


@router.post("/flows/{flow_id}/stop")
async def stop_flow(flow_id: str):
    """Stop all processors in a process group."""
    try:
        result = await nifi_service.stop_flow(flow_id)
        return _ok(data=result, message=f"Flow {flow_id} stopped")
    except Exception as exc:
        return _err(f"Failed to stop flow {flow_id}: {exc}")


@router.get("/flows/{flow_id}/status")
async def get_flow_status(flow_id: str):
    """Return the current status of a specific process group."""
    try:
        result = await nifi_service.get_flow_status(flow_id)
        return _ok(data=result, message=f"Status for flow {flow_id}")
    except Exception as exc:
        return _err(f"Failed to get status for flow {flow_id}: {exc}")


@router.get("/templates")
async def list_templates():
    """List all templates uploaded to NiFi."""
    try:
        templates = await nifi_service.list_templates()
        return _ok(data=templates, message=f"{len(templates)} template(s) found")
    except Exception as exc:
        return _err(f"Failed to list templates: {exc}")
