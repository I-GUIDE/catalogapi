import json
import os

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from api.config import get_settings
from api.main import app
from api.authentication.user import get_current_user
from api.models.catalog import CoreMetadataDOC, Submission
from api.models.schema import CoreMetadata, Dataset
from api.models.user import User
from api.procedures.user import create_or_update_user


async def override_get_current_user() -> User:
    return await create_or_update_user("pytest_user")


app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture
async def client_test():
    """
    Create an instance of the client.
    :return: yield HTTP client.
    """
    if not get_settings().testing:
        raise Exception("App is not in testing mode")
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            ac.app = app
            yield ac

        # cleanup the test db collections
        await CoreMetadataDOC.find(with_children=True).delete()
        await Submission.find().delete()


@pytest_asyncio.fixture(scope="function")
async def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


@pytest_asyncio.fixture
async def core_data(change_test_dir):
    with open("data/core_metadata.json", "r") as f:
        return json.loads(f.read())


@pytest_asyncio.fixture
async def dataset_data(core_data):
    dataset_data = core_data.copy()
    # add dataset specific metadata
    dataset_data["distribution"] = {
        "@type": "DataDownload",
        "name": "Search",
        "contentUrl": "https://www.my-unique-url.com/get_zip/9d413b9d1/",
        "encodingFormat": "application/zip",
        "contentSize": "102.1 MB",
    }
    dataset_data["variableMeasured"] = "Water Temperature"
    dataset_data["includedInDataCatalog"] = [
        {
            "@type": "DataCatalog",
            "name": "The USGS Science Data Catalog (SDC)",
            "description": "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS.",
            "url": "https://data.usgs.gov/datacatalog/",
            "identifier": "6625bdbde41c45c2b906f32be7ea70f0/",
            "creator": {"@type": "Organization", "name": "U.S. Geological Survey", "url": "https://www.usgs.gov/"},
        }
    ]
    return dataset_data


@pytest_asyncio.fixture
async def core_model():
    return CoreMetadata


@pytest_asyncio.fixture
async def dataset_model():
    class _Dataset(Dataset, CoreMetadata):
        pass

    return _Dataset


@pytest_asyncio.fixture
async def hydroshare_resource_metadata(change_test_dir):
    with open("data/hydroshare_resource_meta.json", "r") as f:
        return json.loads(f.read())


@pytest_asyncio.fixture
async def hydroshare_collection_metadata(hydroshare_resource_metadata):
    collection_meta = hydroshare_resource_metadata.copy()
    collection_meta["type"] = "CollectionResource"
    collection_meta["content_files"] = []
    relations = [
        {
            "type": "This resource includes",
            "value": "Tarboton, D. (2019). Created from iRODS by copy from create resource page, HydroShare, http://www.hydroshare.org/resource/abba182072cc48b691ca61509019e9f8"
        },
        {
            "type": "This resource includes",
            "value": "Dash, P. (2017). Water quality sensor data from the Little Bear River at Mendon Road near Mendon, UT, HydroShare, http://www.hydroshare.org/resource/fd6f39c25ccf492992c79465a2bf0030"
        },
        {
            "type": "This resource includes",
            "value": "Gan, T. (2016). Composite Resource Type Design, HydroShare, http://www.hydroshare.org/resource/e8cd813e376347c5b617deb321227a36"
        },
        {
            "type": "This resource is described by",
            "value": "another resource"
        }
    ]
    collection_meta["relations"] = relations
    return collection_meta
