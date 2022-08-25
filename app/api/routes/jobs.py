from email import message
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from ..utils.airflow import airflow_dag_trigger
from ..utils.jobs import job_formatted
from ..models.jobs import Job, Job_Type

from ..auth.main import validate_token, UserSession
from ..schemas.jobs import GenericJob
from ..schemas.jobs import JobTypeEnum, JobStatus, JobOutput
from ..database.conf import db
from typing import Optional
from jsonschema import SchemaError, ValidationError, validate

router = APIRouter()


@router.get("/{job_uuid}", response_description="Update Session")
async def get_job_details(job_uuid: uuid.UUID,
                          current_user: UserSession = Depends(validate_token),
                          database=Depends(db)):
    if (job := database.query(Job).filter(
            Job.uuid == job_uuid).first()) is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    return job_formatted(job)


@router.get("/project/{project_uuid}", response_description="Get collaborative jobs")
async def get_project_jobs(project_uuid: uuid.UUID,
                           job_type_details: Optional[JobTypeEnum] = None,
                           current_user: UserSession = Depends(validate_token),
                           database=Depends(db)):
    # TODO: agregar paginacion
    result = []
    data = None
    filters = [Job.project_uuid == project_uuid]
    if job_type_details is not None:
        filters.append(Job.type == job_type_details.value)

    if project_uuid:
        data = database.query(Job).filter(*filters).order_by(Job.id.desc())

    if data.first() is None:
        raise HTTPException(status_code=404, detail="Not found")

    for job in data:
        result.append(job_formatted(job))
    return result


@router.post("/{job_type}", response_description="Triggers a generic job")
async def create_generic_job(body: GenericJob,
                             job_type: JobTypeEnum,
                             current_user: UserSession = Depends(
                                 validate_token),
                             database=Depends(db)):
    # Validate Job params
    job_type_details = database.query(Job_Type).filter(
        Job_Type.name == job_type).first()

    if job_type_details is None:
        raise HTTPException(status_code=404, detail="Job Type Not Found")

    try:
        validate(body.params, job_type_details.params_schema)
    except ValidationError as error:
        raise HTTPException(
            status_code=400, detail=f"Params Schema Validation Error: {error}"
        )
    except SchemaError as error:
        raise HTTPException(
            status_code=400, detail=f"Schema Error: {error}"
        )

    default_params = job_type_details.default_params if job_type_details.default_params else {}
    # Create Job
    new_job = Job(
        type=job_type,
        project_uuid=body.project_uuid,
        client_uuid=body.client_uuid,
        application_uuid=body.application_uuid,
        params={**default_params, **body.params}
    )
    database.add(new_job)
    database.commit()

    # Launch airflow dag
    airflow_response = airflow_dag_trigger(
        job_type_details.dag_name, {'job': str(new_job.uuid)})
    return job_formatted(new_job)


@router.patch('/{job_uuid}/status')
async def set_job_status(job_uuid: uuid.UUID,
                         status_update: JobStatus,
                         current_user: UserSession = Depends(validate_token),
                         database=Depends(db)):
    job = database.query(Job).filter(Job.uuid == job_uuid)

    if job.first() is None:
        raise HTTPException(status_code=404, detail="Not found")

    job.update({'status': status_update.status.value,
                'status_message': status_update.status_message})
    database.commit()

    return job_formatted(job.first())


@router.patch('/{job_uuid}/output')
async def join_output(job_uuid: uuid.UUID,
                      body: JobOutput,
                      current_user: UserSession = Depends(validate_token),
                      database=Depends(db)):
    job = database.query(Job).filter(Job.uuid == job_uuid)

    if job.first() is None:
        raise HTTPException(status_code=404, detail="Not found")

    original_output = job.first().output
    if original_output is None:
        original_output = {}

    job.update(
        {'output': {**original_output, **body.output}})
    database.commit()

    return job_formatted(job.first())
