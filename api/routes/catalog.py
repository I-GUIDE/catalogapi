from typing import Annotated, List

from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter, Depends, HTTPException, status

from api.adapters.utils import get_adapter_by_type, RepositoryType
from api.authentication.user import get_current_user
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission, User
from pydantic import BaseModel

router = APIRouter()


def inject_repository_identifier(submission: Submission, document: DatasetMetadataDOC):
    if submission.repository_identifier:
        document.repository_identifier = submission.repository_identifier
    return document


@router.post("/dataset/", response_model=DatasetMetadataDOC, status_code=status.HTTP_201_CREATED)
async def create_dataset(document: DatasetMetadataDOC, user: Annotated[User, Depends(get_current_user)]):
    await document.insert()
    submission = document.as_submission()
    user.submissions.append(submission)
    await user.save(link_rule=WriteRules.WRITE)
    return document


@router.get("/dataset/{submission_id}", response_model=DatasetMetadataDOC, response_model_exclude_none=True)
async def get_dataset(submission_id: PydanticObjectId):
    submission: Submission = await Submission.find_one(Submission.identifier == submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    document: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    document = inject_repository_identifier(submission, document)
    return document


@router.get("/dataset/", response_model=List[DatasetMetadataDOC], response_model_exclude_none=True)
async def get_datasets(user: Annotated[User, Depends(get_current_user)]):
    documents = [inject_repository_identifier(submission, await DatasetMetadataDOC.get(submission.identifier)) for
                 submission in user.submissions]
    return documents


@router.put("/dataset/{submission_id}", response_model=DatasetMetadataDOC)
async def update_dataset(
    submission_id: PydanticObjectId,
    updated_document: DatasetMetadataDOC,
    user: Annotated[User, Depends(get_current_user)],
):
    submission: Submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    updated_document.id = dataset.id
    await updated_document.replace()
    dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission_id)
    updated_submission: Submission = dataset.as_submission()
    updated_submission.id = submission.id
    updated_submission.repository_identifier = submission.repository_identifier
    updated_submission.repository = submission.repository
    updated_submission.submitted = submission.submitted
    await updated_submission.replace()
    dataset = inject_repository_identifier(updated_submission, dataset)
    return dataset


@router.delete("/dataset/{submission_id}", response_model=dict)
async def delete_dataset(submission_id: PydanticObjectId, user: Annotated[User, Depends(get_current_user)]):
    submission: Submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    user.submissions.remove(submission)
    await user.save(link_rule=WriteRules.WRITE)
    await submission.delete()
    await dataset.delete()
    return {"deleted_dataset_id": submission_id}


@router.get("/submission/", response_model=List[Submission])
async def get_submissions(user: Annotated[User, Depends(get_current_user)]):
    return user.submissions


@router.get("/repository/hydroshare/{identifier}", response_model=DatasetMetadataDOC)
async def register_hydroshare_resource_metadata(identifier: str, user: Annotated[User, Depends(get_current_user)]):
    # check that the user has not already registered this resource
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.HYDROSHARE, identifier=identifier)
    if submission is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This resource has already been submitted by this user",
        )
    dataset: DatasetMetadataDOC = await _save_to_db(repository_type=RepositoryType.HYDROSHARE,
                                                    identifier=identifier, user=user)
    return dataset


@router.put("/repository/hydroshare/{identifier}", response_model=DatasetMetadataDOC)
async def refresh_dataset_from_hydroshare(identifier: str, user: Annotated[User, Depends(get_current_user)]):
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.HYDROSHARE, identifier=identifier)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")

    dataset = await _save_to_db(repository_type=RepositoryType.HYDROSHARE, identifier=identifier,
                                user=user, submission=submission)
    return dataset


class S3Path(BaseModel):
    path: str
    bucket: str
    endpoint_url: str = 'https://api.minio.cuahsi.io'


@router.put("/repository/s3", response_model=DatasetMetadataDOC)
async def register_s3_dataset(request_model: S3Path, user: Annotated[User, Depends(get_current_user)]):
    path = request_model.path
    bucket = request_model.bucket
    endpoint_url = request_model.endpoint_url
    identifier = f"{endpoint_url}+{bucket}+{path}"
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.S3, identifier=identifier)
    dataset = await _save_to_db(repository_type=RepositoryType.S3, identifier=identifier, user=user, submission=submission)
    return dataset


async def _save_to_db(repository_type: RepositoryType, identifier: str, user: User, submission: Submission = None):
    adapter = get_adapter_by_type(repository_type=repository_type)
    # fetch metadata from repository as catalog dataset
    repo_dataset: DatasetMetadataDOC = await _get_repo_meta_as_catalog_record(adapter=adapter, identifier=identifier)
    if submission is None:
        # new registration
        await repo_dataset.insert()
        submission = repo_dataset.as_submission()
        submission = adapter.update_submission(submission=submission, repo_record_id=identifier)
        user.submissions.append(submission)
        await user.save(link_rule=WriteRules.WRITE)
        dataset = repo_dataset
    else:
        # update existing registration
        dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
        repo_dataset.id = dataset.id
        await repo_dataset.replace()
        updated_dataset: DatasetMetadataDOC = await DatasetMetadataDOC.get(submission.identifier)
        updated_submission: Submission = updated_dataset.as_submission()
        updated_submission = adapter.update_submission(submission=updated_submission, repo_record_id=identifier)
        updated_submission.id = submission.id
        updated_submission.submitted = submission.submitted
        await updated_submission.replace()
        dataset = updated_dataset
        submission = updated_submission

    dataset = inject_repository_identifier(submission, dataset)
    return dataset


async def _get_repo_meta_as_catalog_record(adapter, identifier: str):
    metadata = await adapter.get_metadata(identifier)
    catalog_dataset: DatasetMetadataDOC = adapter.to_catalog_record(metadata)
    return catalog_dataset
