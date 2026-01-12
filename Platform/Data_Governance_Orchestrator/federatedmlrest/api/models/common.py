from enum import Enum
from typing import TypedDict, Union, Optional, Any
from uuid import UUID, uuid4

import pydantic
from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import CoreSchema, core_schema

class PyUUID(UUID):
    """MongoDBs PyUUID pydantic representation."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type[Any], handler: GetCoreSchemaHandler) -> CoreSchema:
        """Get Validators."""
        return core_schema.general_plain_validator_function(function=cls.validate)

    # @classmethod
    # def __get_pydantic_core_schema__(cls):
    #     """Get Validators."""
    #     yield cls.validate

    @classmethod
    def validate(cls, v: Union[str, UUID], info: core_schema.ValidationInfo) -> Any:
        """Validate this object."""
        return cls(str(v))

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        """Modify schema so that this class is represented as string."""
        field_schema.update(type="string")


class BaseModelNoExtra(pydantic.BaseModel):
    """Don't allow additional fields."""

    class Config:
        """Pydantic config."""

        extra = pydantic.Extra.forbid


class BaseBsonModel(BaseModelNoExtra):
    """Base for models with UUID's to now specifiy a custom json encoder everytime."""

    class Config:
        """Pydantic config."""

        json_encoders = {UUID: str}


class MongoQueryNoVersion(TypedDict):
    """Simple dict that can be used to query mongo objects."""

    _id: UUID  # For database level compatibility keep uuid (pyuuid only as validation for python typing)
    _deleted: Optional[bool]


class MongoID(BaseBsonModel):
    """Base for models that have an ID."""

    id: PyUUID | UUID = pydantic.Field(default_factory=uuid4, alias="_id")
    deleted: bool = pydantic.Field(default=False, alias="_deleted")

    def mongo_query(self) -> MongoQueryNoVersion:
        """Create a query to get this objects from the mongodb."""
        if not self.id:
            raise ValueError("id is not defined")

        return MongoQueryNoVersion(_id=self.id)

    @staticmethod
    def id_to_mongo_query(uuid: UUID) -> MongoQueryNoVersion:
        """Create an id-dict to query to object."""
        return MongoQueryNoVersion(_id=uuid)


class MongoQueryWithVersion(TypedDict):
    _governance_id: UUID  # For database level compatibility keep uuid (pyuuid only as validation for python typing)
    _version: Optional[int]
    _current: Optional[bool]
    _deleted: Optional[bool]


class MongoIDAndVersion(BaseBsonModel):
    """Base for models that have an ID."""
    id: PyUUID | UUID = pydantic.Field(default_factory=uuid4, alias="_id")
    governance_id: PyUUID | UUID = pydantic.Field(default_factory=uuid4, alias="_governance_id")
    version: int = pydantic.Field(default=1, alias="_version")
    current: bool = pydantic.Field(default=True, alias="_current")
    deleted: bool = pydantic.Field(default=False, alias="_deleted")

    def mongo_query(self) -> MongoQueryWithVersion:
        """Create a query to get this objects from the mongodb."""
        if not self.governance_id:
            raise ValueError("id is not defined")

        if self.version == -1:
            return MongoQueryWithVersion(_governance_id=self.governance_id,
                                         _current=True)

        elif not self.current:
            return MongoQueryWithVersion(_governance_id=self.governance_id,
                                         _version=self.version)

    def is_deleted(self):
        return self.deleted

    @staticmethod
    def get_current_document(governance_id: UUID):
        return MongoQueryWithVersion(_governance_id=governance_id, _current=True)

    @staticmethod
    def get_version_document(governance_id: UUID, version: int) -> MongoQueryWithVersion:
        """Create an id-dict to query to object."""
        return MongoQueryWithVersion(_governance_id=governance_id, _version=version)

    @staticmethod
    def id_to_mongo_query(uuid: UUID) -> MongoQueryNoVersion:
        """Create an id-dict to query to object."""
        return MongoQueryNoVersion(_id=uuid)



class Status(str, Enum):
    """Status values."""

    PROPOSED: str = "PROPOSED"
    ACCEPTED: str = "ACCEPTED"
    REJECTED: str = "REJECTED"
    OBSOLETE: str = "OBSOLETE"


class WithStatus(BaseModelNoExtra):
    """Base model for objects with status."""

    status: Status = Status.PROPOSED


# MongoDB only accepts 8byte integers
# class EightByteInt(pydantic.ConstrainedInt):
#     """Restricted Integers to a max length of 8 bytes."""
#
#     lt = 2 ** 63
#     gt = -(2 * 63) + 1


# TODO: Add decimals to mongo.
# class Decimal(pydantic.ConstrainedFloat):
#     """Restricted Integers to a max length of 8 bytes."""
#
#     lt = 2 ** 63
#     gt = -(2 * 63) + 1
