import os
from pathlib import Path
import time

import pydantic
import google.generativeai as genai

from src.syo.tool_factory import collect_tools, get_model_from_function_name
from src.syo.common_models import register_common_models

data_models = register_common_models()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

input_folder = Path("novel")
output_folder = Path("results")
tools = collect_tools()
TOOL_CONFIG = {"function_calling_config": "ANY"}

model = genai.GenerativeModel(
    "gemini-1.0-pro",
    tools=tools,
    tool_config=TOOL_CONFIG,   # type: ignore
    generation_config=genai.GenerationConfig(temperature=0.4),
)


# PROMPT_TEMPLATE = f"""Given the following novel chapter, \
# identify all notable novel {{data_type}}s \
# and register each of them through Tools, \
# including all relevant information about them.
# ```
# {{file_text}}
# ```"""
PROMPT_TEMPLATE = """
以下の小説の章に基づいて,\
注目すべき小説の登場\
{data_type}をすべて特定し,\
それぞれの関連情報を含めてToolに登録する
************************************************
{file_text}"""

print("Prompt template:", PROMPT_TEMPLATE)


def run_for_file(file: Path, data_model: type[pydantic.BaseModel]):
    # prompt = f"""{BASE_PROMPT}\n```\n{file.read_text("UTF-8")}\n```"""
    prompt = PROMPT_TEMPLATE.format(file_text=file.read_text("UTF-8"), data_type=data_model.__name__)
    print(f"Formatted prompt: {prompt.split('***', 1)[0]} [...]")
    model_tools = collect_tools(data_model.__name__)
    response = model.generate_content(
        prompt,
        tools=model_tools,
        tool_config=TOOL_CONFIG,  # type: ignore
    )

    for i, candidate in enumerate(response.candidates, 1):
        for j, part in enumerate(candidate.content.parts, 1):
            print(f"File {file.name!r} - {data_model.__name__} Data"
                  f" Candidate {i}/{len(response.candidates)} Part {j}/{len(candidate.content.parts)}:")
            if part.text:
                # *Should* always be empty. In practice it can not be thanks to bugs on their side.
                print(f"- Output Text: {part.text!r}")
            if part.function_call.name:
                _function_args = dict(part.function_call.args.items()) if part.function_call.args else None
                print(f"- Output Function Call: {part.function_call.name!r}({_function_args!r})")


    result = {}

    for part in (part for candidate in response.candidates for part in candidate.content.parts):
        call = part.function_call
        if call.name == "" or call.args is None:
            continue
        arguments = dict(call.args.items())

        try:
            novel_model = get_model_from_function_name(call.name)
        except KeyError:
            print(f"The model tried to call a function that does not exists: {call.name}. Skipping this Part.")
            continue
        if novel_model is not data_model:
            print(f"Expected for model to operate on a {data_model}, instead model is operating on a {novel_model}. Skipping this Part")
            continue

        try:
            character = novel_model(**arguments)
        except pydantic.ValidationError:
            print(f"Validation Error trying to load {novel_model} with arguments {arguments!r}")
            continue
        result.setdefault(novel_model.__name__, []).append(character)
    return result


CHECKPOINT = 0
# for file in input_folder.glob("*.txt"):
files = list(input_folder.glob("*.txt"))
for file in files[CHECKPOINT:]:
    file_results: dict[str, list] = {}
    for data_model in data_models:
        print(f"Processing file {file!r} for {data_model.__name__}")
        result = run_for_file(file=file, data_model=data_model)
        print(result)
        file_results.update(result)
        print("Sleeping for 4 seconds in consideration of rate limits")
        time.sleep(4)

    adapter = pydantic.TypeAdapter(dict[str, list])
    out_file = output_folder / file.with_suffix(".json").name
    out_file.write_bytes(adapter.dump_json(file_results, indent=4))


