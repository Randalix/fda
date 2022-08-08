# Free Digital Asset
Instead of saving houdini assets as hda this tool saves nodes as python code and uses git for versioning.

Why?
- See changes
- Revert changes
- Have people collaborate and merge efforts.
- No Licensing restrictions
- No need to share hdas with renderfarms and colleagues.

Currently every node is its own github repository. This way it's easier to rollback changes and to collaborate.


## Dependencies:
- git
- fzf https://github.com/junegunn/fzf

optional (for automatic online commits):
- hub https://github.com/github/hub

If you want to automaticly upload commits to github you need git with ssh-keys, and hub to be initialized.

## Install
Open a terminal in the houdini python directory.
Macos ~/Library/Preferences/houdini/X.Y/python3.7libs
Linux ~/houdiniX.Y/python3.7libs
Run 
```
git clone https://github.com/Randalix/fda.git
cd fda
setup.py

```
