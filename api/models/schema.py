import re
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from .utils import parse_date


class SchemaBaseModel(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: dict[str, Any], model) -> None:
            # json schema modification for jsonforms
            for prop in schema.get('properties', {}).values():
                if 'const' in prop:
                    # hiding const/readonly fields from the form
                    prop['readonly'] = True
                    prop['option'] = {'hidden': True}
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
        const=True,
        default="CreativeWork",
        description="All records in the IGUIDE data catalog are considered creative works. Creative works can encompass various forms of content, such as datasets, software source code, digital documents, etc.",
    )
    name: str = Field(description="Record's title")


class PropertyValue(SchemaBaseModel):
    id: HttpUrl = Field(
        alias="@id",
        description="The unique identifier for the property value. For example, this can be an ORCID identifier for a person who created a creative work.",
    )
    type: str = Field(
        alias="@type",
        const=True,
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


Identifier = Union[str, HttpUrl, PropertyValue]


class Person(SchemaBaseModel):
    type: str = Field(
        alias="@type", const=True, default="Person", description="Describe the author(s) of a creative work"
    )
    name: str = Field(
        description="The name of individual who contributed to this creative work. Contribution can include being an author, editor, publisher, etc."
    )
    email: Optional[EmailStr] = Field(description="The email address of the individual who is listed as a contributor.")
    identifier: Optional[List[Union[HttpUrl, Identifier]]] = Field(description="The unique identifier for the person.")


class Organization(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        const=True,
        default="Organization",
        description="Describe the organization(s) contributed to a creative work",
    )
    name: str = Field(description="The organization name who contributed to this creative work.")
    url: Optional[HttpUrl] = Field(
        description="Indicates the URL associated with the organizatino who contributed to this work."
    )
    identifier: Optional[List[Union[HttpUrl, Identifier]]] = Field(
        description="The unique identifier for the organization."
    )
    address: Optional[str] = Field(
        description="The mailing address for the organization."
    )  # Should address be a string or another constrained type?


class ProviderID(SchemaBaseModel):
    id: HttpUrl = Field(
        alias="@id",
        description="The URL of a provider. For example, the URL to the HydroShare data repository that is considered as a provider for a creatiev work.",
    )


class ProviderOrganization(Organization):
    parentOrganization: Optional[Organization] = Field(
        description="The larger organization that the provider or publisher organization is a subOrganization of."
    )


class DefinedTerm(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DefinedTerm", description="TODO")
    name: str = Field(description="TODO")
    description: str = Field(description="TODO")


class KeywordTerm(DefinedTerm):
    inDefinedTermSet: HttpUrl = Field(description="TODO")


class HasPart(CreativeWork):
    description: str = Field(description="TODO")
    identifier: Identifier = Field(description="TODO")
    creator: Optional[Union[Person, Organization]] = Field(description="TODO")


class IsPartOf(HasPart):
    pass


class SubjectOf(CreativeWork):
    url: HttpUrl = Field(description="TODO")
    encodingFormat: str = Field(description="TODO")


class License(CreativeWork):
    url: HttpUrl = Field(description="TODO")


class LanguageEnum(str, Enum):
    eng = 'eng'
    esp = 'esp'


class Grant(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="MonetaryGrant", description="TODO")
    name: str = Field(description="TODO")
    url: HttpUrl = Field(description="TODO")
    funder: Union[Person, Organization] = Field(description="TODO")


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
        if not isinstance(v, str):
            raise TypeError('string required')

        v = v.strip()
        if not v:
            raise ValueError('empty string')
        try:
            start, end = v.split('/')
        except ValueError:
            raise ValueError('invalid date format')

        if parse_date(start) is None:
            raise ValueError('invalid date format')
        if end != "..":
            if parse_date(end) is None:
                raise ValueError('invalid date format')
        return v

    def __repr__(self):
        return f'TimeInterval({super().__repr__()})'


class GeoCoordinates(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="GeoCoordinates", description="TODO")
    latitude: float = Field(description="TODO")
    longitude: float = Field(description="TODO")

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
    type: str = Field(alias="@type", const=True, default="GeoShape", description="TODO")


class Line(GeoShape):
    line: str = Field(description="TODO")

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
    polygon: str = Field(description="TODO")

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
    type: str = Field(alias="@type", const=True, default="Place", description="TODO")
    name: Optional[str] = Field(description="TODO")
    address: Optional[str] = Field(description="TODO")
    geo: Optional[Union[Line, Polygon, GeoCoordinates]] = Field(description="TODO")


class MediaObject(SchemaBaseModel):
    type: str = Field(alias="@type", const=False, default="MediaObject", description="TODO")
    contentUrl: HttpUrl = Field(description="TODO")
    encodingFormat: str = Field(description="TODO")  # TODO enum for encoding formats
    contentSize: str = Field(description="TODO")
    name: str = Field(description="TODO")

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
    context: HttpUrl = Field(alias='@context', default='https://schema.org', description="TODO")
    type: str = Field(alias="@type", const=True, default="Dataset", description="TODO")
    name: str = Field(description="The name or title of the record.")
    description: str = Field(description="The description or abstract of the record.")
    url: HttpUrl = Field(description="The url of the record.")
    identifier: List[Identifier] = Field(description="Any kind of identifier for the record.")
    creator: List[Union[Person, Organization]] = Field(description="Person or organization that created the work.")
    dateCreated: Union[date, datetime] = Field(description="The date on which the work was created.")
    keywords: List[Union[str, HttpUrl, KeywordTerm]] = Field(
        min_items=1, description="Keywords or tags used to describe the dataset, delimited by commas."
    )
    license: Union[License, HttpUrl] = Field(
        description="A license document that applies to the content, typically indicated by a URL."
    )
    provider: Union[ProviderOrganization, Person, ProviderID] = Field(
        description="The service provider, service operator, or service performer."
    )
    publisher: Optional[Union[ProviderOrganization, Person, ProviderID]] = Field(
        description="The publisher of the record."
    )
    datePublished: Optional[Union[date, datetime]] = Field(description="Date of first publication for the record.")
    subjectOf: Optional[List[SubjectOf]] = Field(
        description="A CreativeWork about the record - e.g., a related metadata document describing the record.",
    )
    version: Optional[Union[float, str]] = Field(
        description="The version of the record."
    )  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, str]] = Field(description="The language of the content of the record.")
    creativeWorkStatus: Optional[Union[DefinedTerm, str]] = Field(
        description="The status of a creative work in terms of its stage in a lifecycle. Example terms include Incomplete, Draft, Published, Obsolete. Some organizations define a set of terms for the stages of their publication lifecycle.",
    )
    dateModified: Optional[Union[date, datetime]] = Field(
        description="The date on which the CreativeWork was most recently modified or updated."
    )
    funding: Optional[List[Grant]] = Field(
        description="A Grant that directly or indirectly provide funding or sponsorship for creation of the dataset.",
    )
    temporalCoverage: Optional[TimeInterval] = Field(
        description="The temporalCoverage of a CreativeWork indicates the period that the content applies to, i.e. that it describes, either as a DateTime or as a textual string indicating a time period in ISO 8601 time interval format.",
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
    type: str = Field(alias="@type", const=True, default="DataDownload", description="TODO")
    name: str = Field(description="TODO")
    contentUrl: Optional[HttpUrl] = Field(description="TODO")
    encodingFormat: Optional[List[str]] = Field(description="TODO")
    contentSize: Optional[str] = Field(description="TODO")
    comment: Optional[str] = Field(description="TODO")


class VariableMeasured(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="PropertyValue", description="TODO")
    name: str = Field(description="TODO")
    unitText: str = Field(description="TODO")


class IncludedInDataCatalog(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DataCatalog", description="TODO")
    name: str = Field(description="TODO")
    description: str = Field(description="TODO")
    url: HttpUrl = Field(description="TODO")
    identifier: Identifier = Field(description="TODO")
    creator: Union[Person, Organization] = Field(description="TODO")


class Dataset(SchemaBaseModel):
    distribution: List[Distribution] = Field(
        description="A data distribution in the form of a dataset (see https://schema.org/Dataset for more information).",
    )
    variableMeasured: Optional[List[Union[str, VariableMeasured]]] = Field(
        description="The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue.",
    )
    includedInDataCatalog: List[IncludedInDataCatalog] = Field(
        description="A data catalog which contains this dataset (this property was previously 'catalog', preferred name is now 'includedInDataCatalog').",
    )


class DatasetSchema(Dataset, CoreMetadata):
    # used only for generating the JSON-LD schema for a dataset.
    pass
