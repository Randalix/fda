from subprocess import check_output, PIPE
from hou import ui
from fda import config
form fda import config
from pathlib import Path
from fda import config

def open(input):
    # menuin = "\n".join(input)
    f'{config.runterm} -e bash -c "cat $INPUT_FILE | fzf --preview='' > $OUTPUT_FILE'
    p = run(['fzf'], stdout=PIPE,
        input=menuin, encoding='ascii')
    # output = p.stdout.replace('\n', '')

