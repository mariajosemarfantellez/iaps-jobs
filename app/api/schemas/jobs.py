from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from enum import Enum


class JobStatusEnum(str, Enum):
    DECLARED = 'DECLARED'
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    FINISHED = 'FINISHED'


class JobStatus(BaseModel):
    status: JobStatusEnum
    status_message: Optional[str] = None


class JobOutput(BaseModel):
    output: Dict


class JobTypeEnum(str, Enum):
    COLLABORATIVE_RETRIEVAL = 'COLLABORATIVE_RETRIEVAL'
    COLLABORATIVE_SESSION = 'COLLABORATIVE_SESSION'
    COLLABORATIVE_SPLIT = 'COLLABORATIVE_SPLIT'
    OPTIMIZATION = 'OPTIMIZATION'
    TESTING_GENERIC = 'TESTING_GENERIC'
    CLUSTERING = 'CLUSTERING'
    PREDICTION = 'PREDICTION'
    CLASSIFICATION = 'CLASSIFICATION'

class GenericJob(BaseModel):
    project_uuid: str
    client_uuid: Optional[str]
    application_uuid: Optional[str]
    params: Dict
