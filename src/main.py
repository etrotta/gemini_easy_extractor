import os
from pathlib import Path

import pydantic
import google.generativeai as genai

from src.syo.tool_factory import collect_tools, get_model_from_function_name
from src.syo.common_models import register_common_models

data_models = register_common_models()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

input_folder = Path("novel")
output_folder = Path("results")
tools = collect_tools()

model = genai.GenerativeModel(
    "gemini-1.0-pro",
    tools=tools,
    tool_config={"function_calling_config": "ANY"},   # type: ignore
    generation_config=genai.GenerationConfig(temperature=0.2),
)

def _fancy_join(strings: list[str]) -> str:
    return ", ".join(strings[:-1]) + f", and {strings[-1]}"

# BASE_PROMPT = f"""Given the following novel chapter, \
# identify all notable novel {_fancy_join([data_model.__name__ + 's' for data_model in data_models])} then register each of them through Tools, \
# including all relevant information about each of them."""

# PROMPT_TEMPLATE = f"""Given the following novel chapter, \
# identify all notable novel {_fancy_join([f'`{data_model.__name__}s`' for data_model in data_models])} \
# and register each of them through Tools, \
# including all relevant information about them.
# ```
# {{file_text}}
# ```"""
PROMPT_TEMPLATE = f"""
以下の小説の章に基づいて,\
注目すべき小説の登場\
{','.join([data_model.__name__ for data_model in data_models])}をすべて特定し,\
それぞれの関連情報を含めてToolに登録する
************************************************
{{file_text}}"""

print("Prompt template:", PROMPT_TEMPLATE)


def run_for_file(file: Path):
    # prompt = f"""{BASE_PROMPT}\n```\n{file.read_text("UTF-8")}\n```"""
    prompt = PROMPT_TEMPLATE.format(file_text=file.read_text("UTF-8"))
    response = model.generate_content(prompt)  # type: ignore

    for i, candidate in enumerate(response.candidates, 1):
        for j, part in enumerate(candidate.content.parts, 1):
            print(f"File {file.name!r} Candidate {i}/{len(response.candidates)} Part {j}/{len(candidate.content.parts)}:")
            print(f"- Output Text: {part.text!r}")
            _function_args = dict(part.function_call.args.items()) if part.function_call.args else None
            print(f"- Output Function Call: {part.function_call.name!r}({_function_args!r})")


    result = {}

    # for part in response.parts:
    for part in (part for candidate in response.candidates for part in candidate.content.parts):
        call = part.function_call
        if call.name == "" or call.args is None:
            continue
        arguments = dict(call.args.items())

        novel_model = get_model_from_function_name(call.name)

        try:
            character = novel_model(**arguments)
        except pydantic.ValidationError:
            print(f"Validation Error trying to load {novel_model} with arguments {arguments!r}")
            continue
        result.setdefault(novel_model.__name__, []).append(character)

    print(result)

    adapter = pydantic.TypeAdapter(dict[str, list])
    out_file = output_folder / file.with_suffix(".json").name
    out_file.write_bytes(adapter.dump_json(result, indent=4))

# for file in input_folder.glob("*.txt"):
#     print(f"Processing file {file}")
#     run_for_file(file)
#     break

files = list(input_folder.glob("*.txt"))
import random  # noqa
file = random.choice(files)
print(f"Processing file {file}")
run_for_file(file)

