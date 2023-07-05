import abc
import enum
from datetime import datetime
from typing import List, Optional, Union

import requests
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, HttpUrl

from api.config import Settings, get_settings
from api.models import schema
from api.models.catalog import DatasetMetadataDOC


class RepositoryType(str, enum.Enum):
    HYDROSHARE = "hydroshare"


class RepositoryRequestHandler(abc.ABC):
    settings: Settings = get_settings()

    @abc.abstractmethod
    async def get_metadata(self, record_id: str):
        ...

    @staticmethod
    def get_handler(repository: RepositoryType):
        if repository == RepositoryType.HYDROSHARE:
            return _HydroshareRequestHandler()
        else:
            raise HTTPException(status_code=400, detail=f"Repository {repository} is not supported")


class _HydroshareRequestHandler(RepositoryRequestHandler):

    async def get_metadata(self, record_id: str):
        hs_meta_url = self.settings.hydroshare_meta_read_url % record_id
        hs_file_url = self.settings.hydroshare_file_read_url % record_id

        def make_request(url, file_list=False):
            response = requests.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            if not file_list:
                return response.json()

            content_files = []
            content_files.extend(response.json()["results"])
            # check if there are more results to fetch - by default, 100 files are returned from HydroShare
            while response.json()["next"]:
                response = requests.get(response.json()["next"])
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                content_files.extend(response.json()["results"])
            return content_files

        metadata = make_request(hs_meta_url)
        files_metadata = make_request(hs_file_url, file_list=True)
        metadata["content_files"] = files_metadata
        return metadata


