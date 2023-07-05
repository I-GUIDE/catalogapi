import re
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class SchemaBaseModel(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: dict[str, Any], model) -> None:
            # json schema modification for jsonforms
            for prop in schema.get('properties', {}).values():
                if 'format' in prop and prop['format'] == 'uri':
                    # using a regex for url matching
                    prop.pop('format')
                    prop[
                        'pattern'
                    ] = "^(http:\\/\\/www\\.|https:\\/\\/www\\.|http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$"
                    prop['errorMessage'] = {"pattern": "must match format \"url\""}


class CreativeWork(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="CreativeWork",
        description="Submission type can include various forms of content, such as datasets, software source code, digital documents, etc.",
    )
    name: str = Field(description="Submission's name or title", title="Name or Title")


class PropertyValue(SchemaBaseModel):
    id: HttpUrl = Field(
        alias="@id",
        description="Unique identifier for the property value. For example, this can be an ORCID identifier for a person who created a creative work.",
    )
    type: str = Field(
        alias="@type",
        default="PropertyValue",
        description="Specifies that the type of the structured data object is a PropertyValue.",
    )
    name: Optional[str] = Field(
        description="The name of the property that is related to a specific creative work. For example, DOI of a person who created the creatiev work or the varibale name that is measured for a research work."
    )
    propertyID: Optional[HttpUrl] = Field(
        description="Specifies the property ID. For example, this can be the ORCID registry identifier."
    )
    value: str = Field(
        description="Represents the actual value assigned to the property. For example,  the ORCID identifier: 0000-0000-0000-0001."
    )
    url: HttpUrl = Field(
        description="Indicates the URL associated with the property value. For example, the ORCID profile URL"
    )


class Person(SchemaBaseModel):
    type: str = Field(
        alias="@type", 
        default="Person", 
        description="DELETEME"
    )
    name: str = Field(
        description="A string containing the full name of the person. Personal name format: Family Name, Given Name"
    )
    email: Optional[EmailStr] = Field(description="A string containing an email address for the person")
    identifier: Optional[List[str]] = Field(description="Unique identifiers for the person. Where identifiers can be encoded as URLs, enter URLs here.")


class Organization(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="Organization",
        description="DELETEME",
    )
    name: str = Field(description="Name of the provider organization or repository.")
    url: Optional[HttpUrl] = Field(title="URL",
        description="A URL to the homepage for the organization."
    )
    identifier: Optional[List[str]] = Field(
        description="Unique identifiers for the person or organization. Where identifiers can be encoded as URLs, enter URLs here."
    )
    address: Optional[str] = Field(
        description="Full address for the organization - e.g., “8200 Old Main Hill, Logan, UT 84322-8200”."
    )  # Should address be a string or another constrained type?


class PublisherOrganization(Organization):
    name: str = Field(description="Name of the publishing organization.")


class DefinedTerm(SchemaBaseModel):
    type: str = Field(alias="@type", default="DefinedTerm", description="A formal definition of a word, name, acronym, phrase, or similar. Often used in the context of category or subject classification, glossaries or dictionaries, product or creative work types, etc.")
    name: str = Field(description="The name of the term or item being defined.")
    description: str = Field(description="The description of the item being defined.")


class KeywordTerm(DefinedTerm):
    inDefinedTermSet: HttpUrl = Field(description="Keywords or tags with a formal definition used to describe the creative work.")


class HasPart(CreativeWork):
    url: Optional[HttpUrl] = Field(title="URL", description="TODO")
    description: Optional[str] = Field(description="Information about a related resource that is part of this resource.")


class IsPartOf(CreativeWork):
    url: Optional[HttpUrl] = Field(title="URL", description="TODO")
    description: Optional[str] = Field(description="Information about a related resource that this resource is a part of - e.g., a related collection.")


class SubjectOf(CreativeWork):
    url: Optional[HttpUrl] = Field(title="URL", description="The URL address that serves as a reference to access additional details related to the record. It is important to note that this type of metadata solely pertains to the record itself and may not necessarily be an integral component of the record, unlike the HasPart metadata.")
    description: Optional[str] = Field(description="Information about a related resource that is about or describes this resource - e.g., a related metadata document describing the resource.")


class License(CreativeWork):
    name: str = Field(description="A text string indicating the name of the license under which the resource is shared.")
    url: Optional[HttpUrl] = Field(title="URL", description="A URL for a web page that describes the license.")
    description: Optional[str] = Field(description="A text string describing the license or containing the text of the license itself.")


class LanguageEnum(str, Enum):
    eng = 'eng'
    esp = 'esp'


class Grant(SchemaBaseModel):
    type: str = Field(alias="@type", default="MonetaryGrant", description="This metadata represents details about a grant or financial assistance provided to an individual(s) or organization(s) for supporting the work related to the record.")
    name: str = Field(title="Name or Title", description="A text string indicating the name or title of the grant or financial assistance.")
    description: Optional[str] = Field(description="A text string describing the grant or financial assistance.")
    identifier: Optional[str] = Field(title="Funding Identifier", description="Grant award number or other identifier.")
    funder: Optional[Union[Person, Organization]] = Field(description="A Grant or monetary assistance that directly or indirectly provided funding or sponsorship for creation of the resource.")


