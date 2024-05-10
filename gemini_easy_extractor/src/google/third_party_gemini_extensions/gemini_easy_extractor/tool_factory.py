import re
import typing
import google.ai.generativelanguage as glm
import pydantic
from pydantic.fields import FieldInfo

class FunctionTemplate(pydantic.BaseModel):
    name: str
    description_prefix: str

type DataModel = typing.Type[pydantic.BaseModel]

class FunctionGroup:
    _models: dict[str, DataModel]
    _schemas: dict[str, glm.Schema]
    _functions: list[FunctionTemplate]

    def __init__(
            self,
            models: list[DataModel] | dict[str, DataModel] | None = None,
            functions: dict[str, str] | list[FunctionTemplate] | None = None,
        ):
        """Creates a Group of Data Models and Gemini Functions"""
        self._models = {}
        self._schemas = {}
        match models:
            case list():
                for model in models:
                    self.register_model(model)
            case dict():
                for key, model in models.items():
                    self.register_model(model)
                    self._models[key] = self._models[_snake_case(key)]
            case None:
                pass
            case _:
                raise TypeError(f"Invalid argument for models: {models}, expected list of pydantic models")
        match functions:
            case list():
                self._functions = functions.copy()
            case dict():
                self._functions = [FunctionTemplate(name=name, description_prefix=desc) for name, desc in functions.items()]
            case None:
                self._functions = []
            case _:
                raise TypeError(f"Invalid argument for models: {models}, expected a dictionary of {{'name': 'description'}}")

    def register_model[ModelType: DataModel](self, model: ModelType) -> ModelType:
        """Registers a Data Model as part of this FunctionGroup."""
        # V Not just me liking Python ; Google recommend snake case themselves for gemini functions
        snake_case_name = _snake_case(model.__name__)
        if snake_case_name in self._models:
            raise Exception(f"There already exists a model registered as {snake_case_name}")
        self._models[snake_case_name] = model

        parameters: dict[str, glm.Schema] = {}
        required: list[str] = []
        for key, field in model.model_fields.items():
            parameters[key] = _format_parameter(field)
            if field.is_required():
                required.append(key)

        model_schema = glm.Schema(
            type=glm.Type.OBJECT,
            nullable=False,
            properties=parameters,
            required=required,
        )
        self._schemas[snake_case_name] = model_schema
        return model

    def create_function(self, name: str, description: str) -> FunctionTemplate:
        """Creates, register and returns a new Function Template"""

        assert "{" in name, "The function name must contain a {} placeholder for the name of the model that will be inserted"

        if name in (func.name for func in self._functions):
            raise Exception(f"There already exists a function registered as {name}")
        function = FunctionTemplate(name=name, description_prefix=description)
        return self.register_function(function)

    def register_function[Function: FunctionTemplate](self, function: Function) -> Function:
        """Registers a Function Template as part of this FunctionGroup"""
        self._functions.append(function)
        return function

    def clear_models_and_functions(self) -> None:
        "Unregister all models and functions from this group"
        self._models.clear()
        self._schemas.clear()
        self._functions.clear()

    def has_models_and_functions(self) -> bool:
        "Checks whenever this FunctionGroup has at least one Model and one Function registered"
        return bool(self._models) and bool(self._functions)

    def collect_models(self) -> dict[str, typing.Type[pydantic.BaseModel]]:
        "Lists all registered models"
        return self._models.copy()

    def collect_tools(self, filter_model: str | None = None) -> glm.Tool:
        """Creates Gemini functions for registered (Model x Function Function) combinations. May filter to create for only one model"""
        functions = [
            glm.FunctionDeclaration(
                name=function.name.format(model_name),
                description=f"{function.description_prefix} {self._models[model_name].__doc__}",
                parameters=model_schema,
            )
            for function in self._functions
            for model_name, model_schema in self._schemas.items()
            if (filter_model is None) or (model_name == filter_model)
        ]
        return glm.Tool(function_declarations=functions)

    def get_model_from_function_name(self, function_name: str) -> DataModel:
        """Returns the model that was used to create a GeminiFunction"""
        names = {
            function.name.format(model_name): model
            for function in self._functions
            for model_name, model in self._models.items()
        }
        return names[function_name]


class _SchemaConfig(typing.TypedDict):
    description: str
    nullable: bool


def _format_parameter(field: FieldInfo) -> glm.Schema:
    assert field.annotation is not None, f"Field {field} missing annotation"
    assert field.description is not None, f"Field {field} missing description"
    _optional_mappings = {(ann | None): ann for type_ in (str, bool, int, float) for ann in (type_, list[type_])}

    annotation = field.annotation
    if nullable := (annotation in _optional_mappings):
        annotation = _optional_mappings[annotation]
    config = _SchemaConfig(description=field.description, nullable=nullable)
    return _format_type(annotation, **config)


def _format_type(annotation: type, **kwargs: typing.Unpack[_SchemaConfig]) -> glm.Schema:
    # Surely there is a better way of doing this right?...
    # like a built in function? or even this not being required at all?
    mapping = {
        str: glm.Schema(type=glm.Type.STRING, **kwargs),
        bool: glm.Schema(type=glm.Type.BOOLEAN, **kwargs),
        int: glm.Schema(type=glm.Type.INTEGER, **kwargs),
        float: glm.Schema(type=glm.Type.NUMBER, **kwargs),
        list[str]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.STRING), **kwargs),
        list[bool]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.BOOLEAN), **kwargs),
        list[int]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.INTEGER), **kwargs),
        list[float]: glm.Schema(type=glm.Type.ARRAY, items=glm.Schema(type=glm.Type.NUMBER), **kwargs),
    }
    return mapping[annotation]


def _snake_case(name: str) -> str:
    return '_'.join(re.findall(r"([A-Z][a-z0-9\_]+)", name)).lower()
