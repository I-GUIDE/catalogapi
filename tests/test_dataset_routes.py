import pytest

from api.models.catalog import Submission
from api.models.user import User

pytestmark = pytest.mark.asyncio


async def test_create_dataset(client_test, dataset_data):
    """Testing the dataset routes for post and get"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.pop('_id')

    # prepare the expected dataset data
    dataset_data['funding'] = None
    dataset_data['publisher'] = None
    dataset_data['distribution']['comment'] = None
    dataset_data['creator'][0]['identifier']['name'] = None
    dataset_data['provider']['identifier'] = None
    dataset_data['provider']['address'] = None
    dataset_data['provider']['parentOrganization']['identifier'] = None
    dataset_data['spatialCoverage']['geo'] = None
    dataset_data['hasPart'][0]['creator'] = None
    dataset_data['isPartOf'][0]['creator'] = None
    dataset_data['includedInDataCatalog'][0]['creator']['address'] = None
    dataset_data['includedInDataCatalog'][0]['creator']['identifier'] = None

    # assert that the response contains the expected data
    assert response_data == dataset_data
    # there should be one related submission record in the db
    submissions = await Submission.find().to_list()
    assert len(submissions) == 1
    user = await User.find_one(fetch_links=True)
    assert len(user.submissions) == 1
    submission_id = submissions[0].identifier
    assert submission_id == user.submissions[0].identifier
    assert user.submission(submission_id) is not None

    # retrieve the record from the db
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200


async def test_update_dataset(client_test, dataset_data):
    """Testing the dataset put route for updating dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get('_id')
    # update the dataset record
    dataset_data['name'] = 'Updated title'
    response = await client_test.put(f"api/catalog/dataset/{record_id}", json=dataset_data)
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('_id')

    # prepare the expected dataset data
    dataset_data['funding'] = None
    dataset_data['publisher'] = None
    dataset_data['distribution']['comment'] = None
    dataset_data['creator'][0]['identifier']['name'] = None
    dataset_data['provider']['identifier'] = None
    dataset_data['provider']['address'] = None
    dataset_data['provider']['parentOrganization']['identifier'] = None
    dataset_data['spatialCoverage']['geo'] = None
    dataset_data['hasPart'][0]['creator'] = None
    dataset_data['isPartOf'][0]['creator'] = None
    dataset_data['includedInDataCatalog'][0]['creator']['address'] = None
    dataset_data['includedInDataCatalog'][0]['creator']['identifier'] = None

    # assert that the response contains the expected data
    assert response_data == dataset_data


async def test_delete_dataset(client_test, dataset_data):
    """Testing the dataset delete route for deleting a dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get('_id')
    # delete the dataset record
    response = await client_test.delete(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
    # there should not be any submission records in the db
    assert await Submission.find_many().count() == 0


@pytest.mark.parametrize("multiple", [True, False])
async def test_get_datasets(client_test, dataset_data, multiple):
    """Testing the get all datasets for a given user"""

    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    if multiple:
        # add another dataset record to the db
        dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
        assert dataset_response.status_code == 201

    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    if multiple:
        assert len(dataset_response_data) == 2
    else:
        assert len(dataset_response_data) == 1


@pytest.mark.parametrize("multiple", [True, False])
async def test_get_submissions(client_test, dataset_data, multiple):
    """Testing the get submissions route"""

    # add a dataset record to the db - this will also add a submission record
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    dataset_response_data = dataset_response.json()
    if multiple:
        # add another dataset record to the db - this will also add a submission record
        dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
        assert dataset_response.status_code == 201
        dataset_response_data = [dataset_response_data, dataset_response.json()]

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    if multiple:
        assert len(submission_response_data) == 2
        assert submission_response_data[0]['identifier'] != submission_response_data[1]['identifier']
        assert submission_response_data[0]['title'] == dataset_response_data[0]['name']
        assert submission_response_data[1]['title'] == dataset_response_data[1]['name']
        assert submission_response_data[0]['identifier'] == dataset_response_data[0]['_id']
        assert submission_response_data[1]['identifier'] == dataset_response_data[1]['_id']
        assert submission_response_data[0]['url'] == dataset_response_data[0]['url']
        assert submission_response_data[1]['url'] == dataset_response_data[1]['url']
    else:
        assert len(submission_response_data) == 1
        assert submission_response_data[0]['title'] == dataset_response_data['name']
        assert submission_response_data[0]['identifier'] == dataset_response_data['_id']
        assert submission_response_data[0]['url'] == dataset_response_data['url']
