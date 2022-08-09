from pathlib import Path
home=Path.home()
online=False
lib=home / "fda"
TERM="/Users/joe/.cargo/bin/alacritty"
FZF="/opt/homebrew/bin/fzf"
savenetworks = ["obj", "mat", "tasks", "stage", "img", "shop", "out", "ch"]
lib.mkdir(parents=True, exist_ok=True)
