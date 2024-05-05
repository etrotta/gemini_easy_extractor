import re
import typing
import google.ai.generativelanguage as glm
import pydantic
from pydantic.fields import FieldInfo

registered_models: dict[str, typing.Type[pydantic.BaseModel]] = {}  # Model Name => Model
declared_functions: dict[str, list[glm.FunctionDeclaration]] = {}  # Model Name => Function


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
    """Register the Model and declare Tool functions to manage instances of it."""
    snake_case_name = '_'.join(re.findall(r"([A-Z][a-z0-9\_]+)", model.__name__)).lower()

    registered_models[model.__name__] = model
    # registered_models[snake_case_name] = model

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
        ("register_{}", "Register a new"),
        # ("update_{}", "Updates information about an existing"),
        # ("start_{}_event", "Add information about a new event related to a"),
        # ("update_{}_event", "Updates information about an ongoing event related to a"),
    ]
    functions = {
        model.__name__: [glm.FunctionDeclaration(
            name=function_name.format(snake_case_name),
            description=f"{function_description} {model.__doc__}",
            parameters=model_schema,
        )
        for function_name, function_description in base_functions]
    }
    declared_functions.update(functions)
    return model

def clear_models_and_functions() -> None:
    "Unregister all models and functions previously declared by `novel_model`"
    registered_models.clear()
    declared_functions.clear()

def collect_models() -> dict[str, typing.Type[pydantic.BaseModel]]:
    "Lists all models registered as `@novel_model`s"
    return registered_models.copy()

def collect_tools(model_name: str | None = None) -> glm.Tool:
    "Collects functions declared by `@novel_model`, optionally filtering by the relevant model"
    if model_name:
        functions = declared_functions[model_name]
    else:
        functions = [func for sublist in declared_functions.values() for func in sublist]
    return glm.Tool(function_declarations=functions)

def get_model_from_function_name(function_name: str) -> typing.Type[pydantic.BaseModel]:
    owners = {function.name: owner for owner, functions in declared_functions.items() for function in functions}
    return registered_models[owners[function_name]]
