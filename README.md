# poe-m

## Introduction

I was looking for a Commander which can easily remember cmds and have the possibility to add some basic prompts to some scripts and to recall them later.

Poem is able to 

- index shell scripts or python poetry tasks to execute them in albert launcher
- define paths where to crawl for the files
- for pyproject.toml working with python / poe:
    - parsed parameters: name, command, helptext
    - activate virtual environment before execution
    - all tasks from poetry get listed as commands
- for bash scripts:
    - all usages in the header get listed as commands
    - parsed parameters: name, command
- template folder where you can both scenarios from top automatically (type "poem new")
- it creates a file with aliases which you can source into your shell: ~/.poem-aliases

in union the benefits of:

- `albert launcher` to provide the GUI
- `python` for easeness to extend the plugin
- `poetry` / `pyproject.toml` to maintain metadata and pip packages
- `poe-nat` to organize the tasks for python project
- `click` to create a python cli
- 

## Todo

- explain how to setup poe
- option for the bash aliases
- check how poe can work globally
- check for icon in the same folder
- check for icon by path