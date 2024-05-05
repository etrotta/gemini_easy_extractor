import pydantic

from src.syo.tool_factory import novel_model


class Character(pydantic.BaseModel):
    """important Character present in the novel."""

    name: str = pydantic.Field(default="Unknown", description="This character's real name.")
    aliases: list[str] = pydantic.Field(
        default=[],
        description="Alternative names this character is called by, including nicknames and titles.",
    )
    long_description: str | None = pydantic.Field(
        default=None,
        description="A long description including all relevant details about this event."
    )
    description: str = pydantic.Field(
        description="A short description including the most important details about this character."
    )
    current_events: list[str] = pydantic.Field(
        default=[],
        description="Important events that this character is currently taking part of.",
    )
    notable_events: list[str] = pydantic.Field(
        default=[],
        description="Important events that this character have experienced in the past.",
    )
    allies: list[str] = pydantic.Field(
        default=[],
        description="Other characters this character have a positive relationship with.",
    )
    enemies: list[str] = pydantic.Field(
        default=[],
        description="Other characters this character have a negative relationship with.",
    )
    notable_effects: list[str] = pydantic.Field(
        default=[],
        description="Important effects that affect this character, which they may or may not have control over.",
    )
    notable_skills: list[str] = pydantic.Field(
        default=[], description="Important abilities this character possess and can actively use."
    )
    origin: str = pydantic.Field(default="Unknown", description="Where this character was born.")
    current_location: str = pydantic.Field(
        default="Unknown", description="Where this character is in currently."
    )
    notable_past_locations: list[str] = pydantic.Field(
        default=[],
        description="Important locations that make up part of this character's background.",
    )
    age: int | None = pydantic.Field(
        default=None, description="This character's real age in years."
    )


class Location(pydantic.BaseModel):
    """important Location present in the novel."""

    name: str = pydantic.Field(default="Unknown", description="This location's name.")
    aliases: list[str] = pydantic.Field(
        default=[],
        description="Alternative names this location is called by.",
    )
    description: str = pydantic.Field(
        description="A short description including the most important details about this location."
    )
    long_description: str | None = pydantic.Field(
        default=None,
        description="A long description including all relevant details about this event."
    )
    current_events: list[str] = pydantic.Field(
        default=[],
        description="Important events that are currently taking part in this location.",
    )
    notable_events: list[str] = pydantic.Field(
        default=[],
        description="Important events that have happened in this location in the past.",
    )
    notable_effects: list[str] = pydantic.Field(
        default=[],
        description="Important ways in which this location influences the world around it.",
    )
    origin: str = pydantic.Field(
        default="Unknown", description="How this location was found or created."
    )
    parent_location: str = pydantic.Field(
        default="Unknown", description="Where this location is contained in."
    )
    nearby_locations: list[str] = pydantic.Field(
        default=[],
        description="Other locations close to this.",
    )
    notable_characters: list[str] = pydantic.Field(
        default=[],
        description="Important characters that are currently in this location.",
    )
    notable_past_characters: list[str] = pydantic.Field(
        default=[],
        description="Important characters that make up part of this locations's history.",
    )
    age: int | None = pydantic.Field(
        default=None, description="How long this location has existed for."
    )


class Event(pydantic.BaseModel):
    """important Event present in the novel."""

    name: str | None = pydantic.Field(default=None, description="This event's name.")
    aliases: list[str] = pydantic.Field(
        default=[],
        description="Alternative names this event is called by.",
    )
    description: str = pydantic.Field(
        description="A short description including the most important details about this event."
    )
    long_description: str | None = pydantic.Field(
        default=None,
        description="A long description including all relevant details about this event."
    )
    connected_events: list[str] = pydantic.Field(
        default=[],
        description="Other important events that are connected to this event.",
    )
    notable_effects: list[str] = pydantic.Field(
        default=[],
        description="Important ways in which this Event is influencing the world around it.",
    )
    start_reason: str = pydantic.Field(
        default="Unknown", description="What caused this Event to start."
    )
    end_reason: str | None = pydantic.Field(
        default=None, description="What caused this Event to end, if it is over."
    )
    outcomes: list[str] = pydantic.Field(
        default=[],
        description="How have things changed because of this Event.",
    )
    notable_characters: list[str] = pydantic.Field(
        default=[],
        description="Important characters that are involved in this Event.",
    )
    notable_locations: list[str] = pydantic.Field(
        default=[],
        description="Important locations that are involved in this Event.",
    )


def register_common_models() -> list[type[pydantic.BaseModel]]:
    "Register common models for Tools and returns them as a list."
    return [
        novel_model(Character),
        novel_model(Location),
        novel_model(Event),
    ]
