# Gemini Easy Extractor

Automatically create a structured JSON summary containing relevant information about novels, books, documents or any form of text.

## Warnings
Remember to never send private or classified information to the free version of the Gemini API, the data may be used to train Google's LLM models, which can cause for the model to memorize it and reproduce it to other users.

The output is not anywhere near realiable enough to blindly trust it. Do not use it for anything beyond experimentation/research, and review it before using for anything important.

From my testing, the names and descriptions of your Data Models and Function Template must be writen in English for Gemini to work properly, but you can use other languages for the Prompt itself and for Model Field descriptions.

This is not an official Google project, nor is it endorsed by Google

# How to use it

## User Friendly way

I recommend using the Google Colab version if you need of handholding.
- English version: https://gist.github.com/etrotta/566da8c1e0e7a4110d7fede740644539
- Português Brasileiro: https://gist.github.com/etrotta/7c87f9ebeab0554769a518ef6d0bcfd2

Some details are different between the English version, the Portuguese verion and the Programmer's Way. These are in part to account for the target audience needs and level of technical profeciency, in part because of small improvements I may have made while working on them that I haven't ported back to the others yet. 

## Programmer's Way

It is not available on pypi, but this repository can be installed as a python package:

```
pip install git+https://github.com/etrotta/gemini_easy_extractor/#subdirectory=gemini_easy_extractor
```

If you want to use it like this, please refer to the [examples folder](examples).

It injects itself under the "google" package namespace, creating a new "third_party_gemini_extensions" subpackage, so you have to import it as:

```py
from google.third_party_gemini_extensions import gemini_easy_extractor
# or
from google.third_party_gemini_extensions.gemini_easy_extractor import (
    FunctionGroup,
    create_gemini_model,
    extract_document_information,
)
```
