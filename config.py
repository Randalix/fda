from pathlib import Path
home=Path.home()

lib=home / "fda"
lib.mkdir(parents=True, exist_ok=True)
