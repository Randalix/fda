# Free Digital Asset
Instead of saving houdini assets as hda this tool saves nodes as python code and uses git for versioning.

Why?

All the advantages of git:
- See changes
- Revert changes
- Have people collaborate and merge efforts.

Currently every node is its own github repository. This way it's easier to rollback changes and to collaborate.


## Dependencies:
- git

optional (for automatic online commits):
- hub https://github.com/github/hub
- fzf https://github.com/junegunn/fzf
- 
If you want to automaticly upload commits to github you need git with ssh-keys, and hub to be initialized.

## Install
In the houdini home directory create a folder python3.7libs. Open a Terminal there  and run Open a Terminal and run `git clone https://github.com/Randalix/fda.git`
