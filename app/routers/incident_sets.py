from fastapi import APIRouter, HTTPException, Depends, Request


from app import crud
from app.s3 import S3Client
from app.models import IncidentList, IncidentSet

from app.auth import verify_user
from app.index import Index


async def verify_creator(request: Request, incident_set_id: str):
    creator = Index.get_creator(incident_set_id)
    if creator != request.session["user"]["login"]:
        raise HTTPException(status_code=403, detail="Not your incident set")


router = APIRouter()


@router.get("/sets/{incident_set_id}")
def api_get_incident_set(incident_set_id: str):
    try:
        return crud.get_incident_set(S3Client, incident_set_id).incidents
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc


@router.put("/sets", status_code=201, dependencies=[Depends(verify_user)])
def api_put_incident_set(request: Request, incident_list: IncidentList):
    incident_set = IncidentSet(
        incidents=incident_list, creator=request.session["user"]["login"]
    )
    crud.put_incident_set(S3Client, incident_set)
    return incident_set


@router.post(
    "/sets/{incident_set_id}",
    status_code=200,
    dependencies=[Depends(verify_user), Depends(verify_creator)],
)
def api_update_incident_set(incident_set_id: str, incident_list: IncidentList):
    try:
        original_incident_set = crud.get_incident_set(
            S3Client,
            incident_set_id,
        )
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc

    original_incident_set.incidents = incident_list
    try:
        crud.put_incident_set(S3Client, original_incident_set)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return original_incident_set


@router.delete(
    "/sets/{incident_set_id}",
    dependencies=[Depends(verify_user), Depends(verify_creator)],
)
def api_delete_incident_set(incident_set_id: str):
    try:
        crud.delete_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return {"status": "ok"}
