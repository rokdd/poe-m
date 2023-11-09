# -*- coding: utf-8 -*-
#  Copyright (c) 2023-2023 Robert Kühn

from itertools import count
from click import command
from albert import *
from locale import getdefaultlocale
from socket import timeout
from time import sleep
from urllib import request, parse
import json, os
from pathlib import Path
import fnmatch
import tomllib
import re

md_iid = "2.1"
md_version = "0.12"
md_name = "poe-m"
md_description = "Execute commandos and shell scripts"
md_license = "BSD-3"
md_url = "https://github.com/al"
# https://github.com/albertlauncher/python/blob/master/albert.pyi

HOME_DIR = os.environ["HOME"]

'''
TODO:
- open directory?
- create new project
- create new shell file

'''


class poe_mFallbackHandler(FallbackHandler):
    def __init__(self):
        FallbackHandler.__init__(
            self,
            id=f"{md_id}_poe_m_fb",
            name=f"{md_name} fallback",
            description="poe-m fallback search",
        )

    def fallbacks(self, query_string):
        stripped = query_string.strip()
        return [Plugin.createFallbackItem(query_string)]


class NameItem(StandardItem):
    def __init__(self,cmd:str,
                 **kwargs):
                 
        StandardItem.__init__(
            self,
            **kwargs
        )
        
        self.cmd = cmd

