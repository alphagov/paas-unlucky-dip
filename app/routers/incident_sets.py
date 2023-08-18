from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.auth import RequestWithUser, verify_user
from app.index import Index
from app.models import UUID4, IncidentSet, IncidentSetUpdateBody
from app.s3 import S3Client


async def verify_creator(request: RequestWithUser, incident_set_id: UUID4):
    creator = Index.get_creator(incident_set_id)
    if creator != request.state.user.login:
        raise HTTPException(status_code=403, detail="Not your incident set")


router = APIRouter()


@router.get("/sets/{incident_set_id}")
def api_get_incident_set(incident_set_id: UUID4):
    try:
        return crud.get_incident_set(S3Client, incident_set_id).incidents
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc


@router.put("/sets", status_code=201, dependencies=[Depends(verify_user)])
def api_put_incident_set(request: RequestWithUser, data: IncidentSetUpdateBody):
    incident_set = IncidentSet(
        incidents=data.incidents,
        creator=request.state.user.login,
        name=data.name,
    )
    crud.put_incident_set(S3Client, incident_set)
    return incident_set


@router.post(
    "/sets/{incident_set_id}",
    status_code=200,
    dependencies=[Depends(verify_user), Depends(verify_creator)],
)
def api_update_incident_set(incident_set_id: UUID4, data: IncidentSetUpdateBody):
    try:
        original_incident_set = crud.get_incident_set(
            S3Client,
            incident_set_id,
        )
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc

    original_incident_set.incidents = data.incidents
    original_incident_set.name = data.name
    try:
        crud.put_incident_set(S3Client, original_incident_set)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return original_incident_set


@router.delete(
    "/sets/{incident_set_id}",
    dependencies=[Depends(verify_user), Depends(verify_creator)],
)
def api_delete_incident_set(incident_set_id: UUID4):
    try:
        crud.delete_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return {"status": "ok"}