class TimeInterval(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        pass

    @classmethod
    def validate(cls, v):
        def parse_date(date_string):
            if len(date_string) == 10:
                parse_format = "%Y-%m-%d"
            elif len(date_string) == 7:
                parse_format = "%Y-%m"
            elif len(date_string) == 4:
                parse_format = "%Y"
            else:
                parse_format = "%Y-%m-%dT%H:%M:%S"
            try:
                datetime.strptime(date_string, parse_format)
            except ValueError:
                raise ValueError('invalid date format')

        if not isinstance(v, str):
            raise TypeError('string required')

        v = v.strip()
        if not v:
            raise ValueError('empty string')
        try:
            start, end = v.split('/')
        except ValueError:
            raise ValueError('invalid format')

        parse_date(start)
        if end != "..":
            parse_date(end)

        return v

    def __repr__(self):
        return f'TimeInterval({super().__repr__()})'


class GeoCoordinates(SchemaBaseModel):
    type: str = Field(alias="@type", default="GeoCoordinates", description="Geographic coordinates that represent a specific location on the Earth's surface. GeoCoordinates typically consists of two components: latitude and longitude.")
    latitude: float = Field(description="Represents the angular distance of a location north or south of the equator, measured in degrees and ranges from -90 to +90 degrees.")
    longitude: float = Field(description="Represents the angular distance of a location east or west of the Prime Meridian, measured in degrees and ranges from -180 to +180 degrees.")

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class GeoShape(SchemaBaseModel):
    type: str = Field(alias="@type", default="GeoShape", description="A structured representation that describes the coordinates of a geographic feature (line or polygon).")


class Line(GeoShape):
    line: str = Field(description="A line that is expressed as a series of two or more point objects separated by space.")

    @validator('line')
    def validate_line(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        v = v.strip()
        if not v:
            raise ValueError('empty string')
        v_parts = v.split(' ')
        if len(v_parts) < 2:
            raise ValueError('Line must have at least 2 points')
        for item in v_parts:
            try:
                item = float(item)
            except ValueError:
                raise ValueError('Line point is not a number')
            item = abs(item)
            if item > 180:
                raise ValueError('Line point must be between -180 and 180')
        return v


class Polygon(GeoShape):
    polygon: str = Field(description="A polygon outlines the boundary of a specific region by a point-to-point path for which the starting and ending points are the same.")

    @validator('polygon')
    def validate_polygon(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        v = v.strip()
        if not v:
            raise ValueError('empty string')
        v_parts = v.split(' ')
        if len(v_parts) < 3:
            raise ValueError('Polygon must have at least 3 points')
        for item in v_parts:
            try:
                item = float(item)
            except ValueError:
                raise ValueError('Polygon point is not a number')
            item = abs(item)
            if item > 180:
                raise ValueError('Polygon point must be between -180 and 180')
        return v


class Place(SchemaBaseModel):
    type: str = Field(alias="@type", default="Place", description="Represents the focus area of the record's content.")
    name: Optional[str] = Field(description="The name of the focus area of the record's content.")
    address: Optional[str] = Field(description="The address of the focus area.")
    geo: Optional[Union[Line, Polygon, GeoCoordinates]] = Field(description="Specifies the geographic coordinates of the place in the form of a point location, line, or area coverage extent.")


class MediaObject(SchemaBaseModel):
    type: str = Field(alias="@type", default="MediaObject", description="An item that encodes the record.")
    contentUrl: HttpUrl = Field(description="The direct URL link to access or download the actual content of the media object.")
    encodingFormat: str = Field(description="Represents the specific file format in which the media is encoded.")  # TODO enum for encoding formats
    contentSize: str = Field(description="Represents the file size, expressed in bytes, kilobytes, megabytes, or another unit of measurement.")
    name: str = Field(description="The name of the media object (file).")

    @validator('contentSize')
    def validate_content_size(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('empty string')

        match = re.match(r"([0-9.]+)([a-zA-Z]+$)", v.replace(" ", ""))
        if not match:
            raise ValueError('invalid format')

        size_unit = match.group(2)
        if size_unit.upper() not in [
            'KB',
            'MB',
            'GB',
            'TB',
            'PB',
            'KILOBYTES',
            'MEGABYTES',
            'GIGABYTES',
            'TERABYTES',
            'PETABYTES',
        ]:
            raise ValueError('invalid unit')

        return v


class CoreMetadata(SchemaBaseModel):
    context: HttpUrl = Field(alias='@context', default='https://schema.org', description="Specifies the vocabulary employed for understanding the structured data markup.")
    type: str = Field(alias="@type", title="Submission Type", default="Dataset", 
                      description="Submission type can include various forms of content, such as datasets, software source code, digital documents, etc.", 
                      enum=["Dataset", "Notebook", "Software Source Code"])
    name: str = Field(title="Name or Title", description="A text string with a descriptive name or title for the resource.")
    description: str = Field(title="Description or Abstract", description="A text string containing a description/abstract for the resource.")
    url: HttpUrl = Field(title="URL", description="A URL for the landing page that describes the resource and where the content of the resource can be accessed. If there is no landing page, provide the URL of the content.")
    identifier: List[str] = Field(title="Identifiers", description="Any kind of identifier for the resource. Multiple identifiers can be entered. Where identifiers can be encoded as URLs, enter URLs here.")
    creator: List[Union[Person, Organization]] = Field(description="Person or organization that created the work.")
    dateCreated: datetime = Field(title="Date Created", description="The date on which the work was created.")
    keywords: List[str] = Field(
        min_items=1, description="Keywords or tags used to describe the dataset, delimited by commas."
    )
    license: License = Field(
        description="A license document that applies to the content, typically indicated by a URL."
    )
    provider: Union[Organization, Person] = Field(
        description="The repository, service provider, organization, person, or service performer that provides access to the resource."
    )
    publisher: Optional[PublisherOrganization] = Field(
        title="Publisher",
        description="The publisher of the record."
    )
    datePublished: Optional[datetime] = Field(title="Date Published", description="Date of first publication for the record.")
    subjectOf: Optional[List[SubjectOf]] = Field(
        description="A CreativeWork about the record - e.g., a related metadata document describing the record.",
    )
    version: Optional[str] = Field(
        description="A text string indicating the version of the resource."
    )  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, str]] = Field(title="Language", description="The language of the content of the resource.")
    # TODO: find a way to modify fields inside Unions so we can add titles, descriptions, options, etc.
    creativeWorkStatus: Optional[Union[DefinedTerm, str]] = Field(
        title="Resource Status",
        description="The status of this resource in terms of its stage in a lifecycle. Example terms include Incomplete, Draft, Published, and Obsolete.",
    )
    dateModified: Optional[datetime] = Field(
        title="Date Modified",
        description="The date on which the CreativeWork was most recently modified or updated."
    )
    funding: Optional[List[Grant]] = Field(
        description="A Grant that directly or indirectly provide funding or sponsorship for creation of the dataset.",
    )
    temporalCoverage: Optional[TimeInterval] = Field(
        description="The time period that the resource content applies to.",
    )
    spatialCoverage: Optional[Place] = Field(
        description="The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. It is a subproperty of contentLocation intended primarily for more technical and detailed materials. For example with a Dataset, it indicates areas that the dataset describes: a dataset of New York weather would have spatialCoverage which was the place: the state of New York.",
    )
    hasPart: Optional[List[HasPart]] = Field(
        description="Indicates an record or CreativeWork that is part of this record."
    )
    isPartOf: Optional[List[IsPartOf]] = Field(
        description="Indicates an record or CreativeWork that this record, or CreativeWork (in some sense), is part of.",
    )
    associatedMedia: Optional[List[MediaObject]] = Field(
        description="A media object that encodes this CreativeWork. This property is a synonym for encoding.",
    )


class Distribution(SchemaBaseModel):
    type: str = Field(alias="@type", default="DataDownload", description="A downloadable form of the resource, at a specific location, in a specific format. Repeat if multiple files or if different formats/variations are available.")
    name: Optional[str] = Field(description="A text string indicating the name of the content to be downloaded. This could be a file name or a descriptive name for the content file.")
    contentUrl: HttpUrl = Field(title="Content URL", description="A URL for the content to be downloaded.")
    encodingFormat: Optional[str] = Field(description="Text string indicating the file or media type, usually expressed using a MIME format.")
    contentSize: Optional[str] = Field(description="A text string indicating the file size in megabytes")
    comment: Optional[str] = Field(description="A text string with comments about the resource. For example, an explanation that provides additional information on how the dataset is being accessed or downloaded.")


class VariableMeasured(SchemaBaseModel):
    type: str = Field(alias="@type", default="PropertyValue", description="Indicates specific information about the variable being measured in a particular dataset, study, or observation.")
    name: str = Field(description="The name of the variable being measured.")
    unitText: str = Field(description="Indicate the unit of measurement for the variable.")


class IncludedInDataCatalog(SchemaBaseModel):
    type: str = Field(alias="@type", default="DataCatalog", description="A data catalog which contains this dataset.")
    name: str = Field(description="The name of the data catalog containing this dataset.")
    description: str = Field(description="The description of the data catalog.")
    url: HttpUrl = Field(description="The URL address to the data catalog.")
    identifier: str = Field(description="The unique identifier for the data catalog. This is generated automatically by the system.")
    creator: Union[Person, Organization] = Field(description="The creator, owner, or provider of the data catalog.")


class Dataset(SchemaBaseModel):
    distribution: List[Distribution] = Field(
        description="A downloadable form of the resource, at a specific location, in a specific format. Repeat if multiple files or if different formats/variations are available.",
    )
    variableMeasured: Optional[List[str]] = Field(
        title="Variable Measured",
        description="The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue.",
    )
    includedInDataCatalog: Optional[List[IncludedInDataCatalog]] = Field(
        description="Any other data catalog that contains a description of this resource.",
    )


class DatasetSchema(Dataset, CoreMetadata):
    # used only for generating the JSON-LD schema for a dataset.
    pass
