#!/bin/bash -       
#title           :Create new python project
#description     :This script will create a skeleton of python project with poetry, click and tasks
#author		 :bgw, modified by rokdd
#date            :20231118
#version         :0.1
#usage		 :bash new_project.sh
#notes           :Install python-venv before
#bash_version    :4.1.5(1)-release
#==============================================================================

today=$(date +%Y%m%d)
div=======================================

/usr/bin/clear

function _ask_yes_or_no() {
    read -p "$1 ([y]es or [N]o): "
    case $(echo $REPLY | tr '[A-Z]' '[a-z]') in
        y|yes) echo "yes" ;;
        *)     echo "no" ;;
    esac
}

_select_title(){

    # Get the user input.
    printf "Enter a title: " ; read -r title

    # Remove the spaces from the title if necessary.
    title=${title// /_}

    # Convert uppercase to lowercase.
    title=${title,,}

   

    # Check to see if the file exists already.
    if [ -e $title ] ; then 
        printf "\n%s\n%s\n\n" "The script \"$title\" already exists." \
        "Please select another title."
        _select_title
    fi

}

_select_title

sudo apt install python3-venv > /dev/null

printf "Enter parent path: " ; read -r path_folder
cd $path_folder
mkdir -p $title
cd $title
echo "Created folder"
python3 -m venv "$path_folder/$title/.venv"
echo "Created venv"
source .venv/bin/activate
python3 -m pip install --upgrade pip -q
if [[ "yes" == $(_ask_yes_or_no "Do you want to add poetry including poethepoet+click and a initial pyproject.toml?") ]]
then
pip install poetry -q
poetry init -n
poetry add poethepoet -q
poetry add click -q
echo "Poetry inited"
#add dummy task
cat >> pyproject.toml << EOF
[tool.poe.tasks]
test         = "pytest --cov=my_app"                         # a simple command task
serve.script = "my_app.service:run(debug=True)"              # python script based task
tunnel.shell = "ssh -N -L 0.0.0.0:8080:\$PROD:8080 \$PROD &"   # (posix) shell based task
EOF
fi

if [[ "yes" == $(_ask_yes_or_no "Do you want an initial main.py?") ]]
then
cat >> main.py << EOF
import click

@click.group()
def cli():
    pass

@cli.command()
def hello_world():
    print("Hello World")


@cli.command()
@click.option("-g",'--goodbye', default=False, is_flag=True,help='Say goodbye')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello_human(goodbye,human):
    if goodbye:
       print("Bye "+human)
    else:
        print("Hello "+human)

if __name__ == '__main__':
    cli()
EOF
fi

if [[ "yes" == $(_ask_yes_or_no "Do you want an .gitignore?") ]]
then
cat >> .gitignore << EOF
#source: https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*\$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/


# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py


# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

#for the project configuration
*.code-workspace
EOF
fi


_create_vs_workspace(){
cat >> $title.code-workspace << EOF
  {
    "folders": [
      {
      "path": "."
      }
    ],
    "settings": {}
  }
EOF
}

_select_editor(){

    # Select between Vim or Emacs.
    printf "%s\n%s\n%s\n\n\n" "Select an editor." "1 for visual studio code." "2 for visual studio code insiders."
    read -r editor

    # Open the file with the cursor on the twelth line.
    case $editor in
        1) _create_vs_workspace
            code $title.code-workspace
            ;;
        2) _create_vs_workspace
            code-insiders $title.code-workspace
            ;;
        *) /usr/bin/clear
           printf "%s\n%s\n\n" "I did not understand your selection." \
               "Press <Ctrl-c> to quit."
           _select_editor
            ;;
    esac

}

_select_editor
echo "Project prepared"