import pydantic

from google.third_party_gemini_extensions.gemini_easy_extractor import FunctionGroup

group = FunctionGroup()

@group.register_model
class Character(pydantic.BaseModel):
    """important Character present in the story."""

    name: str | None = pydantic.Field(default=None, description="This character's real name.")
    description: str = pydantic.Field(
        description="A short description including the most important details about this character."
    )
    skills: list[str] = pydantic.Field(
        default=[], description="Important abilities this character possess, be it expert knowledge, passive effects or powers they can use at will."
    )
    origin: str | None = pydantic.Field(default=None, description="Where this character was born or raised.")
    current_location: str | None = pydantic.Field(
        default=None, description="Where this character is in currently."
    )
    age: int | None = pydantic.Field(
        default=None, description="This character's real age in years."
    )


@group.register_model
class Location(pydantic.BaseModel):
    """important Location present in the story."""

    name: str | None = pydantic.Field(default=None, description="This location's name.")
    description: str = pydantic.Field(
        description="A short description including the most important details about this location."
    )
    notable_effects: list[str] = pydantic.Field(
        default=[],
        description="Important ways in which this location influences the world around it.",
    )
    origin: str | None = pydantic.Field(
        default=None, description="How this location was found or created."
    )
    parent_location: str | None = pydantic.Field(
        default=None, description="Where this location is contained in."
    )


@group.register_model
class Event(pydantic.BaseModel):
    """important Event present in the story."""

    name: str | None = pydantic.Field(default=None, description="This event's name.")
    description: str = pydantic.Field(
        description="A short description detailing what happened in this event."
    )
    effects: list[str] = pydantic.Field(
        default=[],
        description="Important ways in which this Event affected the world around it.",
    )

