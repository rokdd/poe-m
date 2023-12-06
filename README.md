# poe-m

## Introduction

I was looking for a Commander which can easily remember cmds and have the possibility to add some basic prompts to some scripts and to recall them later.

## Features

- Python-Plugin which can be installed in albert launcher
- define paths where to crawl for the files and index them
- for pyproject.toml working with python / poe:
    - parsed parameters: name, command, helptext
    - activate virtual environment before execution
    - all tasks from poetry get listed as commands
- for bash scripts:
    - all usages in the header get listed as commands
    - parsed parameters: name, command
- template folder where you can both scenarios from top automatically (type "poem new")
- it creates a file with aliases which you can source into your shell: ~/.poem-aliases

## Todo

- explain how to setup poe
- option for the bash aliases
- check how poe can work globally
- check for icon in the same folder
- check for icon by path