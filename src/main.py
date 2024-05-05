import os
from pathlib import Path

import google.generativeai as genai

from tools import collect_tools, get_model_from_function_name

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)

folder = Path("novel")

test_file = next(iter(folder.glob("*.txt")))
# V please tell me there is a simpler way to define this tool config
# _tool_config = glm.ToolConfig(glm.FunctionCallingConfig(glm.FunctionCallingConfig.Mode.ANY))
# _tool_config = glm.ToolConfig(function_calling_config=glm.FunctionCallingConfig.Mode.ANY)
# model = genai.GenerativeModel('gemini-1.0-pro', tools=collect_tools(), tool_config=_tool_config)
model = genai.GenerativeModel('gemini-1.0-pro', tools=collect_tools(), tool_config={'function_calling_config':'ANY'})  # type: ignore

prompt = f"""Given the following chapter, identify all notable Characters and create a summary including relevant information about each of them.
```
{test_file.read_text("UTF-8")}
```"""

breakpoint()

response = model.generate_content(prompt, tools=collect_tools(), tool_config={'function_calling_config':'ANY'})  # type: ignore

# len(response.candidates)
# len(response.candidates[0].content.parts)
# response.candidates[0].content.parts[0].text
# response.candidates[0].content.parts[0].function_call.name

for candidate in response.candidates:
    for part in candidate.content.parts:
        print("Output Text:", part.text)
        print("Output Function Call:", part.function_call.name, part.function_call.args)

# In theory it should have no Text and <n> function calls, but in practice it did not actually call the function,
# and instead just gave me a freeform text describing the characters, whose format is inconsistent between different runs.

result = {}
for part in response.parts:
    call = part.function_call
    arguments = dict(call.args.items())

    function_name: str = arguments.pop("function_name")  # type: ignore
    assert function_name != "", "Missing Function call"

    novel_model = get_model_from_function_name(function_name)
    character = novel_model(**arguments)  # type: ignore

    result.setdefault(novel_model.__name__, []).append(character)

print(result)
