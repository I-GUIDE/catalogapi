from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from beanie import Document, Link, PydanticObjectId

from api.models.schema import HttpUrlStr

if TYPE_CHECKING:
    # this avoids circular imports
    from api.adapters.utils import RepositoryType


class Submission(Document):
    title: str = None
    authors: List[str] = []
    identifier: PydanticObjectId
    submitted: datetime = datetime.utcnow()
    url: HttpUrlStr = None
    repository: Optional[str] = None
    repository_identifier: Optional[str] = None


class User(Document):
    access_token: str
    orcid: str
    preferred_username: Optional[str] = None
    submissions: List[Link[Submission]] = []

    def submission(self, identifier: PydanticObjectId) -> Submission:
        return next(filter(lambda submission: submission.identifier == identifier, self.submissions), None)

    def submission_by_repository(self, repo_type: 'RepositoryType', identifier: str) -> Submission:
        return next(
            filter(
                lambda submission: submission.repository_identifier == identifier
                and submission.repository == repo_type,
                self.submissions,
            ),
            None,
        )
