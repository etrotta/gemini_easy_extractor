from pathlib import Path
import logging

logging.basicConfig()
log = logging.getLogger(__name__)

folder = Path("novel")

novels = [*folder.glob("*.txt")]

assert len(novels) == 30

# novel = novels[0]
for novel in novels:
    text = novel.read_text("UTF-8")
    log.info(f"Cleaning {text.split("\n", 1)[0]!r}")
    try:
        post_note_index = text.index("***")
    except ValueError:
        continue  # No need to clean anything
    text, post_note = text[:post_note_index], text[post_note_index:]
    log.debug("Throwing away note: {post_note!r}")
    novel.write_text(text, encoding="UTF-8")

