"""Pipeline orchestration — triggers NiFi ingestion then dbt transformation."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pipeline import Pipeline, PipelineRun
from app.services.dbt_service import dbt_service
from app.services.nifi_service import nifi_service


class PipelineService:
    async def run_pipeline(self, pipeline_id: str, db: AsyncSession) -> dict:
        """
        Execute a pipeline:
        1. Load pipeline definition from DB
        2. If definition has a nifi_flow_id, start the NiFi flow
        3. Run dbt (always)
        4. Update pipeline run status

        Returns a run_id immediately; execution is tracked in the DB.
        """
        # Load pipeline
        result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
        pipeline = result.scalar_one_or_none()
        if pipeline is None:
            return {"status": "error", "message": f"Pipeline {pipeline_id} not found"}

        # Create run record
        run = PipelineRun(
            id=str(uuid.uuid4()),
            pipeline_id=pipeline_id,
            status="running",
            logs="Pipeline run started.\n",
            started_at=datetime.utcnow(),
        )
        db.add(run)
        await db.commit()

        # Mark pipeline as running
        await db.execute(
            update(Pipeline).where(Pipeline.id == pipeline_id).values(status="running")
        )
        await db.commit()

        # Kick off background execution (fire and forget)
        asyncio.create_task(self._execute(pipeline, run, db))

        return {
            "status": "success",
            "run_id": run.id,
            "message": "Pipeline execution started",
        }

    async def _execute(
        self, pipeline: Pipeline, run: PipelineRun, db: AsyncSession
    ) -> None:
        logs: list[str] = []
        try:
            definition = (
                json.loads(pipeline.definition)
                if isinstance(pipeline.definition, str)
                else pipeline.definition
            )
            nifi_flow_id: Optional[str] = definition.get("nifi_flow_id")

            # ------------------------------------------------------------------
            # Step 1: NiFi ingestion (optional)
            # ------------------------------------------------------------------
            if nifi_flow_id:
                logs.append("Starting NiFi flow...")
                try:
                    await nifi_service.start_flow(nifi_flow_id)
                    logs.append(f"NiFi flow {nifi_flow_id} started.")
                    # Wait briefly then stop (batch mode — one-shot ingestion)
                    await asyncio.sleep(30)
                    await nifi_service.stop_flow(nifi_flow_id)
                    logs.append("NiFi flow stopped.")
                except Exception as exc:
                    logs.append(f"NiFi error (continuing): {exc}")
            else:
                logs.append(
                    "No nifi_flow_id in pipeline definition — skipping NiFi step."
                )

            # ------------------------------------------------------------------
            # Step 2: dbt transformation
            # ------------------------------------------------------------------
            logs.append("Running dbt...")
            dbt_select: Optional[str] = definition.get("dbt_select")
            dbt_result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: dbt_service.run_models(dbt_select)
            )
            if dbt_result["success"]:
                logs.append("dbt run completed.")
            else:
                logs.append(f"dbt run failed: {dbt_result['stderr'][:500]}")

            final_status = "success" if dbt_result["success"] else "error"

        except Exception as exc:
            logs.append(f"Pipeline error: {exc}")
            final_status = "error"

        # ------------------------------------------------------------------
        # Persist final state
        # ------------------------------------------------------------------
        run.status = final_status
        run.logs = "\n".join(logs)
        run.finished_at = datetime.utcnow()
        db.add(run)

        from sqlalchemy import update as sa_update
        from app.models.pipeline import Pipeline as PipelineModel

        await db.execute(
            sa_update(PipelineModel)
            .where(PipelineModel.id == pipeline.id)
            .values(status=final_status)
        )
        await db.commit()


pipeline_service = PipelineService()
