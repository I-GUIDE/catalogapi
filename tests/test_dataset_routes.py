import pytest

from api.models.catalog import Submission
from api.models.user import User

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_dataset(client_test, dataset_data, test_user_access_token):
    """Testing the dataset routes for post and get"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.pop("_id")

    # adjust the temporal coverage dates for comparison
    if dataset_data["temporalCoverage"]["startDate"].endswith("Z"):
        dataset_data["temporalCoverage"]["startDate"] = dataset_data[
            "temporalCoverage"
        ]["startDate"][:-1]
    if dataset_data["temporalCoverage"]["endDate"].endswith("Z"):
        dataset_data["temporalCoverage"]["endDate"] = dataset_data["temporalCoverage"][
            "endDate"
        ][:-1]
    start_date_length = len(dataset_data["temporalCoverage"]["startDate"])
    end_date_length = len(dataset_data["temporalCoverage"]["endDate"])

    response_data["temporalCoverage"]["startDate"] = response_data["temporalCoverage"][
        "startDate"
    ][:start_date_length]
    response_data["temporalCoverage"]["endDate"] = response_data["temporalCoverage"][
        "endDate"
    ][:end_date_length]
    # assert that the response contains the expected data
    response_data.pop("repository_identifier")
    assert response_data["associatedMedia"][0]["additionalProperty"] == []
    response_data["associatedMedia"][0].pop("additionalProperty")
    assert response_data["associatedMedia"][0]["sourceOrganization"] is None
    response_data["associatedMedia"][0].pop("sourceOrganization")
    assert response_data["associatedMedia"][0]["spatialCoverage"] is None
    response_data["associatedMedia"][0].pop("spatialCoverage")
    assert response_data["associatedMedia"][0]["temporalCoverage"] is None
    response_data["associatedMedia"][0].pop("temporalCoverage")
    assert response_data["associatedMedia"][0]["variableMeasured"] == []
    response_data["associatedMedia"][0].pop("variableMeasured")
    assert response_data["spatialCoverage"]["additionalProperty"] == []
    response_data["spatialCoverage"].pop("additionalProperty")

    assert response_data == dataset_data
    # there should be one related submission record in the db
    submissions = await Submission.find().to_list()
    assert len(submissions) == 1
    user = await User.find_one(
        User.access_token == test_user_access_token, fetch_links=True
    )
    assert len(user.submissions) == 1
    submission_id = submissions[0].identifier
    assert submission_id == user.submissions[0].identifier
    assert user.submission(submission_id) is not None
    assert user.submission(submission_id).repository is None
    assert user.submission(submission_id).repository_identifier is None
    # retrieve the record from the db
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_refresh_dataset_from_hydroshare(
    client_test, test_user_access_token
):
    """Testing catalog registration/refresh of hydroshare metadata record"""

    # create hydroshare resource metadata as a catalog dataset record
    hs_published_res_id = "b5f58460941c49578e311adb9823657a"
    response = await client_test.get(
        f"api/catalog/repository/hydroshare/{hs_published_res_id}"
    )
    assert response.status_code == 200
    hs_dataset = response.json()
    assert hs_dataset["repository_identifier"] == hs_published_res_id
    await _check_hs_submission(hs_dataset, test_user_access_token, hs_published_res_id)

    # retrieve the record from the db
    record_id = hs_dataset.get("_id")
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200

    # refresh the hydroshare metadata record
    response = await client_test.put(
        f"api/catalog/repository/hydroshare/{hs_published_res_id}"
    )
    assert response.status_code == 200
    hs_dataset = response.json()
    assert hs_dataset["repository_identifier"] == hs_published_res_id
    await _check_hs_submission(hs_dataset, test_user_access_token, hs_published_res_id)


@pytest.mark.asyncio
async def test_update_dataset(client_test, dataset_data):
    """Testing the dataset put route for updating dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get("_id")
    # update the dataset name
    dataset_data["name"] = "Updated title"
    # remove citation
    dataset_data["citation"] = []
    # remove publisher
    dataset_data["publisher"] = None

    # update the dataset temporal coverage
    dataset_data["temporalCoverage"] = {
        "startDate": "2020-01-01T10:00:20",
        "endDate": "2020-11-29T00:30:00",
    }
    response = await client_test.put(
        f"api/catalog/dataset/{record_id}", json=dataset_data
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop("_id")
    # assert that the response contains the expected data
    response_data.pop("repository_identifier")
    assert response_data["associatedMedia"][0]["additionalProperty"] == []
    response_data["associatedMedia"][0].pop("additionalProperty")
    assert response_data["associatedMedia"][0]["sourceOrganization"] is None
    response_data["associatedMedia"][0].pop("sourceOrganization")
    assert response_data["associatedMedia"][0]["spatialCoverage"] is None
    response_data["associatedMedia"][0].pop("spatialCoverage")
    assert response_data["associatedMedia"][0]["temporalCoverage"] is None
    response_data["associatedMedia"][0].pop("temporalCoverage")
    assert response_data["associatedMedia"][0]["variableMeasured"] == []
    response_data["associatedMedia"][0].pop("variableMeasured")
    assert response_data["spatialCoverage"]["additionalProperty"] == []
    response_data["spatialCoverage"].pop("additionalProperty")
    assert response_data == dataset_data


@pytest.mark.asyncio
async def test_delete_dataset(client_test, dataset_data, test_user_access_token):
    """Testing the dataset delete route for deleting a dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get("_id")
    # delete the dataset record
    response = await client_test.delete(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
    # there should not be any submission records in the db
    assert await Submission.find_many().count() == 0
    user = await User.find_one(
        User.access_token == test_user_access_token, fetch_links=True
    )
    assert len(user.submissions) == 0

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200


@pytest.mark.parametrize("multiple", [True, False])
@pytest.mark.asyncio
async def test_get_datasets(client_test, dataset_data, multiple):
    """Testing the get all datasets for a given user"""

    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    if multiple:
        # add another dataset record to the db
        dataset_response = await client_test.post(
            "api/catalog/dataset", json=dataset_data
        )
        assert dataset_response.status_code == 201

    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    if multiple:
        assert len(dataset_response_data) == 2
    else:
        assert len(dataset_response_data) == 1


@pytest.mark.asyncio
async def test_get_datasets_exclude_none(client_test, dataset_data):
    """Testing exclude none is applied to dataset response model"""

    dataset_data["version"] = None
    dataset_data["spatialCoverage"]["name"] = None
    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201

    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    assert "version" not in dataset_response_data[0]
    assert "name" not in dataset_response_data[0]["spatialCoverage"]


@pytest.mark.parametrize("multiple", [True, False])
@pytest.mark.asyncio
async def test_get_submissions(client_test, dataset_data, multiple):
    """Testing the get submissions route"""

    # add a dataset record to the db - this will also add a submission record
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    dataset_response_data = dataset_response.json()
    if multiple:
        # add another dataset record to the db - this will also add a submission record
        dataset_response = await client_test.post(
            "api/catalog/dataset", json=dataset_data
        )
        assert dataset_response.status_code == 201
        dataset_response_data = [dataset_response_data, dataset_response.json()]

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    if multiple:
        assert len(submission_response_data) == 2
        assert (
            submission_response_data[0]["identifier"]
            != submission_response_data[1]["identifier"]
        )
        assert submission_response_data[0]["title"] == dataset_response_data[0]["name"]
        assert submission_response_data[1]["title"] == dataset_response_data[1]["name"]
        assert (
            submission_response_data[0]["identifier"] == dataset_response_data[0]["_id"]
        )
        assert (
            submission_response_data[1]["identifier"] == dataset_response_data[1]["_id"]
        )
        assert submission_response_data[0]["url"] == dataset_response_data[0]["url"]
        assert submission_response_data[1]["url"] == dataset_response_data[1]["url"]
    else:
        assert len(submission_response_data) == 1
        assert submission_response_data[0]["title"] == dataset_response_data["name"]
        assert submission_response_data[0]["identifier"] == dataset_response_data["_id"]
        assert submission_response_data[0]["url"] == dataset_response_data["url"]


async def _check_hs_submission(hs_dataset, user_access_token, hs_published_res_id):
    assert hs_dataset["provider"]["name"] == "HYDROSHARE"
    assert hs_dataset["provider"]["url"] == "https://www.hydroshare.org/"

    # there should be one related submission record in the db
    submissions = await Submission.find().to_list()
    assert len(submissions) == 1
    user = await User.find_one(User.access_token == user_access_token, fetch_links=True)
    assert len(user.submissions) == 1
    submission_id = submissions[0].identifier
    assert submission_id == user.submissions[0].identifier
    assert user.submission(submission_id) is not None
    assert user.submission(submission_id).repository == "HYDROSHARE"
    assert user.submission(submission_id).repository_identifier == hs_published_res_id
