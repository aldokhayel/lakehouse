"""Subprocess wrapper for the dbt CLI."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from app.config import settings


class DbtService:
    """Runs dbt CLI commands as subprocesses and parses their output."""

    def _run(self, *args: str, timeout: int = 300) -> dict:
        """Execute a dbt sub-command and capture stdout/stderr."""
        cmd = [
            "dbt",
            *args,
            "--project-dir",
            settings.dbt_project_dir,
            "--profiles-dir",
            settings.dbt_project_dir,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def run_models(self, select: Optional[str] = None) -> dict:
        """Run dbt models, optionally filtered by a node selector."""
        args = ["run"]
        if select:
            args += ["--select", select]
        return self._run(*args)

    def run_tests(self, select: Optional[str] = None) -> dict:
        """Run dbt tests, optionally filtered by a node selector."""
        args = ["test"]
        if select:
            args += ["--select", select]
        return self._run(*args)

    def list_models(self) -> list[dict]:
        """Return a list of dbt models as dicts (JSON output from dbt ls)."""
        result = self._run("ls", "--output", "json")
        if not result["success"]:
            return []
        models = []
        for line in result["stdout"].strip().splitlines():
            line = line.strip()
            if line:
                try:
                    models.append(json.loads(line))
                except json.JSONDecodeError:
                    models.append({"name": line})
        return models

    def get_run_results(self) -> dict:
        """Load and return the most recent dbt run_results.json artifact."""
        path = Path(settings.dbt_project_dir) / "target" / "run_results.json"
        if not path.exists():
            return {"results": [], "message": "No run results yet. Run dbt first."}
        with open(path) as f:
            return json.load(f)

    def is_available(self) -> bool:
        """Return True if the dbt CLI is installed and reachable."""
        result = subprocess.run(["dbt", "--version"], capture_output=True, text=True)
        return result.returncode == 0


dbt_service = DbtService()
