from typing import Annotated, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from api.authentication.user import get_current_user
from api.models.adapter import RepositoryMetadataAdapter, RepositoryRequestHandler, RepositoryType
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission, User

router = APIRouter()


@router.post("/dataset/", response_model=DatasetMetadataDOC, status_code=status.HTTP_201_CREATED)
async def create_dataset(document: DatasetMetadataDOC, user: Annotated[User, Depends(get_current_user)]):
    await document.insert()
    submission = document.as_submission()
    await submission.insert()
    user.submissions.append(submission)
    await user.save()
    return document


@router.get("/dataset/{submission_id}", response_model=DatasetMetadataDOC)
async def get_dataset(submission_id: PydanticObjectId, user: Annotated[User, Depends(get_current_user)]):
    submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    document = await DatasetMetadataDOC.get(submission.identifier)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    return document


@router.get("/dataset/", response_model=List[DatasetMetadataDOC])
async def get_datasets(user: Annotated[User, Depends(get_current_user)]):
    documents = [await DatasetMetadataDOC.get(submission.identifier) for submission in user.submissions]
    return documents


@router.put("/dataset/{submission_id}", response_model=DatasetMetadataDOC)
async def update_dataset(
    submission_id: PydanticObjectId,
    updated_document: DatasetMetadataDOC,
    user: Annotated[User, Depends(get_current_user)],
):
    submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    await dataset.set(updated_document.dict(exclude_unset=True, by_alias=True))
    dataset = await DatasetMetadataDOC.get(submission_id)
    await submission.set(dataset.as_submission().dict(exclude_unset=True))
    return dataset


@router.delete("/dataset/{submission_id}", response_model=dict)
async def delete_dataset(submission_id: PydanticObjectId, user: Annotated[User, Depends(get_current_user)]):
    submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    dataset = await DatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    await submission.delete()
    await dataset.delete()
    return {"deleted_dataset_id": submission_id}


@router.get("/submission/", response_model=List[Submission])
async def get_submissions(user: Annotated[User, Depends(get_current_user)]):
    return user.submissions


@router.get("/repository/hydroshare/{identifier}", response_model=DatasetMetadataDOC)
# async def get_hydroshare_resource_metadata(request: Request, identifier: str,
#                                            user: Annotated[User, Depends(get_current_user)]):
async def get_hydroshare_resource_metadata(request: Request, identifier: str):
    # TODO: Add user authentication
    hs_request_handler = RepositoryRequestHandler.get_handler(repository=RepositoryType.HYDROSHARE)
    metadata = await hs_request_handler.get_metadata(identifier)
    hs_adapter = RepositoryMetadataAdapter.get_adapter(repository=RepositoryType.HYDROSHARE)
    catalog_dataset = hs_adapter.to_catalog_record(metadata)
    return catalog_dataset
