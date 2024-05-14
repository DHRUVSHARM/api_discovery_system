from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Optional, List
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator


PyObjectId = Annotated[str, BeforeValidator(str)]


class APIModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    summary: Optional[str]
    rating: Optional[float]
    name: str
    label: Optional[str]
    author: Optional[str]
    description: Optional[str]
    type: Optional[int]
    downloads: Optional[int]  # If it should accept integers
    useCount: Optional[str]
    sampleUrl: Optional[str]
    downloadUrl: Optional[str]
    dateModified: Optional[str]
    remoteFeed: Optional[str]
    numComments: Optional[str]
    commentsUrl: Optional[str]
    tags: List[str] = []
    category: Optional[str]
    protocols: Optional[str]
    serviceEndpoint: Optional[str]
    version: Optional[str]
    wsdl: Optional[str]
    dataFormats: Optional[str]
    apiGroups: Optional[str]
    example: Optional[str]
    clientInstall: Optional[str]
    authentication: Optional[str]
    ssl: Optional[str]
    readonly: Optional[str]
    vendorApiKits: Optional[str]
    communityApiKits: Optional[str]
    blog: Optional[str]
    forum: Optional[str]
    support: Optional[str]
    accountReq: Optional[str]
    commercial: Optional[str]
    provider: Optional[str]
    managedBy: Optional[str]
    nonCommercial: Optional[str]
    dataLicensing: Optional[str]
    fees: Optional[str]
    limits: Optional[str]
    terms: Optional[str]
    company: Optional[str]
    updated: Optional[str]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class APIUsed(BaseModel):
    name: str
    url: str


class MashupModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    summary: Optional[str]
    author: Optional[str]
    description: Optional[str]
    type: Optional[str]
    downloads: Optional[int]  # If it should accept integers
    useCount: Optional[int]
    sampleUrl: Optional[str]
    dateModified: Optional[str]
    numComments: Optional[int]
    commentsUrl: Optional[str]
    tags: List[str] = []
    apis: List[APIUsed] = []
    updated: Optional[str]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
