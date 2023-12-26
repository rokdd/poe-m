# Albert launcher extension Poem

## Background

I was looking for a Command palette which can easily remember cmds and have the possibility to add some basic prompts to some scripts and to recall them later.

## Solution Poe-Manager

Poem is able to
- `index` shell scripts or python poetry tasks
- define paths where to crawl for the files
- `pyproject.toml` working with python / poe:
    - parsed parameters: name, command, helptext
    - activate virtual environment before execution
    - all tasks from poetry get listed as commands
- `shell scripts`:
    - all usages in the header get listed as commands
    - parsed parameters: name, command
- create a `new shell script from template` (type "poem new script")
- create a complete `new python project with venv and configurations` (type "poem new project")
- `execute the commands` in albert launcher
- `creates aliases` so that you can use commands in shell: ~/.poem-aliases

in union the benefits of:
- [albert launcher](https://albertlauncher.github.io/) to provide the GUI
- [python extension](https://github.com/albertlauncher/python/blob/master/albert.pyi) for easeness to extend the plugin
- [poetry](https://python-poetry.org/docs/basic-usage/) to maintain pip packages and `pyproject.toml`
- [pyproject.toml](https://python-poetry.org/docs/pyproject/#scripts) to maintain metadata and pip packages
- [poethepoet](https://github.com/nat-n/poethepoet) to organize the tasks for python project
- [click](https://click.palletsprojects.com) to create a python cli and to prompt for missing arguments
- 

## Todo

- explain how to setup poe
- check for icon in the same folder
- check for icon by path
- update python projects
- option to reindex and rewrite the alias file (currently only at startup)

## Documentation

### Using bash aliases

The extension can write a static alias file in the location you define in the settings.
Limitation: At the moment the file is only written once at startup.

Then add the following line in your ~/.bashrc to source the file:
`. <your filename>`

Afterwards you can refresh the shell and use:

`poem <your command> <your arguments>`

### Using Poetry tasks for python projects

The project needs to use a virtual environment and poetry and [poethepoet](https://poethepoet.natn.io/guides/help_guide.html)

There are different styles how to add your tasks to the `pyproject.toml`

### Update this extension