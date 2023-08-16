from fastapi import APIRouter, HTTPException


from app import crud
from app.s3 import S3Client
from app.models import IncidentList, IncidentSet

import nanoid

router = APIRouter()


@router.get("/sets/{incident_set_id}")
def api_get_incident_set(incident_set_id: str):
    try:
        return crud.get_incident_set(S3Client, incident_set_id).incidents
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc


@router.post("/sets", status_code=201)
def api_post_incident_set(incident_list: IncidentList):
    incident_set = IncidentSet(
        id=nanoid.generate(alphabet="0123456789abcdef", size=8), incidents=incident_list
    )
    crud.put_incident_set(S3Client, incident_set)
    return incident_set
