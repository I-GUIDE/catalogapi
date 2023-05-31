import logging
import typer

from asyncio import run as aiorun
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings
from api.models.user import Submission
from api.models.utils import parse_date

logger = logging.getLogger()


def parse_temporal_coverage_to_date(coverage_date_string: str):
    start_date, end_date = coverage_date_string.split("/")
    return parse_date(start_date), parse_date(end_date)


async def _main():
    logger.warning("starting up watch submissions")
    settings = get_settings()
    db = AsyncIOMotorClient(settings.db_connection_string)[get_settings().database_name]
    await init_beanie(database=db, document_models=[Submission])

    try:
        while True:
            try:
                await watch_submissions(db)
            except:
                logger.exception("Submission Watch Task failed, restarting the task")
    finally:
        db.close()


async def watch_submissions(db: AsyncIOMotorClient):
    async with db["Submission"].watch(full_document="updateLookup", full_document_before_change="whenAvailable") as stream:
        # stream.resume_token
        async for change in stream:
            if change["operationType"] == "delete":
                document = change["fullDocumentBeforeChange"]
                await db["discovery"].delete_one({"_id": document["identifier"]})
            else:
                document = change["fullDocument"]
                catalog_entry = await db["catalog"].find_one({"_id": document["identifier"]})
                temporal_coverage = catalog_entry.get('temporalCoverage', None)
                if temporal_coverage:
                    start_date, end_date = parse_temporal_coverage_to_date(temporal_coverage)
                    catalog_entry['temporalCoverageStart'] = start_date
                    catalog_entry['temporalCoverageEnd'] = end_date
                else:
                    catalog_entry['temporalCoverageStart'] = None
                    catalog_entry['temporalCoverageEnd'] = None

                await db["discovery"].find_one_and_replace(
                        {"_id": document["identifier"]}, catalog_entry, upsert=True
                    )


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