class HydroshareResourceMetadata(BaseModel):

    class Creator(BaseModel):
        name: Optional[str]
        email: Optional[EmailStr]
        organization: Optional[str]
        homepage: Optional[HttpUrl]
        address: Optional[str]
        identifiers: Optional[dict] = {}

        def to_dataset_creator(self):
            if self.name:
                creator = schema.Person(name=self.name)
                if self.email:
                    creator.email = self.email
            else:
                creator = schema.Organization(name=self.organization)
                if self.homepage:
                    creator.url = self.homepage
                if self.address:
                    creator.address = self.address
            creator.identifier = []
            for _, v in self.identifiers.items():
                creator.identifier.append(v)
            return creator

    class Award(BaseModel):
        funding_agency_name: str
        title: Optional[str]
        number: Optional[str]
        funding_agency_url: Optional[HttpUrl]

        def to_dataset_grant(self):
            if self.title:
                grant = schema.Grant(name=self.title)
            else:
                grant = schema.Grant(name=self.funding_agency_name)
            if self.number:
                grant.identifier = self.number
            funder = schema.Organization(name=self.funding_agency_name)
            if self.funding_agency_url:
                funder.url = self.funding_agency_url
            grant.funder = funder
            return grant

    class TemporalCoverage(BaseModel):
        start: str
        end: str

        def to_dataset_temporal_coverage(self):
            return f"{self.start}/{self.end}"

    class SpatialCoverageBox(BaseModel):
        name: Optional[str]
        northlimit: float
        eastlimit: float
        southlimit: float
        westlimit: float

        def to_dataset_spatial_coverage(self):
            place = schema.Place.construct()
            if self.name:
                place.name = self.name
            place.geo = schema.Polygon.construct()
            place.geo.polygon = f"{self.northlimit} {self.eastlimit} {self.southlimit} {self.westlimit}"
            return place

    class SpatialCoveragePoint(BaseModel):
        name: Optional[str]
        north: float
        east: float

        def to_dataset_spatial_coverage(self):
            place = schema.Place.construct()
            if self.name:
                place.name = self.name
            place.geo = schema.GeoCoordinates.construct()
            place.geo.latitude = self.north
            place.geo.longitude = self.east
            return place

    class ContentFile(BaseModel):
        file_name: str
        url: HttpUrl
        size: int
        content_type: str
        logical_file_type: str
        modified_time: datetime
        checksum: str

        def to_dataset_media_object(self):
            media_object = schema.MediaObject.construct()
            media_object.contentUrl = self.url
            media_object.encodingFormat = self.content_type
            media_object.contentSize = f"{self.size/1000.00} KB"
            media_object.name = self.file_name
            return media_object

    class Relation(BaseModel):
        type: str
        value: str

        def to_dataset_part_relation(self, relation_type: str):
            relation = None
            if relation_type == "IsPartOf" and self.type.endswith("is part of"):
                relation = schema.IsPartOf.construct()
            elif relation_type == "HasPart" and self.type.endswith("resource includes"):
                relation = schema.HasPart.construct()
            else:
                return relation

            description, url = self.value.rsplit(',', 1)
            relation.description = description.strip()
            relation.url = url.strip()
            relation.name = self.value
            return relation

    class Rights(BaseModel):
        statement: str
        url: HttpUrl

        def to_dataset_license(self):
            _license = schema.License.construct()
            _license.name = self.statement
            _license.url = self.url
            return _license

    title: str
    abstract: str
    url: HttpUrl
    identifier: HttpUrl
    creators: List[Creator]
    created: datetime
    modified: datetime
    subjects: Optional[List[str]]
    language: str
    rights: Rights
    awards: Optional[List[Award]]
    spatial_coverage: Optional[Union[SpatialCoverageBox, SpatialCoveragePoint]]
    period_coverage: Optional[TemporalCoverage]
    relations: Optional[List[Relation]]
    content_files: Optional[List[ContentFile]]

    def to_dataset_creators(self):
        creators = []
        for creator in self.creators:
            creators.append(creator.to_dataset_creator())
        return creators

    def to_dataset_grants(self):
        grants = []
        for award in self.awards:
            grants.append(award.to_dataset_grant())
        return grants

    def to_dataset_media_objects(self):
        media_objects = []
        for content_file in self.content_files:
            media_objects.append(content_file.to_dataset_media_object())
        return media_objects

    def to_dataset_part_relations(self, relation_type: str):
        part_relations = []
        for relation in self.relations:
            part_relation = relation.to_dataset_part_relation(relation_type)
            if part_relation:
                part_relations.append(part_relation)
        return part_relations

    def to_dataset_distributions(self):
        distributions = []
        distribution = schema.Distribution.construct()
        distribution.name = f"{self.url.split('/')[-1]}.zip"
        distribution.contentUrl = self.url
        distribution.encodingFormat = "application/zip"
        distribution.comment = "The HydroShare Resource Landing Page contains instructions for downloading the dataset"
        distributions.append(distribution)
        return distributions

    def to_catalog_dataset(self):
        dataset = DatasetMetadataDOC.construct()
        dataset.provider = schema.Organization.construct()
        dataset.provider.name = "Hydroshare"
        dataset.provider.url = "https://www.hydroshare.org/"
        dataset.name = self.title
        dataset.description = self.abstract
        dataset.url = self.url
        dataset.identifier = [self.identifier]
        dataset.creator = self.to_dataset_creators()
        dataset.dateCreated = self.created
        dataset.dateModified = self.modified
        dataset.keywords = self.subjects if self.subjects else ["HydroShare"]
        dataset.inLanguage = self.language
        dataset.funding = self.to_dataset_grants()
        if self.spatial_coverage:
            dataset.spatialCoverage = self.spatial_coverage.to_dataset_spatial_coverage()
        if self.period_coverage:
            dataset.temporalCoverage = self.period_coverage.to_dataset_temporal_coverage()
        dataset.associatedMedia = self.to_dataset_media_objects()
        dataset.isPartOf = self.to_dataset_part_relations("IsPartOf")
        dataset.hasPart = self.to_dataset_part_relations("HasPart")
        dataset.license = self.rights.to_dataset_license()
        dataset.distribution = self.to_dataset_distributions()
        return dataset


class RepositoryMetadataAdapter(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def to_catalog_record(metadata: dict) -> DatasetMetadataDOC:
        """Converts repository metadata to a catalog dataset record"""
        ...

    @staticmethod
    @abc.abstractmethod
    def to_repository_record(catalog_record: DatasetMetadataDOC):
        """Converts dataset catalog dataset record to repository metadata"""
        ...

    @staticmethod
    def get_adapter(repository: RepositoryType):
        """Returns the metadata adapter for the specified repository"""
        if repository == RepositoryType.HYDROSHARE:
            return HydroshareMetadataAdapter
        else:
            raise ValueError(f"Repository {repository} is not supported")


class HydroshareMetadataAdapter(RepositoryMetadataAdapter):

    @staticmethod
    def to_catalog_record(metadata: dict) -> DatasetMetadataDOC:
        """Converts hydroshare resource metadata to a catalog dataset record"""
        hs_metadata_model = HydroshareResourceMetadata(**metadata)
        return hs_metadata_model.to_catalog_dataset()

    @staticmethod
    def to_repository_record(catalog_record: DatasetMetadataDOC):
        """Converts dataset catalog record to hydroshare resource metadata"""
        raise NotImplementedError
