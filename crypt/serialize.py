from pathlib import Path

PARENT_DIR = Path(__file__).parent.absolute()
(PARENT_DIR / 'key_storage').mkdir(parents=True, exist_ok=True)


def save(filename, text):
    with open(PARENT_DIR / "key_storage" / filename, "wb") as f:
        f.write(text)


def load(filename):
    try:
        with open(PARENT_DIR / "key_storage" / filename, "rb") as f:
            text = f.read()
        return text
    except IOError:
        return None


if __name__ == "__main__":
    save("text.txt", "lol")
