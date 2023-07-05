import datetime

import pytest

from tests import utils


@pytest.mark.asyncio
async def test_core_schema(core_data, core_model):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model. Note: This test does nat
    add a record to the database.
    """
    core_data = core_data
    core_model = core_model

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.name == "Test Dataset"


@pytest.mark.parametrize('multiple_creators', [True, False])
@pytest.mark.parametrize('creator_type', ["person", "organization"])
@pytest.mark.asyncio
async def test_core_schema_creator_cardinality(core_data, core_model, multiple_creators, creator_type):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we can have one or
    more creators. Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("creator")
    if multiple_creators:
        if creator_type == "person":
            core_data["creator"] = [
                {"@type": "Person", "name": "John Doe", "email": "john.doe@gmail.com"},
                {"@type": "Person", "name": "Jane Doe", "email": "jan.doe@gmail.com"},
            ]
        else:
            core_data["creator"] = [
                {
                    "@type": "Organization",
                    "name": "National Centers for Environmental Information",
                    "url": "https://www.ncei.noaa.gov/",
                },
                {
                    "@type": "Organization",
                    "name": "National Oceanic and Atmospheric Administration",
                    "url": "https://www.noaa.gov/",
                },
            ]
    else:
        if creator_type == "person":
            core_data["creator"] = [{"@type": "Person", "name": "John Doe", "email": "john.doe@gmail.com"}]
        else:
            core_data["creator"] = [
                {
                    "@type": "Organization",
                    "name": "National Centers for Environmental Information",
                    "url": "https://www.ncei.noaa.gov/",
                }
            ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    if multiple_creators:
        if creator_type == "person":
            assert len(core_model_instance.creator) == 2
            assert core_model_instance.creator[0].type == "Person"
            assert core_model_instance.creator[1].type == "Person"
            assert core_model_instance.creator[0].name == "John Doe"
            assert core_model_instance.creator[1].name == "Jane Doe"
            assert core_model_instance.creator[0].email == "john.doe@gmail.com"
            assert core_model_instance.creator[1].email == "jan.doe@gmail.com"
        else:
            assert len(core_model_instance.creator) == 2
            assert core_model_instance.creator[0].type == "Organization"
            assert core_model_instance.creator[1].type == "Organization"
            assert core_model_instance.creator[0].name == "National Centers for Environmental Information"
            assert core_model_instance.creator[1].name == "National Oceanic and Atmospheric Administration"
            assert core_model_instance.creator[0].url == "https://www.ncei.noaa.gov/"
            assert core_model_instance.creator[1].url == "https://www.noaa.gov/"
    else:
        if creator_type == "person":
            assert core_model_instance.creator[0].type == "Person"
            assert core_model_instance.creator[0].name == "John Doe"
            assert core_model_instance.creator[0].email == "john.doe@gmail.com"
        else:
            assert core_model_instance.creator[0].type == "Organization"
            assert core_model_instance.creator[0].name == "National Centers for Environmental Information"
            assert core_model_instance.creator[0].url == "https://www.ncei.noaa.gov/"


@pytest.mark.parametrize(
    'data_format',
    [
        {"@type": "Person", "name": "John Doe"},
        {"@type": "Person", "name": "John Doe", "email": "john.doe@gmail.com"},
        {
            "@type": "Person",
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "identifier": "https://orcid.org/0000-0002-1825-0097",
        },
        {"@type": "Person", "name": "John Doe", "identifier": "https://orcid.org/0000-0002-1825-0097"},
    ],
)
@pytest.mark.asyncio
async def test_core_schema_creator_person_optional_attributes(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    email and identifier attributes are optional. Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("creator")
    core_data["creator"] = [data_format]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.creator[0].type == "Person"
    assert core_model_instance.creator[0].name == "John Doe"
    if "email" in data_format:
        assert core_model_instance.creator[0].email == "john.doe@gmail.com"
    if "identifier" in data_format:
        assert core_model_instance.creator[0].identifier == "https://orcid.org/0000-0002-1825-0097"


@pytest.mark.parametrize(
    'data_format',
    [
        {"@type": "Organization", "name": "National Centers for Environmental Information"},
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "address": "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476",
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "url": "https://www.ncei.noaa.gov/",
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "identifier": "https://orcid.org/0000-0002-1825-0097",
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "url": "https://www.ncei.noaa.gov/",
            "identifier": "https://orcid.org/0000-0002-1825-0097",
            "address": "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476",
        },
    ],
)
@pytest.mark.asyncio
async def test_core_schema_creator_organization_optional_attributes(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    optional attributes of the organization object. Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("creator")
    core_data["creator"] = [data_format]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.creator[0].type == "Organization"
    assert core_model_instance.creator[0].name == "National Centers for Environmental Information"
    if "url" in data_format:
        assert core_model_instance.creator[0].url == "https://www.ncei.noaa.gov/"
    if "identifier" in data_format:
        assert core_model_instance.creator[0].identifier == "https://orcid.org/0000-0002-1825-0097"
    if "address" in data_format:
        assert core_model_instance.creator[0].address == "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476"


@pytest.mark.parametrize(
    'data_format',
    [
        {"@type": "Person", "name": "John Doe", "identifier": "https://orcid.org/0000-0002-1825-0097"},
        {
            "@type": "Person",
            "name": "John Doe",
            "identifier": ["https://orcid.org/0000-0002-1825-0097", "https://orcid.org/0000-0002-1825-0098"],
        },
        {"@type": "Person", "name": "John Doe", "identifier": "12345-6789-abcd-efgh"},
        {
            "@type": "Person",
            "name": "John Doe",
            "identifier": {
                "@type": "PropertyValue",
                "@id": "https://orcid.org/0000-0000-0000-0001",
                "propertyID": "https://registry.identifiers.org/registry/orcid",
                "url": "https://orcid.org/0000-0000-0000-0001",
                "value": "0000-0000-0000-0001",
            },
        },
    ],
)
@pytest.mark.asyncio
async def test_core_schema_creator_person_identifier(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where the creator
    property of type person can have different value types for its identifier attribute.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("creator")
    core_data["creator"] = [data_format]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.creator[0].type == "Person"
    assert core_model_instance.creator[0].name == "John Doe"
    if isinstance(data_format["identifier"], list):
        assert len(core_model_instance.creator[0].identifier) == len(data_format["identifier"])
        assert core_model_instance.creator[0].identifier[0] == data_format["identifier"][0]
        assert core_model_instance.creator[0].identifier[1] == data_format["identifier"][1]
    elif isinstance(data_format["identifier"], str):
        assert core_model_instance.creator[0].identifier == data_format["identifier"]
    elif isinstance(data_format["identifier"], dict):
        assert core_model_instance.creator[0].identifier.type == data_format["identifier"]["@type"]
        assert core_model_instance.creator[0].identifier.id == data_format["identifier"]["@id"]
        assert core_model_instance.creator[0].identifier.propertyID == data_format["identifier"]["propertyID"]
        assert core_model_instance.creator[0].identifier.url == data_format["identifier"]["url"]
        assert core_model_instance.creator[0].identifier.value == data_format["identifier"]["value"]


@pytest.mark.parametrize(
    'data_format',
    [
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "identifier": "https://orcid.org/0000-0002-1825-0097",
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "identifier": ["https://orcid.org/0000-0002-1825-0097", "https://orcid.org/0000-0002-1825-0098"],
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "identifier": "12345-6789-abcd-efgh",
        },
        {
            "@type": "Organization",
            "name": "National Centers for Environmental Information",
            "identifier": {
                "@type": "PropertyValue",
                "@id": "https://orcid.org/0000-0000-0000-0001",
                "propertyID": "https://registry.identifiers.org/registry/orcid",
                "url": "https://orcid.org/0000-0000-0000-0001",
                "value": "0000-0000-0000-0001",
            },
        },
    ],
)
@pytest.mark.asyncio
async def test_core_schema_creator_organization_identifier(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where the
    creator property of type organization can have different value types for its identifier attribute.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("creator")
    core_data["creator"] = [data_format]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.creator[0].type == "Organization"
    assert core_model_instance.creator[0].name == "National Centers for Environmental Information"
    if isinstance(data_format["identifier"], list):
        assert len(core_model_instance.creator[0].identifier) == len(data_format["identifier"])
        assert core_model_instance.creator[0].identifier[0] == data_format["identifier"][0]
        assert core_model_instance.creator[0].identifier[1] == data_format["identifier"][1]
    elif isinstance(data_format["identifier"], str):
        assert core_model_instance.creator[0].identifier == data_format["identifier"]
    elif isinstance(data_format["identifier"], dict):
        assert core_model_instance.creator[0].identifier.type == data_format["identifier"]["@type"]
        assert core_model_instance.creator[0].identifier.id == data_format["identifier"]["@id"]
        assert core_model_instance.creator[0].identifier.propertyID == data_format["identifier"]["propertyID"]
        assert core_model_instance.creator[0].identifier.url == data_format["identifier"]["url"]
        assert core_model_instance.creator[0].identifier.value == data_format["identifier"]["value"]


@pytest.mark.parametrize('multiple_media', [True, False, None])
@pytest.mark.asyncio
async def test_core_schema_associated_media_cardinality(core_data, core_model, multiple_media):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    one or more associated media objects can be created. Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    if multiple_media is None:
        core_data.pop("associatedMedia", None)
    if multiple_media and multiple_media is not None:
        core_data["associatedMedia"] = [
            {
                "@type": "DataDownload",
                "contentUrl": "https://www.hydroshare.org/resource/51d1539bf6e94b15ac33f7631228118c/data/contents/USGS_Harvey_gages_TxLaMsAr.csv",
                "encodingFormat": "text/csv",
                "contentSize": "0.17 GB",
                "name": "USGS gage locations within the Harvey-affected areas in Texas",
            },
            {
                "@type": "VideoObject",
                "contentUrl": "https://www.hydroshare.org/resource/81cb3f6c0dde4433ae4f43a26a889864/data/contents/HydroClientMovie.mp4",
                "encodingFormat": "video/mp4",
                "contentSize": "79.2 MB",
                "name": "HydroClient Video",
            },
        ]
    elif multiple_media is not None:
        core_data["associatedMedia"] = [
            {
                "@type": "DataDownload",
                "contentUrl": "https://www.hydroshare.org/resource/51d1539bf6e94b15ac33f7631228118c/data/contents/USGS_Harvey_gages_TxLaMsAr.csv",
                "encodingFormat": "text/csv",
                "contentSize": "0.17 MB",
                "name": "USGS gage locations within the Harvey-affected areas in Texas",
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    if multiple_media is None:
        assert core_model_instance.associatedMedia is None
    if multiple_media and multiple_media is not None:
        assert len(core_model_instance.associatedMedia) == 2
        assert core_model_instance.associatedMedia[0].type == "DataDownload"
        assert core_model_instance.associatedMedia[1].type == "VideoObject"
        assert (
            core_model_instance.associatedMedia[0].name
            == "USGS gage locations within the Harvey-affected areas in Texas"
        )
        assert core_model_instance.associatedMedia[1].name == "HydroClient Video"
        assert core_model_instance.associatedMedia[0].contentSize == "0.17 GB"
        assert core_model_instance.associatedMedia[1].contentSize == "79.2 MB"
        assert core_model_instance.associatedMedia[0].encodingFormat == "text/csv"
        assert core_model_instance.associatedMedia[1].encodingFormat == "video/mp4"
    elif multiple_media is not None:
        assert core_model_instance.associatedMedia[0].type == "DataDownload"
        assert (
            core_model_instance.associatedMedia[0].name
            == "USGS gage locations within the Harvey-affected areas in Texas"
        )
        assert core_model_instance.associatedMedia[0].contentSize == "0.17 MB"
        assert core_model_instance.associatedMedia[0].encodingFormat == "text/csv"


@pytest.mark.parametrize(
    'content_size_format',
    [
        "100.17 KB",
        "100.17kilobytes",
        ".89 KB",
        "0.89 KB",
        "100.17 MB",
        "100.17 megabytes",
        "100.17 GB",
        "100.17 gigabytes",
        "100.17 TB",
        "100.17 terabytes",
        "100.17 PB",
        "10.170 petabytes",
    ],
)
@pytest.mark.asyncio
async def test_core_schema_associated_media_content_size(core_data, core_model, content_size_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    valid values for the contentSize attribute of the associatedMedia property.
    Note: This test does nat add a record to the database.
    """

    core_data = core_data
    core_model = core_model

    core_data["associatedMedia"] = [
        {
            "@type": "DataDownload",
            "contentUrl": "https://www.hydroshare.org/resource/51d1539bf6e94b15ac33f7631228118c/data/contents/USGS_Harvey_gages_TxLaMsAr.csv",
            "encodingFormat": "text/csv",
            "contentSize": content_size_format,
            "name": "USGS gage locations within the Harvey-affected areas in Texas",
        }
    ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    assert core_model_instance.associatedMedia[0].contentSize == content_size_format


@pytest.mark.parametrize('include_coverage', [True, False])
@pytest.mark.asyncio
async def test_core_schema_temporal_coverage_optional(core_data, core_model, include_coverage):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    temporal coverage can be optional.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    coverage_value = "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"
    core_data.pop("temporalCoverage", None)
    if not include_coverage:
        core_data.pop("temporalCoverage", None)
    else:
        core_data["temporalCoverage"] = coverage_value

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if not include_coverage:
        assert core_model_instance.temporalCoverage is None
    else:
        assert core_model_instance.temporalCoverage == coverage_value


@pytest.mark.parametrize(
    'data_format',
    [
        "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z",
        "2007-03-01T13:00:00Z/2008-05-11",
        "2007-03-01/2008-05-11T15:30:00Z",
        "2007-03-01/2010-01-01",
        "2007-03-01T13:00:00Z/..",
        "2007-03-01/..",
        "2007-03/..",
        "2007/..",
    ],
)
@pytest.mark.asyncio
async def test_core_schema_temporal_coverage_format(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    valid values for temporal coverage.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data["temporalCoverage"] = data_format

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    assert core_model_instance.temporalCoverage == data_format


@pytest.mark.parametrize('include_coverage', [True, False])
@pytest.mark.asyncio
async def test_core_schema_spatial_coverage_optional(core_data, core_model, include_coverage):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    spatial coverage can be optional.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    coverage_value = {
        "@type": "Place",
        "name": "CUAHSI Office",
        "address": "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476",
    }

    if not include_coverage:
        core_data.pop("spatialCoverage", None)
    else:
        core_data["spatialCoverage"] = coverage_value

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if not include_coverage:
        assert core_model_instance.spatialCoverage is None
    else:
        assert core_model_instance.spatialCoverage.type == coverage_value["@type"]
        assert core_model_instance.spatialCoverage.name == coverage_value["name"]
        assert core_model_instance.spatialCoverage.address == coverage_value["address"]


@pytest.mark.parametrize(
    'data_format',
    [
        {
            "@type": "Place",
            "name": "CUAHSI Office",
            "address": "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476",
        },
        {"@type": "Place", "geo": {"@type": "GeoCoordinates", "latitude": 39.3280, "longitude": 120.1633}},
        {"@type": "Place", "geo": {"@type": "GeoShape", "line": "39.3280 120.1633 40.445 123.7878"}},
        {
            "@type": "Place",
            "geo": {
                "@type": "GeoShape",
                "polygon": "39.3280 120.1633 40.445 123.7878 41 121 39.77 122.42 39.3280 120.1633",
            },
        },
    ],
)
@pytest.mark.asyncio
async def test_core_schema_spatial_coverage_value_type(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    valid values for spatial coverage.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data["spatialCoverage"] = data_format
    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    assert core_model_instance.spatialCoverage.type == "Place"
    if "name" in data_format:
        assert core_model_instance.spatialCoverage.name == data_format["name"]
    if "geo" in data_format:
        if data_format["geo"]["@type"] == "GeoCoordinates":
            assert core_model_instance.spatialCoverage.geo.latitude == data_format["geo"]["latitude"]
            assert core_model_instance.spatialCoverage.geo.longitude == data_format["geo"]["longitude"]
        elif data_format["geo"]["@type"] == "GeoShape":
            if "polygon" in data_format["geo"]:
                assert core_model_instance.spatialCoverage.geo.polygon == data_format["geo"]["polygon"]
            else:
                assert core_model_instance.spatialCoverage.geo.line == data_format["geo"]["line"]
    if "address" in data_format:
        assert core_model_instance.spatialCoverage.address == data_format["address"]


@pytest.mark.parametrize('include_creative_works', [True, False])
@pytest.mark.asyncio
async def test_create_dataset_creative_works_status_optional(core_data, core_model, include_creative_works):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    creativeWorkStatus can be optional.
    Note: This test does nat add a record to the database.
    """

    core_data = core_data
    core_model = core_model
    if not include_creative_works:
        core_data.pop("creativeWorkStatus", None)
    else:
        core_data["creativeWorkStatus"] = {
            "@type": "DefinedTerm",
            "name": "Private",
            "description": "This is a private dataset",
        }

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if not include_creative_works:
        assert core_model_instance.creativeWorkStatus is None
    else:
        assert core_model_instance.creativeWorkStatus.type == "DefinedTerm"
        assert core_model_instance.creativeWorkStatus.name == "Private"
        assert core_model_instance.creativeWorkStatus.description == "This is a private dataset"


@pytest.mark.parametrize('include_multiple', [True, False])
@pytest.mark.asyncio
async def test_core_schema_keywords_cardinality(core_data, core_model, include_multiple):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that one or more keywords can be added.
    Note: This test does nat add a record to the database.
    """

    core_data = core_data
    core_model = core_model
    core_data.pop("keywords", None)
    if include_multiple:
        core_data["keywords"] = [
            {
                "@type": "DefinedTerm",
                "name": "Leaf wetness",
                "description": "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall.",
                "inDefinedTermSet": "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV",
            },
            {
                "@type": "DefinedTerm",
                "name": "Core",
                "description": "Core sample resulting in a section of a substance",
                "inDefinedTermSet": "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=SampleTypeCV",
            },
        ]
    else:
        core_data["keywords"] = [
            {
                "@type": "DefinedTerm",
                "name": "Leaf wetness",
                "description": "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall.",
                "inDefinedTermSet": "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV",
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if include_multiple:
        assert len(core_model_instance.keywords) == 2
        assert core_model_instance.keywords[0].name == "Leaf wetness"
        assert core_model_instance.keywords[1].name == "Core"
        assert (
            core_model_instance.keywords[0].description
            == "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall."
        )
        assert core_model_instance.keywords[1].description == "Core sample resulting in a section of a substance"
        assert (
            core_model_instance.keywords[0].inDefinedTermSet
            == "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV"
        )
        assert (
            core_model_instance.keywords[1].inDefinedTermSet
            == "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=SampleTypeCV"
        )
    else:
        assert len(core_model_instance.keywords) == 1
        assert core_model_instance.keywords[0].name == "Leaf wetness"
        assert (
            core_model_instance.keywords[0].description
            == "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall."
        )
        assert (
            core_model_instance.keywords[0].inDefinedTermSet
            == "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV"
        )


@pytest.mark.parametrize("kw_type", ["DefinedTerm", "String"])
@pytest.mark.asyncio
async def test_core_schema_keywords_value_type(core_data, core_model, kw_type):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    valid value types for keywords.
    Note: This test does nat add a record to the database.
    """

    core_data = core_data
    core_model = core_model
    core_data.pop("keywords", None)
    if kw_type == "DefinedTerm":
        core_data["keywords"] = [
            {
                "@type": "DefinedTerm",
                "name": "Leaf wetness",
                "description": "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall.",
                "inDefinedTermSet": "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV",
            },
            {
                "@type": "DefinedTerm",
                "name": "Core",
                "description": "Core sample resulting in a section of a substance",
                "inDefinedTermSet": "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=SampleTypeCV",
            },
        ]
    else:
        core_data["keywords"] = ["Leaf wetness", "Core"]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if kw_type == "DefinedTerm":
        assert len(core_model_instance.keywords) == 2
        assert core_model_instance.keywords[0].type == "DefinedTerm"
        assert core_model_instance.keywords[1].type == "DefinedTerm"
        assert core_model_instance.keywords[0].name == "Leaf wetness"
        assert core_model_instance.keywords[1].name == "Core"
        assert (
            core_model_instance.keywords[0].description
            == "The effect of moisture settling on the surface of a leaf as a result of either condensation or rainfall."
        )
        assert core_model_instance.keywords[1].description == "Core sample resulting in a section of a substance"
        assert (
            core_model_instance.keywords[0].inDefinedTermSet
            == "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=VariableNameCV"
        )
        assert (
            core_model_instance.keywords[1].inDefinedTermSet
            == "http://his.cuahsi.org/mastercvreg/edit_cv11.aspx?tbl=SampleTypeCV"
        )
    else:
        assert len(core_model_instance.keywords) == 2
        assert core_model_instance.keywords[0] == "Leaf wetness"
        assert core_model_instance.keywords[1] == "Core"


@pytest.mark.parametrize(
    "data_format",
    [
        "https://creativecommons.org/licenses/by/4.0/",
        {"@type": "CreativeWork", "name": "MIT License", "url": "https://spdx.org/licenses/MIT"},
    ],
)
@pytest.mark.asyncio
async def test_core_schema_keywords_value_type(core_data, core_model, data_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    valid value types for license property.
    Note: This test does nat add a record to the database.
    """

    core_data = core_data
    core_model = core_model
    core_data["license"] = data_format
    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if isinstance(data_format, str):
        assert core_model_instance.license == data_format
    else:
        assert core_model_instance.license.type == data_format["@type"]
        assert core_model_instance.license.name == data_format["name"]
        assert core_model_instance.license.url == data_format["url"]


@pytest.mark.parametrize('is_multiple', [True, False, None])
@pytest.mark.asyncio
async def test_core_schema_has_part_of_cardinality(core_data, core_model, is_multiple):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the hasPartOf property is optional and one or more values can be added for this property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("hasPart", None)

    if is_multiple and is_multiple is not None:
        core_data["hasPart"] = [
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Bathymetry",
                "description": "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry.",
                "identifier": "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/",
            },
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Level and Volume",
                "description": "Time series of level, area and volume in the Great Salt Lake.",
                "identifier": "https://www.hydroshare.org/resource/b26090299ec947c692d4ee4651815579/",
            },
        ]
    elif is_multiple is not None:
        core_data["hasPart"] = [
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Bathymetry",
                "description": "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry.",
                "identifier": "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/",
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if is_multiple and is_multiple is not None:
        assert len(core_model_instance.hasPart) == 2
        assert core_model_instance.hasPart[0].type == "CreativeWork"
        assert core_model_instance.hasPart[1].type == "CreativeWork"
        assert core_model_instance.hasPart[0].name == "Great Salt Lake Bathymetry"
        assert core_model_instance.hasPart[1].name == "Great Salt Lake Level and Volume"
        assert (
            core_model_instance.hasPart[0].description
            == "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry."
        )
        assert (
            core_model_instance.hasPart[1].description
            == "Time series of level, area and volume in the Great Salt Lake."
        )
        assert (
            core_model_instance.hasPart[0].identifier
            == "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/"
        )
        assert (
            core_model_instance.hasPart[1].identifier
            == "https://www.hydroshare.org/resource/b26090299ec947c692d4ee4651815579/"
        )
    elif is_multiple is not None:
        assert len(core_model_instance.hasPart) == 1
        assert core_model_instance.hasPart[0].type == "CreativeWork"
        assert core_model_instance.hasPart[0].name == "Great Salt Lake Bathymetry"
        assert (
            core_model_instance.hasPart[0].description
            == "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry."
        )
        assert (
            core_model_instance.hasPart[0].identifier
            == "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/"
        )
    else:
        assert core_model_instance.hasPart is None


@pytest.mark.parametrize('is_multiple', [True, False, None])
@pytest.mark.asyncio
async def test_core_schema_is_part_of_cardinality(core_data, core_model, is_multiple):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the isPartOf property is optional and one or more values can be added for this property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("isPartOf", None)

    if is_multiple and is_multiple is not None:
        core_data["isPartOf"] = [
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Bathymetry",
                "description": "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry.",
                "identifier": "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/",
            },
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Level and Volume",
                "description": "Time series of level, area and volume in the Great Salt Lake.",
                "identifier": "https://www.hydroshare.org/resource/b26090299ec947c692d4ee4651815579/",
            },
        ]
    elif is_multiple is not None:
        core_data["isPartOf"] = [
            {
                "@type": "CreativeWork",
                "name": "Great Salt Lake Bathymetry",
                "description": "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry.",
                "identifier": "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/",
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if is_multiple and is_multiple is not None:
        assert len(core_model_instance.isPartOf) == 2
        assert core_model_instance.isPartOf[0].type == "CreativeWork"
        assert core_model_instance.isPartOf[1].type == "CreativeWork"
        assert core_model_instance.isPartOf[0].name == "Great Salt Lake Bathymetry"
        assert core_model_instance.isPartOf[1].name == "Great Salt Lake Level and Volume"
        assert (
            core_model_instance.isPartOf[0].description
            == "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry."
        )
        assert (
            core_model_instance.isPartOf[1].description
            == "Time series of level, area and volume in the Great Salt Lake."
        )
        assert (
            core_model_instance.isPartOf[0].identifier
            == "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/"
        )
        assert (
            core_model_instance.isPartOf[1].identifier
            == "https://www.hydroshare.org/resource/b26090299ec947c692d4ee4651815579/"
        )
    elif is_multiple is not None:
        assert len(core_model_instance.isPartOf) == 1
        assert core_model_instance.isPartOf[0].type == "CreativeWork"
        assert core_model_instance.isPartOf[0].name == "Great Salt Lake Bathymetry"
        assert (
            core_model_instance.isPartOf[0].description
            == "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry."
        )
        assert (
            core_model_instance.isPartOf[0].identifier
            == "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/"
        )
    else:
        assert core_model_instance.isPartOf is None


@pytest.mark.parametrize('part_name', ["hasPart", "isPartOf"])
@pytest.mark.parametrize(
    'identifier_format',
    [
        "https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/",
        "582060f00f6b443bb26e896426d9f62a",
        {
            "@id": "https://doi.org/10.4211/hs.6625bdbde41c45c2b906f32be7ea70f0",
            "@type": "PropertyValue",
            "name": "DOI: 10.4211/hs.6625bdbde41c45c2b906f32be7ea70f0",
            "propertyID": "https://registry.identifiers.org/registry/doi",
            "value": "doi:10.4211/hs.6625bdbde41c45c2b906f32be7ea70f0",
            "url": "https://doi.org/10.4211/hs.6625bdbde41c45c2b906f32be7ea70f0",
        },
    ],
)
@pytest.mark.asyncio
async def test_core_schema_part_identifier_value_type(core_data, core_model, part_name, identifier_format):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    allowed value type for the hasPartOf/IsPartOf property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data[part_name] = []
    data_format = {
        "@type": "CreativeWork",
        "name": "Great Salt Lake Bathymetry",
        "description": "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry.",
        "identifier": identifier_format,
    }
    core_data[part_name].append(data_format)
    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if part_name == "hasPart":
        part = core_model_instance.hasPart
    else:
        part = core_model_instance.isPartOf

    assert len(part) == 1
    assert part[0].type == "CreativeWork"
    assert part[0].name == "Great Salt Lake Bathymetry"
    assert part[0].description == "Digital Elevation Model for the Great Salt Lake, lake bed bathymetry."
    if isinstance(identifier_format, dict):
        assert part[0].identifier.id == identifier_format["@id"]
        assert part[0].identifier.type == identifier_format["@type"]
        assert part[0].identifier.name == identifier_format["name"]
        assert part[0].identifier.propertyID == identifier_format["propertyID"]
        assert part[0].identifier.value == identifier_format["value"]
        assert part[0].identifier.url == identifier_format["url"]
    else:
        assert part[0].identifier == identifier_format


@pytest.mark.parametrize('property_name', ["hasPart", "isPartOf"])
@pytest.mark.parametrize('include_creator', [True, False])
@pytest.mark.asyncio
async def test_core_schema_part_creator_optional(core_data, core_model, property_name, include_creator):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    creator attribute for the hasPartOf/IsPartOf property is optional.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data[property_name] = []
    data_format = {
        "@type": "CreativeWork",
        "name": "Collection of Great Salt Lake Data",
        "description": "Data from the Great Salt Lake and its basin",
        "identifier": "https://www.hydroshare.org/resource/b6c4fcad40c64c4cb4dd7d4a25d0db6e/",
    }
    if include_creator:
        data_format["creator"] = {"@type": "Person", "name": "David Tarboton"}
    core_data[property_name].append(data_format)
    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if property_name == "hasPart":
        part = core_model_instance.hasPart
    else:
        part = core_model_instance.isPartOf
    assert len(part) == 1
    assert part[0].type == "CreativeWork"
    assert part[0].name == "Collection of Great Salt Lake Data"
    assert part[0].description == "Data from the Great Salt Lake and its basin"
    assert part[0].identifier == "https://www.hydroshare.org/resource/b6c4fcad40c64c4cb4dd7d4a25d0db6e/"
    if include_creator:
        assert part[0].creator.type == "Person"
        assert part[0].creator.name == "David Tarboton"


@pytest.mark.parametrize('dt_type', ["date", "datetime", None])
@pytest.mark.asyncio
async def test_core_schema_date_value_type(core_data, core_model, dt_type):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    allowed value types for the date type attributes (dateCreated, dateModified, and datePublished).
    Also testing that dateModified and datePublished are optional.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    if dt_type == "date":
        core_data["dateCreated"] = "2020-01-01"
        core_data["dateModified"] = "2020-02-01"
        core_data["datePublished"] = "2020-05-01"
    elif dt_type == "datetime":
        core_data["dateCreated"] = "2020-01-01T10:00:05"
        core_data["dateModified"] = "2020-02-01T11:20:30"
        core_data["datePublished"] = "2020-05-01T08:00:45"
    else:
        core_data["dateCreated"] = "2020-01-01T10:00:05"
        core_data.pop("dateModified", None)
        core_data.pop("datePublished", None)

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if dt_type == "date":
        assert core_model_instance.dateCreated == datetime.date(2020, 1, 1)
        assert core_model_instance.dateModified == datetime.date(2020, 2, 1)
        assert core_model_instance.datePublished == datetime.date(2020, 5, 1)
    elif dt_type == "datetime":
        assert core_model_instance.dateCreated == datetime.datetime(2020, 1, 1, 10, 0, 5)
        assert core_model_instance.dateModified == datetime.datetime(2020, 2, 1, 11, 20, 30)
        assert core_model_instance.datePublished == datetime.datetime(2020, 5, 1, 8, 0, 45)
    else:
        assert core_model_instance.dateCreated == datetime.datetime(2020, 1, 1, 10, 0, 5)
        assert core_model_instance.dateModified is None
        assert core_model_instance.datePublished is None


@pytest.mark.parametrize('provider_pub_type', ["person", "organization", "id"])
@pytest.mark.parametrize('key_name', ["provider", "publisher"])
@pytest.mark.asyncio
async def test_core_schema_provider_and_publisher_value_type(core_data, core_model, provider_pub_type, key_name):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    allowed value types for the provide/publisher attributes.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    core_data.pop("provider", None)
    if key_name == "publisher":
        # we need a mandatory provider element
        core_data["provider"] = {"@type": "Person", "name": "John Doe", "email": "jdoe@gmail.com"}
        if provider_pub_type == "person":
            core_data[key_name] = {"@type": "Person", "name": "John Doe", "email": "jdoe@gmail.com"}
    if provider_pub_type == "person" and key_name == "provider":
        core_data[key_name] = {"@type": "Person", "name": "John Doe", "email": "jdoe@gmail.com"}
    elif provider_pub_type == "organization":
        core_data[key_name] = {
            "@type": "Organization",
            "name": "HydroShare",
            "url": "https://hydroshare.org",
            "parentOrganization": {
                "@type": "Organization",
                "name": "CUAHSI",
                "url": "https://www.cuahsi.org/",
                "address": "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476",
            },
        }
    elif provider_pub_type == "id":
        core_data[key_name] = {"@id": "https://hydroshare.org"}

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if key_name == "provider":
        element = core_model_instance.provider
    else:
        element = core_model_instance.publisher
    if provider_pub_type == "person":
        assert element.type == "Person"
        assert element.name == "John Doe"
        assert element.email == "jdoe@gmail.com"
    elif provider_pub_type == "organization":
        assert element.type == "Organization"
        assert element.name == "HydroShare"
        assert element.url == "https://hydroshare.org"
        assert element.parentOrganization.type == "Organization"
        assert element.parentOrganization.name == "CUAHSI"
        assert element.parentOrganization.url == "https://www.cuahsi.org/"
        assert element.parentOrganization.address == "1167 Massachusetts Ave Suites 418 & 419, Arlington, MA 02476"
    else:
        assert element.id == "https://hydroshare.org"


@pytest.mark.parametrize('multiple_values', [True, False, None])
@pytest.mark.asyncio
async def test_core_schema_subject_of_cardinality(core_data, core_model, multiple_values):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the subjectOf property is optional and one or more values can be added for this property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    if multiple_values is None:
        core_data.pop("subjectOf", None)
    elif multiple_values:
        core_data["subjectOf"] = [
            {
                "@type": "CreativeWork",
                "name": "Test Creative Work - 1",
                "url": "https://www.hydroshare.org/hsapi/resource/c1be74eeea614d65a29a185a66a7552f/scimeta/",
                "encodingFormat": "application/rdf+xml",
            },
            {
                "@type": "CreativeWork",
                "name": "Test Creative Work - 2",
                "url": "https://www.hydroshare.org/hsapi/resource/b1be74eeea614d65a29a185a66a7552c/scimeta/",
                "encodingFormat": "application/rdf+xml",
            },
        ]
    else:
        core_data["subjectOf"] = [
            {
                "@type": "CreativeWork",
                "name": "Test Creative Work",
                "url": "https://www.hydroshare.org/hsapi/resource/c1be74eeea614d65a29a185a66a7552f/scimeta/",
                "encodingFormat": "application/rdf+xml",
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if multiple_values and multiple_values is not None:
        assert len(core_model_instance.subjectOf) == 2
        assert core_model_instance.subjectOf[0].type == "CreativeWork"
        assert core_model_instance.subjectOf[0].name == "Test Creative Work - 1"
        assert (
            core_model_instance.subjectOf[0].url
            == "https://www.hydroshare.org/hsapi/resource/c1be74eeea614d65a29a185a66a7552f/scimeta/"
        )
        assert core_model_instance.subjectOf[0].encodingFormat == "application/rdf+xml"
        assert core_model_instance.subjectOf[1].type == "CreativeWork"
        assert core_model_instance.subjectOf[1].name == "Test Creative Work - 2"
        assert (
            core_model_instance.subjectOf[1].url
            == "https://www.hydroshare.org/hsapi/resource/b1be74eeea614d65a29a185a66a7552c/scimeta/"
        )
        assert core_model_instance.subjectOf[1].encodingFormat == "application/rdf+xml"
    elif multiple_values is not None:
        assert len(core_model_instance.subjectOf) == 1
        assert core_model_instance.subjectOf[0].type == "CreativeWork"
        assert core_model_instance.subjectOf[0].name == "Test Creative Work"
        assert (
            core_model_instance.subjectOf[0].url
            == "https://www.hydroshare.org/hsapi/resource/c1be74eeea614d65a29a185a66a7552f/scimeta/"
        )
        assert core_model_instance.subjectOf[0].encodingFormat == "application/rdf+xml"
    else:
        assert core_model_instance.subjectOf is None


@pytest.mark.parametrize('version_value_type', ["float", "string", None])
@pytest.mark.asyncio
async def test_core_schema_version_value_type(core_data, core_model, version_value_type):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the version property is optional and allowed value types for this property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    if version_value_type is None:
        core_data.pop("version", None)
    elif version_value_type == "float":
        core_data["version"] = 1.0
    else:
        core_data["version"] = "v1.0"

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if version_value_type == "float":
        assert core_model_instance.version == 1.0
    elif version_value_type == "string":
        assert core_model_instance.version == "v1.0"
    else:
        assert core_model_instance.version is None


@pytest.mark.parametrize('include_language', [True, False])
@pytest.mark.asyncio
async def test_core_schema_language_cardinality(core_data, core_model, include_language):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the inLanguage property is optional.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model
    if include_language:
        core_data["inLanguage"] = "en-US"
    else:
        core_data.pop("inLanguage", None)

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if include_language:
        assert core_model_instance.inLanguage == "en-US"
    else:
        assert core_model_instance.inLanguage is None


@pytest.mark.parametrize('multiple_funder', [True, False, None])
@pytest.mark.asyncio
async def test_core_schema_funding_cardinality(core_data, core_model, multiple_funder):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    that the funding property is optional and one or more values can be added to this property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model

    if multiple_funder and multiple_funder is not None:
        core_data["funding"] = [
            {
                "@type": "MonetaryGrant",
                "name": "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment",
                "url": "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329",
                "funder": {
                    "@type": "Organization",
                    "name": "National Science Foundation",
                    "identifier": ["https://ror.org/021nxhr62", "https://doi.org/10.13039/100000001"],
                },
            },
            {
                "@type": "MonetaryGrant",
                "name": "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment",
                "url": "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329",
                "funder": {"@type": "Person", "name": "John Doe", "email": "johnd@gmail.com"},
            },
        ]
    elif multiple_funder is not None:
        core_data["funding"] = [
            {
                "@type": "MonetaryGrant",
                "name": "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment",
                "url": "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329",
                "funder": {"@type": "Person", "name": "John Doe", "email": "johnd@gmail.com"},
            }
        ]
    else:
        core_data.pop("funding", None)

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)
    if multiple_funder and multiple_funder is not None:
        assert core_model_instance.funding[0].type == "MonetaryGrant"
        assert (
            core_model_instance.funding[0].name
            == "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment"
        )
        assert core_model_instance.funding[0].url == "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329"
        assert core_model_instance.funding[0].funder.type == "Organization"
        assert core_model_instance.funding[0].funder.name == "National Science Foundation"
        assert core_model_instance.funding[0].funder.identifier[0] == "https://ror.org/021nxhr62"
        assert core_model_instance.funding[0].funder.identifier[1] == "https://doi.org/10.13039/100000001"
        assert core_model_instance.funding[1].type == "MonetaryGrant"
        assert (
            core_model_instance.funding[1].name
            == "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment"
        )
        assert core_model_instance.funding[1].url == "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329"
        assert core_model_instance.funding[1].funder.type == "Person"
        assert core_model_instance.funding[1].funder.name == "John Doe"
        assert core_model_instance.funding[1].funder.email == "johnd@gmail.com"
    elif multiple_funder is not None:
        assert core_model_instance.funding[0].type == "MonetaryGrant"
        assert (
            core_model_instance.funding[0].name
            == "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment"
        )
        assert core_model_instance.funding[0].url == "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329"
        assert core_model_instance.funding[0].funder.type == "Person"
        assert core_model_instance.funding[0].funder.name == "John Doe"
        assert core_model_instance.funding[0].funder.email == "johnd@gmail.com"
    else:
        assert core_model_instance.funding is None


@pytest.mark.parametrize('funder_type', ["person", "organization"])
@pytest.mark.asyncio
async def test_core_schema_funding_funder_value_type(core_data, core_model, funder_type):
    """Test that a core metadata pydantic model can be created from core metadata json.
    Purpose of the test is to validate core metadata schema as defined by the pydantic model where we are testing
    allowed value types for the funder attribute of the funding property.
    Note: This test does nat add a record to the database.
    """
    core_data = core_data
    core_model = core_model

    if funder_type == "organization":
        core_data["funding"] = [
            {
                "@type": "MonetaryGrant",
                "name": "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment",
                "url": "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329",
                "funder": {
                    "@type": "Organization",
                    "name": "National Science Foundation",
                    "identifier": ["https://ror.org/021nxhr62", "https://doi.org/10.13039/100000001"],
                },
            }
        ]
    else:
        core_data["funding"] = [
            {
                "@type": "MonetaryGrant",
                "name": "HDR Institute: Geospatial Understanding through an Integrative Discovery Environment",
                "url": "https://nsf.gov/awardsearch/showAward?AWD_ID=2118329",
                "funder": {"@type": "Person", "name": "John Doe", "email": "johnd@gmail.com"},
            }
        ]

    # validate the data model
    core_model_instance = await utils.validate_data_model(core_data, core_model)

    if funder_type == "organization":
        assert core_model_instance.funding[0].funder.type == "Organization"
        assert core_model_instance.funding[0].funder.name == "National Science Foundation"
        assert core_model_instance.funding[0].funder.identifier[0] == "https://ror.org/021nxhr62"
        assert core_model_instance.funding[0].funder.identifier[1] == "https://doi.org/10.13039/100000001"
    else:
        assert core_model_instance.funding[0].funder.type == "Person"
        assert core_model_instance.funding[0].funder.name == "John Doe"
        assert core_model_instance.funding[0].funder.email == "johnd@gmail.com"
