from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class VoiceActionBase(BaseModel):
    userId: str = Field(..., description="Unique session ID for the user")
    audioTranscript: str = Field(..., description="Transcribed banking action request")
    audioFileName: Optional[str] = Field(None, description="Optional audio file name")
    processed: bool = Field(default=False, description="Whether the action has been processed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the record was created")


class VoiceActionCreate(VoiceActionBase):
    pass


class VoiceActionInDB(VoiceActionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class VoiceActionResponse(BaseModel):
    id: str
    userId: str
    audioTranscript: str
    audioFileName: Optional[str]
    processed: bool
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }