import pytest

from tests import utils


@pytest.mark.parametrize('multiple_distribution', [True, False])
@pytest.mark.asyncio
async def test_dataset_schema_distribution_cardinality(dataset_data, dataset_model, multiple_distribution):
    """Test that a dataset pydantic model can be created from dataset json data.
    Purpose of the test is to validate dataset pydantic model where we are testing the distribution property can have
    one or more values.
    Note: This test does nat add a record to the database.
    """
    dataset_data = dataset_data
    dataset_model = dataset_model
    if multiple_distribution:
        dataset_data["distribution"] = [
            {
                "@type": "DataDownload",
                "name": "Search",
                "contentSize": "100.5 MB",
                "contentUrl": "https://www.ncdc.noaa.gov/stormevents/",
                "encodingFormat": "text/csv",
            },
            {
                "@type": "DataDownload",
                "name": "Bulk Data Download (CSV)",
                "contentSize": "102.1 MB",
                "contentUrl": "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
                "encodingFormat": "application/zip",
            },
        ]
    else:
        dataset_data["distribution"] = {
            "@type": "DataDownload",
            "name": "Search",
            "contentSize": "100.5 MB",
            "contentUrl": "https://www.ncdc.noaa.gov/stormevents/",
            "encodingFormat": "text/csv",
        }

    dataset_instance = await utils.validate_data_model(dataset_data, dataset_model)
    # checking dataset specific metadata
    if multiple_distribution:
        assert len(dataset_instance.distribution) == 2
        assert dataset_instance.distribution[0].type == "DataDownload"
        assert dataset_instance.distribution[1].type == "DataDownload"
        assert dataset_instance.distribution[0].name == "Search"
        assert dataset_instance.distribution[1].name == "Bulk Data Download (CSV)"
        assert dataset_instance.distribution[0].contentSize == "100.5 MB"
        assert dataset_instance.distribution[1].contentSize == "102.1 MB"
        assert dataset_instance.distribution[0].contentUrl == "https://www.ncdc.noaa.gov/stormevents/"
        assert (
            dataset_instance.distribution[1].contentUrl
            == "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
        )
        assert dataset_instance.distribution[0].encodingFormat == "text/csv"
        assert dataset_instance.distribution[1].encodingFormat == "application/zip"
    else:
        assert dataset_instance.distribution.type == "DataDownload"
        assert dataset_instance.distribution.name == "Search"
        assert dataset_instance.distribution.contentSize == "100.5 MB"
        assert dataset_instance.distribution.contentUrl == "https://www.ncdc.noaa.gov/stormevents/"
        assert dataset_instance.distribution.encodingFormat == "text/csv"


@pytest.mark.parametrize(
    'data_format',
    [
        {"@type": "DataDownload", "name": "Fiber_opticdist.zip"},
        {
            "@type": "DataDownload",
            "name": "Fiber_opticdist.zip",
            "contentUrl": "https://www.sciencebase.gov/catalog/file/get/626b086bd34e76103cd183c5",
        },
        {
            "@type": "DataDownload",
            "name": "Fiber_opticdist.zip",
            "contentUrl": "https://www.sciencebase.gov/catalog/file/get/626b086bd34e76103cd183c5",
            "encodingFormat": "application/zip",
        },
        {
            "@type": "DataDownload",
            "name": "Fiber_opticdist.zip",
            "contentUrl": "https://www.sciencebase.gov/catalog/file/get/626b086bd34e76103cd183c5",
            "encodingFormat": "application/zip",
            "contentSize": "439 MB",
        },
        {
            "@type": "DataDownload",
            "name": "Fiber_opticdist.zip",
            "contentUrl": "https://www.sciencebase.gov/catalog/file/get/626b086bd34e76103cd183c5",
            "encodingFormat": "application/zip",
            "contentSize": "439 MB",
            "comment": "Downloading all the data within this dataset",
        },
        {
            "@type": "DataDownload",
            "name": "Fiber_opticdist.zip",
            "contentUrl": "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
            "encodingFormat": ["text/csv", "application/zip"],
        },
    ],
)
@pytest.mark.asyncio
async def test_dataset_schema_distribution_value_type(dataset_data, dataset_model, data_format):
    """Test that a dataset pydantic model can be created from dataset json data.
    Purpose of the test is to validate dataset pydantic model where we are testing allowed value types
    for distribution property.
    Note: This test does nat add a record to the database.
    """
    dataset_data = dataset_data
    dataset_model = dataset_model
    dataset_data["distribution"] = data_format
    # validate the data model
    dataset_instance = await utils.validate_data_model(dataset_data, dataset_model)
    # checking dataset specific metadata
    assert dataset_instance.distribution.type == "DataDownload"
    assert dataset_instance.distribution.name == "Fiber_opticdist.zip"

    if "contentUrl" in data_format:
        assert dataset_instance.distribution.contentUrl == data_format["contentUrl"]
    if "encodingFormat" in data_format:
        if isinstance(data_format["encodingFormat"], list):
            assert dataset_instance.distribution.encodingFormat == data_format["encodingFormat"]
        else:
            assert dataset_instance.distribution.encodingFormat == data_format["encodingFormat"]
    if "contentSize" in data_format:
        assert dataset_instance.distribution.contentSize == data_format["contentSize"]
    if "comment" in data_format:
        assert dataset_instance.distribution.comment == data_format["comment"]


