import os

import google.generativeai as genai

from tools import collect_tools, get_model_from_function_name

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

tools = collect_tools()
model = genai.GenerativeModel(
    "gemini-1.0-pro",
    tools=tools,
    tool_config={"function_calling_config": "ANY"},   # type: ignore
    generation_config=genai.GenerationConfig(temperature=0.2),
)
novel = """Chapter 1 - Begginings

This is the story of Sora, the blue slime, and Kevin, its Tamer.
Sora was born in the outskirts, during a Mana Storm, \
when a lot of mana concentrated in the Mystic Lake, increasing the occurante rate of monsters.
After being born, Sora was just wondering around and consuming weaker monster for days,\
becoming stronger thanks to slimes inherent ability Gluttony.

Around a month after the Storm, adventures investigating the aftermatch found Sora and the party's Tamer created a Pact with it, \
despite the Ranger and Paladin protests against it, thanks to the leader Knight's approval.
"""

prompt = f"""Given the following novel chapter, identify notable Novel Characters then register each of them through Tools, including all relevant information about each of them.
```
{novel}
```"""

response = model.generate_content(prompt)

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
with open("example_output.json", 'wb') as file:
    adapter = pydantic.TypeAdapter(dict[str, list])
    file.write(adapter.dump_json(result, indent=4))
