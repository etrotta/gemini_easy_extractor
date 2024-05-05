import re
import typing
import google.ai.generativelanguage as glm
import pydantic
from pydantic.fields import FieldInfo

registered_models: dict[str, typing.Type[pydantic.BaseModel]] = {}  # Model Name => Model
declared_functions: list[glm.FunctionDeclaration] = []  # All Functions
_function_owners: dict[str, typing.Type[pydantic.BaseModel]] = {}  # Function name => Model


class SchemaConfig(typing.TypedDict):
    description: str
    nullable: bool


def _format_type(annotation: type, **kwargs: typing.Unpack[SchemaConfig]) -> glm.Schema:
    # Surely there is a better way of doing this right?...
    # like a built in function? or even this not being required at all?
    mapping = {
        str: glm.Schema(type=glm.Type.STRING, **kwargs),
        int: glm.Schema(type=glm.Type.INTEGER, **kwargs),
        list[str]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.STRING), **kwargs),
        list[int]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.INTEGER), **kwargs),
    }
    return mapping[annotation]


def format_parameter(field: FieldInfo) -> glm.Schema:
    assert field.annotation is not None, f"Field {field} missing annotation"
    assert field.description is not None, f"Field {field} missing description"
    _optional_mappings = {(ann | None): ann for ann in (str, int, list[str], list[int])}
    annotation = field.annotation
    nullable = annotation in _optional_mappings
    if nullable:
        annotation = _optional_mappings[annotation]
    config = SchemaConfig(description=field.description, nullable=nullable)
    return _format_type(annotation, **config)


def novel_model[ModelType: typing.Type[pydantic.BaseModel]](model: ModelType) -> ModelType:
    """Register the model and declare glm Tool Functions to manage instances of it."""
    snake_case_name = '_'.join(re.findall(r"([A-Z][a-z0-9\_]+)", model.__name__)).lower()

    registered_models[model.__name__] = model
    registered_models[snake_case_name] = model

    parameters: dict[str, glm.Schema] = {}
    required: list[str] = []
    for key, field in model.model_fields.items():
        parameters[key] = format_parameter(field)
        if field.is_required():
            required.append(key)

    model_schema = glm.Schema(
        type=glm.Type.OBJECT,
        nullable=False,
        properties=parameters,
        required=required,
    )
    base_functions = [
        ("register", "Register a new "),
        ("update", "Add new information about an existing"),
    ]
    functions = [
        glm.FunctionDeclaration(
            name=f"{function_prefix}_{snake_case_name}",
            description=f"{function_description} {model.__doc__}",
            parameters=model_schema,
        )
        for function_prefix, function_description in base_functions
    ]
    declared_functions.extend(functions)
    for function in functions:
        _function_owners[function.name] = model
    return model

def clear_models_and_functions() -> None:
    "Unregister all models and functions previously declared by `novel_model`"
    registered_models.clear()
    declared_functions.clear()

def collect_models() -> dict[str, typing.Type[pydantic.BaseModel]]:
    "Lists all models registered as `@novel_model`s"
    return registered_models.copy()

def collect_tools() -> glm.Tool:
    "Collects all function declared by `@novel_model`s"
    return glm.Tool(function_declarations=declared_functions.copy())

def get_model_from_function_name(function_name: str) -> typing.Type[pydantic.BaseModel]:
    return _function_owners[function_name]

@novel_model
class NovelCharacter(pydantic.BaseModel):
    """important Character present in the novel."""
    name: str = pydantic.Field(default="Unknown", description="This character's real name.")
    aliases: list[str] = pydantic.Field(
        default=[],
        description="Alternative names this character is called by, including nicknames and titles.",
    )
    description: str = pydantic.Field(
        description="A short description including the most important details about this character."
    )
    notable_events: list[str] = pydantic.Field(
        default=[],
        description="Important events this character has experienced.",
    )
    notable_skills: list[str] = pydantic.Field(
        default=[], description="Important abilities this character possess."
    )
    origin: str = pydantic.Field(default="Unknown", description="Where this character was born.")
    notable_past_locations: list[str] = pydantic.Field(
        default=[],
        description="Important locations that make up part of this character's background.",
    )
    age: int | None = pydantic.Field(default=None, description="This character's real age in years.")



# calculator = glm.Tool(
#     function_declarations=[
#       glm.FunctionDeclaration(
#         name='multiply',
#         description="Returns the product of two numbers.",
#         parameters=glm.Schema(
#             type=glm.Type.OBJECT,
#             properties={
#                 'a':glm.Schema(type=glm.Type.NUMBER),
#                 'b':glm.Schema(type=glm.Type.NUMBER)
#             },
#             required=['a','b']
#         )
#       )
#     ])

