import os

import google.generativeai as genai

from tools import collect_tools, get_model_from_function_name

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

tools = collect_tools()
model = genai.GenerativeModel("gemini-1.0-pro", tools=tools, tool_config={"function_calling_config": "ANY"})  # type: ignore

novel = """Chapter 1 - Begginings

This is the story of Sora, the blue slime, and Kevin, its Tamer.
Sora was born in the outskirts, during a Mana Storm, \
when a lot of mana concentrated in the Mystic Lake, increasing the occurante rate of monsters.
After being born, Sora was just wondering around and consuming weaker monster for days,\
becoming stronger thanks to slimes inherent ability Gluttony.

Around a month after the Storm, adventures investigating the aftermatch found Sora and the party's Tamer created a Pact with it, \
despite the Ranger and Paladin protests against it, thanks to the leader Knight's approval.
"""

prompt = f"""Given the following chapter, identify notable Characters and create a summary including relevant information about each of them.
```
{novel}
```"""

response = model.generate_content(prompt)

result = {}
for part in response.parts:
    assert part.text == ""
    call = part.function_call
    arguments = dict(call.args.items())

    function_name: str = arguments.pop("function_name")  # type: ignore
    novel_model = get_model_from_function_name(function_name)

    character = novel_model(**arguments)  # type: ignore
    result.setdefault(novel_model.__name__, []).append(character)

print(result)

"""Example output:
{
    "NovelCharacter": [
        NovelCharacter(
            name="Sora",
            aliases=[],
            description="The protagonist slime who just consumed everything to grow up fast.",
            notable_events=["Born during a Mana Storm"],
            notable_skills=[],  # Yep, missing Gluttony...
            origin="The outskirts",  # I'd prefer Mystic Lake...
            notable_past_locations=[],
            age=None,  # Clearly should be 0
        ),
        NovelCharacter(
            name="Kevin",
            aliases=[],  # Should include Tamer imo
            description="Sora\\'s Tamer.",
            notable_events=["The one who Created Pact with Sora"],  # weird wording...
            notable_skills=[],  # Should include Taming...
            origin="Unknown",
            notable_past_locations=[],
            age=None,
        ),
    ]
}
"""
