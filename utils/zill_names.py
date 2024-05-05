from pathlib import Path

folder = Path("novel")

novels = [*folder.glob("*.txt")]

prefix = novels[0].name.split("-")[0] + '-'

numbers = [int(novel.stem.removeprefix(prefix)) for novel in novels]
largest = max(numbers)
# n_decimals = math.ceil(math.log10(largest))
n_decimals = len(str(largest))
formatted_names = [f'{prefix}{number:0>{n_decimals}}' for number in numbers]

# novel = novels[0]
# formatted_name = formatted_names[0]
# novel = novels[1]
# formatted_name = formatted_names[1]
for novel, formatted_name in zip(novels, formatted_names):
    if novel.stem != formatted_name:
        new_name = novel.with_stem(formatted_name)
        print(f"Renaming {novel} to {new_name}")
        novel.rename(new_name)