@pytest.mark.parametrize('multiple_variable', [True, False, None])
@pytest.mark.asyncio
async def test_dataset_schema_variable_cardinality(dataset_data, dataset_model, multiple_variable):
    """Test that a dataset pydantic model can be created from dataset json data.
    Purpose of the test is to validate dataset pydantic model where the variable property can have 0 or more values.
    Note: This test does nat add a record to the database.
    """
    dataset_data = dataset_data
    dataset_model = dataset_model

    if multiple_variable and multiple_variable is not None:
        dataset_data["variableMeasured"] = [
            {"@type": "PropertyValue", "name": "Streambed interface temperature values", "unitText": "degC"},
            {"@type": "PropertyValue", "name": "Air flow rate", "unitText": "m/sec"},
        ]
    elif multiple_variable is not None:
        dataset_data["variableMeasured"] = {
            "@type": "PropertyValue",
            "name": "Streambed interface temperature values",
            "unitText": "degC",
        }
    else:
        dataset_data.pop("variableMeasured", None)

    # validate the dataset model
    dataset_instance = await utils.validate_data_model(dataset_data, dataset_model)
    # checking dataset specific metadata
    if multiple_variable and multiple_variable is not None:
        assert len(dataset_instance.variableMeasured) == 2
        assert dataset_instance.variableMeasured[0].name == "Streambed interface temperature values"
        assert dataset_instance.variableMeasured[1].name == "Air flow rate"
        assert dataset_instance.variableMeasured[0].unitText == "degC"
        assert dataset_instance.variableMeasured[1].unitText == "m/sec"
    elif multiple_variable is not None:
        assert dataset_instance.variableMeasured.name == "Streambed interface temperature values"
        assert dataset_instance.variableMeasured.unitText == "degC"
    else:
        assert dataset_instance.variableMeasured is None


@pytest.mark.parametrize(
    'data_format',
    [
        {"@type": "PropertyValue", "name": "Streambed interface temperature values", "unitText": "degC"},
        "Streambed interface temperature values",
    ],
)
@pytest.mark.asyncio
async def test_dataset_schema_variable_value_type(dataset_data, dataset_model, data_format):
    """Test that a dataset pydantic model can be created from dataset json data.
    Purpose of the test is to validate dataset pydantic model where we are testing allowed value types for
    the variable property.
    Note: This test does nat add a record to the database.
    """
    dataset_data = dataset_data
    dataset_model = dataset_model
    dataset_data["variableMeasured"] = data_format
    # validate the data model
    dataset_instance = await utils.validate_data_model(dataset_data, dataset_model)
    # checking dataset specific metadata
    if isinstance(data_format, dict):
        assert dataset_instance.variableMeasured.type == "PropertyValue"
        assert dataset_instance.variableMeasured.name == data_format["name"]
        assert dataset_instance.variableMeasured.unitText == data_format["unitText"]
    else:
        assert dataset_instance.variableMeasured == data_format


