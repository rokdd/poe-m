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
python3 -m pip install --upgrade pip
pip install poetry
poetry init
poetry add poethepoet
poetry add click
#add dummy task
cat >> pyproject.toml << EOF
[tool.poe.tasks]
test         = "pytest --cov=my_app"                         # a simple command task
serve.script = "my_app.service:run(debug=True)"              # python script based task
tunnel.shell = "ssh -N -L 0.0.0.0:8080:\$PROD:8080 \$PROD &"   # (posix) shell based task
EOF
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
       echo "Bye "+human
    else:
        echo "Hello "+human

if __name__ == '__main__':
    cli()
EOF


_select_editor(){

    # Select between Vim or Emacs.
    printf "%s\n%s\n%s\n\n\n" "Select an editor." "1 for visual studio code." "2 for visual studio code insiders."
    read -r editor

    # Open the file with the cursor on the twelth line.
    case $editor in
        1) code .
            ;;
        2) code-insiders .
            ;;
        *) /usr/bin/clear
           printf "%s\n%s\n\n" "I did not understand your selection." \
               "Press <Ctrl-c> to quit."
           _select_editor
            ;;
    esac

}

_select_editor
