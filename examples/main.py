import os
from pathlib import Path
# import time
import logging

import pydantic
import google.generativeai as genai

from google.third_party_gemini_extensions.gemini_easy_extractor import create_gemini_model, extract_document_information

from models import group

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

input_folder = Path("examples/input")
output_folder = Path("examples/output")

gemini = create_gemini_model(gemini_version="gemini-1.0-pro", temperature=0.15, top_p=0.25)

group.create_function("register_{}", "Register a new")

PROMPT_TEMPLATE = """Given the following story, \
identify all notable {{model_name}}s \
and register each of them through Tools, \
including all relevant information about them.
```
{file_text}
```"""

# PROMPT_TEMPLATE = """Dado o seguinte documento, \
# identifique e registre todos os {{model_name}}s importantes, \
# incluindo todos os dados relevantes sobre cada um deles.
# ---
# {file_text}
# """

# PROMPT_TEMPLATE = """
# 以下の小説の章に基づいて,\
# 注目すべき小説の登場\
# {{model_name}}をすべて特定し,\
# それぞれの関連情報を含めてToolに登録する
# ************************************************
# {file_text}"""


# Note: You might have to re-run multiple times if you get http 500 errors or just trying to get better results
# In these cases, I strongly recommend manually specifying which files or which slice of files you want to (re)run


# for file in input_folder.glob("*.txt"):
files = list(input_folder.glob("*.txt"))
for file in files:
    prompt = PROMPT_TEMPLATE.format(file_text = file.read_text("UTF-8"))

    extracted_data = extract_document_information(
        gemini=gemini,
        function_group=group,
        base_prompt=prompt,
        extract_models_individually=True,
    )
    # print("Sleeping for (4 * num_requests) seconds in consideration of rate limits")
    # time.sleep(12)

    adapter = pydantic.TypeAdapter(dict[str, list])
    out_file = output_folder / file.with_suffix(".json").name
    out_file.write_bytes(adapter.dump_json(extracted_data, indent=4))