@pytest.mark.parametrize('multiple_data_catalog', [True, False])
@pytest.mark.asyncio
async def test_dataset_schema_variable_cardinality(dataset_data, dataset_model, multiple_data_catalog):
    """Test that a dataset pydantic model can be created from dataset json data.
    Purpose of the test is to validate dataset pydantic model where the includedInDataCatalog property can
    have one or more values.
    Note: This test does nat add a record to the database.
    """
    dataset_data = dataset_data
    dataset_model = dataset_model
    if multiple_data_catalog:
        dataset_data["includedInDataCatalog"] = [
            {
                "@type": "DataCatalog",
                "name": "The USGS Science Data Catalog (SDC)",
                "description": "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS.",
                "url": "https://data.usgs.gov/datacatalog/",
                "identifier": "6625bdbde41c45c2b906f32be7ea70f0",
                "creator": {"@type": "Organization", "name": "U.S. Geological Survey", "url": "https://www.usgs.gov/"},
            },
            {
                "@type": "DataCatalog",
                "name": "The I-GUIDE Data Catalog",
                "description": "A centralized metadata catalog capable of indexing data from the diverse, distributed data required by the I-GUIDE project focus areas.",
                "url": "https://iguide.cuahsi.io/discover",
                "identifier": "e2fdf99cbb0c4275b32afd3c16ae6863",
                "creator": {
                    "@type": "Organization",
                    "name": "NSF Institute for Geospatial Understanding through an Integrative Discovery Environment (I-GUIDE)",
                    "url": "https://iguide.illinois.edu/",
                },
            },
        ]
    else:
        dataset_data["includedInDataCatalog"] = [
            {
                "@type": "DataCatalog",
                "name": "The USGS Science Data Catalog (SDC)",
                "description": "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS.",
                "url": "https://data.usgs.gov/datacatalog/",
                "identifier": "6625bdbde41c45c2b906f32be7ea70f0",
                "creator": {"@type": "Organization", "name": "U.S. Geological Survey", "url": "https://www.usgs.gov/"},
            }
        ]
    # validate the dataset model
    dataset_instance = await utils.validate_data_model(dataset_data, dataset_model)
    # checking dataset specific metadata
    if multiple_data_catalog:
        assert len(dataset_instance.includedInDataCatalog) == 2
        assert dataset_instance.includedInDataCatalog[0].name == "The USGS Science Data Catalog (SDC)"
        assert dataset_instance.includedInDataCatalog[1].name == "The I-GUIDE Data Catalog"
        assert dataset_instance.includedInDataCatalog[0].identifier == "6625bdbde41c45c2b906f32be7ea70f0"
        assert dataset_instance.includedInDataCatalog[1].identifier == "e2fdf99cbb0c4275b32afd3c16ae6863"
        assert dataset_instance.includedInDataCatalog[0].url == "https://data.usgs.gov/datacatalog/"
        assert dataset_instance.includedInDataCatalog[1].url == "https://iguide.cuahsi.io/discover"
        assert (
            dataset_instance.includedInDataCatalog[0].description
            == "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS."
        )
        assert (
            dataset_instance.includedInDataCatalog[1].description
            == "A centralized metadata catalog capable of indexing data from the diverse, distributed data required by the I-GUIDE project focus areas."
        )
        assert dataset_instance.includedInDataCatalog[0].creator.name == "U.S. Geological Survey"
        assert (
            dataset_instance.includedInDataCatalog[1].creator.name
            == "NSF Institute for Geospatial Understanding through an Integrative Discovery Environment (I-GUIDE)"
        )
        assert dataset_instance.includedInDataCatalog[0].creator.url == "https://www.usgs.gov/"
        assert dataset_instance.includedInDataCatalog[1].creator.url == "https://iguide.illinois.edu/"
    else:
        assert len(dataset_instance.includedInDataCatalog) == 1
        assert dataset_instance.includedInDataCatalog[0].name == "The USGS Science Data Catalog (SDC)"
        assert dataset_instance.includedInDataCatalog[0].identifier == "6625bdbde41c45c2b906f32be7ea70f0"
        assert dataset_instance.includedInDataCatalog[0].url == "https://data.usgs.gov/datacatalog/"
        assert (
            dataset_instance.includedInDataCatalog[0].description
            == "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS."
        )
        assert dataset_instance.includedInDataCatalog[0].creator.name == "U.S. Geological Survey"
        assert dataset_instance.includedInDataCatalog[0].creator.url == "https://www.usgs.gov/"
