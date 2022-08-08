from pathlib import Path
home=Path.home()
online=True
lib=home / "fda"
savenetworks = ["obj", "mat", "tasks", "stage", "img", "shop", "out", "ch"]
lib.mkdir(parents=True, exist_ok=True)