class Plugin(PluginInstance, TriggerQueryHandler):
    baseFolder = "/home/rokdd/Documents/Eigene-Programme/90_commander"
    # configuration_directory = os.path.join(configLocation(), md_name)
    newScript = baseFolder + "/new_script.sh"
    # /home/rokdd/Documents/Private-Programmierungprojekte/P511_degiroapi/pyproject.toml
    plugin_dir = Path(__file__).parent

    iconUrls = [f"file:{Path(__file__).parent}/poe-m.svg"]
    trigger = "poem "

    def __init__(self):
        TriggerQueryHandler.__init__(
            self,
            id=md_id,
            name=md_name,
            description=md_description,
            defaultTrigger=self.trigger,
        )
        self.poe_m_fb = poe_mFallbackHandler()

        PluginInstance.__init__(self, extensions=[self, self.poe_m_fb])
        #self.CacheFilePath = self.cacheLocation / "commands.json"
        self._path_folder = self.readConfig("path_folder", str) or ""
        
        self.setCommandsAsItems()

    @property
    def path_folder(self):
        return self._path_folder

    @path_folder.setter
    def path_folder(self, value):
        print(f"Setting path_folder to {value}")
        self._path_folder = value
        self.writeConfig("path_folder", value)

    def configWidget(self):
        return [
            {
                "type": "lineedit",
                "property": "path_folder",
                "label": "folder to monitor, split by comma",
            }
        ]

    def findVenv(self, path_folder):
        if Path.exists(path_folder / ".venv/bin/activate"):
            return 'source ".venv/bin/activate" && '
        return ""

    def readProjectToml(self, path):
        commands=[]
        path_folder = Path(path).parent
        with open(path, "rb") as f:
            data = tomllib.load(f)
            title = data["tool"]["poetry"]["name"]
            for k, v in data["tool"]["poe"]["tasks"].items():
                item = {}
                # script means accessing with poe and virtual env
                if isinstance(v, dict) and "script" in v.keys():
                    # tasks can be very complicated .. execute them with poe! https://poethepoet.natn.io/guides/args_guide.html
                    # check for the virtual environment
                    item = {
                        "title": k,
                        "subtitle": "[in " + title + "]",
                        "action": {
                            "cmd": 'cd "'
                            + str(path_folder)
                            + '" && '
                            + str(self.findVenv(path_folder))
                            + "poe "
                            + k,
                            "cwd": str(path_folder),
                            "close": False,
                        },
                    }
                    # docu: https://poethepoet.natn.io/guides/help_guide.html
                    if "help" in v.keys() and len(v["help"]) > 1:
                        item["subtitle"] += " " + v["help"]
                if item != {}:
                    print("index script ", k, item)
                    commands.append(item)

        return commands

    def readProjectSh(self, path):
        commands=[]
        path_folder = Path(path).parent


        var_pat = re.compile(r'^\#(\w+)\s*?\s+:(.*)$', re.MULTILINE)
        with open(path) as f:
            text = f.read()
            var_list = var_pat.findall(text)
            obj={}
            for tupl in var_list:
                if tupl[0] in ["usage"]:
                    if tupl[0] not in obj.keys():
                        obj[tupl[0]]=[tupl[1]]
                    else:
                        obj[tupl[0]]=list(set([tupl[1]]+obj[tupl[0]]))
                else:
                    obj[tupl[0]]=tupl[1]

            if not "usage" in obj.keys():
                return []

            for usage in obj["usage"]:
                commands.append({
                            "title": usage,
                            "subtitle": "[in " + obj["title"] + "]",
                            "action": {
                                "cmd": 'cd "'
                                + str(path_folder)
                                + '" && bash '
                                + usage,
                                "cwd": str(path_folder),
                                "close": False,
                            },
                        })
        
        return commands
        
    def readProject(self, path, pyproject=True):
        commands = []
        # only works for file
        
        item_default = {}
        commands=[]
        if Path(path).suffix == ".toml":
           commands=self.readProjectToml(path)
        elif Path(path).suffix == ".sh":
           commands=self.readProjectSh(path)
        else:
            print("Unknown format",str(path),Path(path).name[:-3],Path(path).suffix)
 
        return commands
    
    def readFiles(self,path):
         files=[]
         for root, dirnames, filenames in os.walk(path, followlinks=True):
            for filename in fnmatch.filter(filenames,  "*.sh"):
                files.append(os.path.join(root,filename))
         return files
    
    def setCommandsAsItems(self):
        res = self.getCommands()
        results=[]

        for i, r in enumerate(res):
            results.append(
                NameItem(
                    id=md_id + str(i),
                    text=r["title"],
                    subtext=r["subtitle"],
                    iconUrls=self.iconUrls,
                    cmd=r["action"]["cmd"],
                    actions=[
                        Action(
                            "open",
                            "Action:" + r["title"]+r["action"]["cmd"],
                            lambda u=r: runTerminal(
                                u["action"]["cmd"],
                                u["action"]["cwd"],
                                u["action"]["close"],
                            ),
                        )
                    ],
                )
            )
        self.items=results
        
        return results

    def getCommands(self, otp=False):
        commands = []
        srcs = [
            "/home/rokdd/Documents/Private-Programmierungprojekte/P511_degiroapi/pyproject.toml",
            *self.readFiles("/home/rokdd/Documents/Eigene-Programme/20_Scripts/7000_test")
        ]
        print("Files we read:",srcs)
        for s in srcs:
            commands.extend(self.readProject(s))

        return sorted(commands, key=lambda s: s["title"].lower())


    def handleTriggerQuery(self, query):
        stripped = query.string.strip()

        if stripped:
            # avoid rate limiting
            for _ in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            results = []      

            qs = query.string.strip().lower()
            for item in self.items:
                if qs in item.text.lower() or qs in item.subtext.lower() or qs in item.cmd.lower():
                    
                    query.add(item)

    
            if not results:
                results.append(Plugin.createFallbackItem(stripped))
            else:
                query.add(results)

        else:
            query.add(
                StandardItem(
                    id=md_id + "wed",
                    text=md_name,
                    subtext="Enter a noting to create a new one",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            "Create command",
                            "Create command %s" % "fggh",
                            lambda selected_project=stripped: runTerminal(
                                "bash " + self.newScript, self.baseFolder, True
                            ),
                        )
                    ],
                )
            )

    @staticmethod
    def createFallbackItem(query_string):
        return StandardItem(
            id=md_id,
            text=md_name,
            subtext="Create new script '%s' with poe-m"
            % query_string.replace(Plugin.trigger, ""),
            iconUrls=Plugin.iconUrls,
            actions=[
                Action(
                    "Create command",
                    "Create command %s" % "fggh",
                    lambda selected_project=query_string: runTerminal(
                        "bash " + Plugin.newScript, Plugin.baseFolder, True
                    ),
                )
            ],
        )
