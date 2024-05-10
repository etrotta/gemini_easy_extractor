import logging
import typing
import google.generativeai as genai
import google.ai.generativelanguage as glm

from google.third_party_gemini_extensions.gemini_easy_extractor.tool_factory import FunctionGroup
import pydantic

log = logging.getLogger("gemini_easy_extractor.generation")


def create_gemini_model(
        *,
        gemini_version: str,
        temperature: float | None = None,
        top_k: int | None = None,
        top_p: float | None = None,
    ) -> genai.GenerativeModel:
    "You may create it on your own instead of calling this function, just be careful about the settings"
    return genai.GenerativeModel(
        gemini_version,
        generation_config=genai.GenerationConfig(temperature=temperature, top_k=top_k, top_p=top_p),
    )


def extract_document_information(
    *,
    gemini: genai.GenerativeModel,
    base_prompt: str,
    function_group: FunctionGroup,
    extract_models_individually: bool = False,
) -> dict[str, list[pydantic.BaseModel]]:
    """Runs all functions from a FunctionGroup for all of its models
    
    Parameters
    ----------
    base_prompt: str
        Prompt to be passed to the model, already including the document's body.
    
    function_group: FunctionGroup
        Group of Data Models and Template Functions detemining which data to extract from the Document
    
    extract_models_individually: bool, default False
        If set to `True`, calls the API once for each Model in the function_group including the entire base_prompt,
          letting Gemini better focus on each part of data.

    Notes
    -----
    If `extract_models_individually` is set to True,
    the base_prompt may contain `{model_name}` as a placeholder, which will be passed through `str.format()`
    
    It is recommended to set it to True and include the `model_name` placeholder, but is set to False by default to prevent billing surprises
    """
    assert function_group.has_models_and_functions(), "You must register Data Models and Template Functions before extracting information"
    if extract_models_individually:
        result = {}
        for model_name in function_group.collect_models():
            tools = function_group.collect_tools(model_name)
            prompt = base_prompt.format(model_name=model_name)
            called_functions = _run_prompt(gemini, prompt, tools)
            models = _build_models(function_group, called_functions)
            result.update(models)
        return result
    else:
        tools = function_group.collect_tools()
        called_functions = _run_prompt(gemini, base_prompt, tools)
        return _build_models(function_group, called_functions)



def _run_prompt(model: genai.GenerativeModel, prompt: str, tools: glm.Tool) -> dict[str, list[dict[str, typing.Any]]]:
    log.debug(f"Calling Gemini with {tools=} for {prompt=}")
    response = model.generate_content(
        prompt,
        tools=tools,
        tool_config={"function_calling_config": "ANY"}, # type: ignore
    )

    for i, candidate in enumerate(response.candidates, 1):
        for j, part in enumerate(candidate.content.parts, 1):
            log.debug(f" Candidate {i}/{len(response.candidates)} Part {j}/{len(candidate.content.parts)}:")
            if part.text:
                # *Should* always be empty. In practice it can not be thanks to bugs on their side.
                log.warning(f"Gemini generated Output Text instead of executing a Function Call: {part.text!r}")
            if part.function_call.name:
                _function_args = dict(part.function_call.args.items()) if part.function_call.args else None
                log.debug(f"Output Function Call: {part.function_call.name!r}({_function_args!r})")

    result = {}
    for part in (part for candidate in response.candidates for part in candidate.content.parts):
        call = part.function_call
        if call.name == "" or call.args is None:
            continue
        arguments = dict(call.args.items())
        result.setdefault(call.name, []).append(arguments)
    return result

def _build_models(group: FunctionGroup, function_calls: dict[str, list[dict[str, typing.Any]]]) -> dict[str, list[pydantic.BaseModel]]:
    result: dict[str, list[pydantic.BaseModel]] = {}
    for function_name, calls in function_calls.items():
        for arguments in calls:
            try:
                model_type = group.get_model_from_function_name(function_name)
            except KeyError:
                log.error(f"Gemini tried to call a function that does not exists: {function_name}.")
                continue
            try:
                data = model_type.model_validate(arguments)
            except pydantic.ValidationError:
                log.error(f"Validation Error trying to load {model_type} with arguments {arguments!r}")
                continue
            # result.setdefault(function_name, []).append(data)
            result.setdefault(model_type.__name__, []).append(data)
    return result
