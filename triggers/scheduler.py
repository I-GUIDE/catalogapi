import asyncio
import logging
from asyncio import run as aiorun

import typer
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.adapters.utils import RepositoryType, get_adapter_by_type
from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission

logger = logging.getLogger()


async def retrieve_repository_record(submission: Submission):
    """Retrieve the repository record from the repository and return it as a Catalog Record"""
    if submission.repository in RepositoryType.__members__:
        adapter = get_adapter_by_type(RepositoryType[submission.repository])
        try:
            repo_record_metadata = await adapter.get_metadata(submission.repository_identifier)
        except Exception as err:
            if hasattr(err, "detail"):
                err_details = err.detail
            else:
                err_details = str(err)

            err_msg = (f"Error retrieving metadata from {submission.repository} repository "
                       f"for record id: {submission.repository_identifier}: {err_details}")
            logger.error(err_msg)
            return None
        return adapter.to_catalog_record(repo_record_metadata)
    else:
        err_msg = f"Repository type {submission.repository} is not supported"
        logger.error(err_msg)
        raise Exception(err_msg)


def scheduler_event_listener(event):
    if event.exception:
        logger.error("SCHEDULER: Repository record refresh job failed")
    else:
        logger.warning("SCHEDULER: Repository record refresh job succeeded")


async def refresh(db: AsyncIOMotorClient):
    await init_beanie(database=db, document_models=[Submission, DatasetMetadataDOC])

    async for submission in Submission.find(Submission.repository != None):
        try:
            dataset = await DatasetMetadataDOC.get(submission.identifier)
            if dataset is None:
                logger.warning(f"No catalog record was found for submission: {submission.identifier}")
                continue

            updated_dataset = await retrieve_repository_record(submission)
            if updated_dataset is not None:
                # update catalog record
                updated_dataset.id = dataset.id
                await updated_dataset.replace()

                # update submission record
                dataset = await DatasetMetadataDOC.get(submission.identifier)
                updated_submission = dataset.as_submission()
                updated_submission.id = submission.id
                updated_submission.submitted = submission.submitted
                updated_submission.repository_identifier = submission.repository_identifier
                updated_submission.repository = submission.repository
                await updated_submission.replace()
            else:
                # couldn't retrieve matching repository record
                await db["discovery"].delete_one({"_id": submission.identifier})
        except:
            logger.exception(f"Failed to collect submission {submission.url}")


async def _main():
    logger.warning("SCHEDULER: starting up repository record refresh job")
    settings = get_settings()
    db = AsyncIOMotorClient(settings.db_connection_string)[settings.database_name]
    await init_beanie(database=db, document_models=[Submission, DatasetMetadataDOC])
    scheduler = AsyncIOScheduler()
    try:
        # run the job once a day at midnight
        scheduler.add_job(refresh, 'cron', hour=0, coalesce=True, args=[db])
        scheduler.add_listener(scheduler_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()
        while True:
            await asyncio.sleep(60)
    finally:
        scheduler.shutdown()
        db.close()


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
