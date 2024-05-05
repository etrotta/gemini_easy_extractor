# Novel Summarizer

Automatically create a structured summary containing relevant information about novels, books or any form of text.

**Disclaimer:** The output quality is not anywhere near usable. Do not use it for anything beyond experimentation/research.

There are some ways in which I could potentially improve it such as
- splitting the chapters into smaller segments
- adding context about the data registered so far
- - throwing a human in the loop to correct mistakes before they pile up if I add the above
- using a better model
- use the same language for everything from the data models, their fields, their description to the prompt to the input text

But I'm not sure how much I really care about it, so feel free to explore that if you're feeling like it

# How it works

First, you have to
- download the data and pre-process it (a folder containing `.txt` files containing only the relevant text, with little markdown and be cautious about prompt injection if try to run it on user input, for things you really shouldn't be using this for in first place.)
- pre-process it, define which models you want to use and register them
- create a Google Gemini API Key and set it as the `GOOGLE_API_KEY` environment variable
- potentially adjust the prompt template

Then just run it for all files in the folder


It is not really meant to be user friendly at its current state, but should be usable if you have some experience programming. Not sure why you would want to use it that hard though.

