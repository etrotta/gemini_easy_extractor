import os
from pathlib import Path

import google.generativeai as genai

from tools import collect_tools, get_model_from_function_name

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)

folder = Path("novel")
tools = collect_tools()

test_file = next(iter(folder.glob("*.txt")))
# V please tell me there is a simpler way to define this tool config
# _tool_config = glm.ToolConfig(glm.FunctionCallingConfig(glm.FunctionCallingConfig.Mode.ANY))
# _tool_config = glm.ToolConfig(function_calling_config=glm.FunctionCallingConfig.Mode.ANY)
# model = genai.GenerativeModel('gemini-1.0-pro', tools=collect_tools(), tool_config=_tool_config)
# model = genai.GenerativeModel('gemini-1.0-pro', tools=tools, tool_config={'function_calling_config':'ANY'})  # type: ignore

model = genai.GenerativeModel(
    "gemini-1.0-pro",
    tools=tools,
    tool_config={"function_calling_config": "ANY"},   # type: ignore
    generation_config=genai.GenerationConfig(temperature=0.2),
)

prompt = f"""Given the following novel chapter, identify notable Novel Characters then register each of them through Tools, including all relevant information about each of them.
```
{test_file.read_text("UTF-8")}
```"""


response = model.generate_content(prompt, tools=collect_tools(), tool_config={'function_calling_config':'ANY'})  # type: ignore

# len(response.candidates)
# len(response.candidates[0].content.parts)
# response.candidates[0].content.parts[0].text
# response.candidates[0].content.parts[0].function_call.name

for i, candidate in enumerate(response.candidates, 1):
    for j, part in enumerate(candidate.content.parts, 1):
        print(f"Candidate {i}/{len(response.candidates)} Part {j}/{len(candidate.content.parts)}:")
        print(f"- Output Text: {part.text!r}")
        print(f"- Output Function Call: {part.function_call.name!r}({dict(part.function_call.args.items())!r})")

result = {}

for part in response.parts:
    call = part.function_call
    arguments = dict(call.args.items())

    assert call.name != "", "Model did not call a function"
    novel_model = get_model_from_function_name(call.name)

    character = novel_model(**arguments)
    result.setdefault(novel_model.__name__, []).append(character)

print(result)

import pydantic  # noqa
with open("main_output.json", 'wb') as file:
    adapter = pydantic.TypeAdapter(dict[str, list])
    file.write(adapter.dump_json(result, indent=4))
