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
from os.path import abspath

md_iid = "2.1"
md_version = "0.16"
md_name = "poe-m"
md_description = "Execute commandos and shell scripts"
md_license = "BSD-3"
md_url = "https://github.com/rokdd/poe-m"

HOME_DIR = os.environ["HOME"]


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
    def __init__(self,cmd:str,trigger:str,
                 **kwargs):
                 
        StandardItem.__init__(
            self,
            **kwargs
        )
        
        self.cmd = cmd
        self.trigger= trigger

class Plugin(PluginInstance, IndexQueryHandler):
    baseFolder = HOME_DIR
    # configuration_directory = os.path.join(configLocation(), md_name)
    newScript = baseFolder + "/new_script.sh"
    plugin_dir = Path(__file__).parent

    iconUrls = [f"file:{Path(__file__).parent}/poe-m.svg"]
    trigger = "poem "

    def __init__(self):
        IndexQueryHandler.__init__(
            self,
            id=md_id,
            name=md_name,
            description=md_description,
            defaultTrigger=self.trigger,
        )
        self.poe_m_fb = poe_mFallbackHandler()

        PluginInstance.__init__(self, extensions=[self, self.poe_m_fb])
        #self.CacheFilePath = self.cacheLocation / "commands.json"

        #path which we monitor for changes
        self._path_watch = self.readConfig("path_watch", str) or ""
        #path for new scripts or commands
        self._path_default_shell = self.readConfig("path_default_shell", str) or ""
        #path for new projects 
        self._path_default_project = self.readConfig("path_default_project", str) or ""
        #path for the alias file. if empty none is written
        self._path_alias= self.readConfig("path_alias", str) or ""

        commands=self.getCommands()
        self.setCommandsAsItems(commands)
        if self.path_alias != "":
            #stupid hack
            self.setCommandsAsAliases(commands,file_name=self.path_alias.replace("~",HOME_DIR+""))

    def findVenv(self, path_watch):
        if Path.exists(path_watch / ".venv/bin/activate"):
            return 'source ".venv/bin/activate" && '
        return ""

    def readProjectToml(self, path):
        commands=[]
        path_watch = Path(path).parent
        with open(path, "rb") as f:
            data = tomllib.load(f)
            if "tool" in data.keys() and "poetry" in data["tool"].keys():
                title = data["tool"]["poetry"]["name"]
                for k, v in data["tool"]["poe"]["tasks"].items():
                    item = {}
                    # script means accessing with poe and virtual env
                    if isinstance(v, dict):
                        # tasks can be very complicated .. execute them with poe! https://poethepoet.natn.io/guides/args_guide.html
                        # check for the virtual environment
                        item = {
                            "title": k,
                            "trigger":k,
                            "subtitle": "[in " + title + "]",
                            "action": {
                                "cmd": 'cd "'
                                + str(path_watch)
                                + '" && '
                                + str(self.findVenv(path_watch))
                                + "poe "
                                + k,
                                "cwd": str(path_watch),
                                "close": False,
                            },
                        }
                    else:
                        continue
                        # docu: https://poethepoet.natn.io/guides/help_guide.html
                    if isinstance(v, dict):
                        if "name" in v.keys() and len(v["name"]) > 1:
                            item["title"] = v["name"]
                        if "help" in v.keys() and len(v["help"]) > 1:
                            item["subtitle"] += " " + v["help"]
                    if item != {}:
                        print("index script ", k, item)
                        commands.append(item)

        return commands

    def readProjectSh(self, path):
        commands=[]
        path_watch = Path(path).parent

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
                #here we just add unknown file bash files
                return [{"title":os.path.basename(str(path)),"trigger":os.path.basename(str(path))[:-3],"subtitle":"","action": {
                                "cmd": 'cd "'
                                + str(path_watch)
                                + '" && bash '
                                + str(path),
                                "cwd": str(path_watch),
                                "close": False,
                            }}]

            for usage in obj["usage"]:
                commands.append({
                            "title": usage,
                            "trigger":os.path.basename(str(path))[:-3],
                            "subtitle": "[in " + obj["title"] + "]",
                            "action": {
                                "cmd": 'cd "'
                                + str(path_watch)
                                + '" && '
                                + usage,
                                "cwd": str(path_watch),
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
    
    def readFiles(self,path,filter="**/*"):
         files=[]
         for path in Path(path).glob(filter):
            if path.suffix in ['.sh', '.toml']:
                files.append(path)
         return files
    
    def setCommandsAsAliases(self,res,file_name=False):
        #without filename we don't do anything
        if not file_name or file_name=="":
            return False
        f = open(file_name, 'w+')  # open file in write mode
        #write a general function to set envs
        f.write('function poem-init() {\n'+"\n".join(["export POEM_"+k.upper()+"='"+getattr(self,k)+"'" for k in ["path_alias","path_default_shell","path_default_project"]])+'\n}\n')
        f.write('\n'+"\n".join(["export POEM_"+k.upper()+"='"+getattr(self,k)+"'" for k in ["path_alias","path_default_shell","path_default_project"]])+'\n\n')
        
        for i, r in enumerate(res):
            f.write('function poem-'+str(r["trigger"])+'() {\npoem-init "$@"\n'+"\n".join(["POEM_"+k.upper()+"='"+getattr(self,k)+"'" for k in ["path_alias","path_default_shell","path_default_project"]])+'\n'+r["action"]["cmd"].replace(" && ","\n")+" \"$@\"\n}\n")

        f.close()

    def setCommandsAsItems(self,res):     
        results=[]

        for i, r in enumerate(res):
            results.append(
                NameItem(
                    id=md_id + str(i),
                    text=r["title"],
                    subtext=r["subtitle"],
                    trigger=r["trigger"],
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
        index_items=[]
        for r in results:
            index_items.append(IndexItem(item=r, string=r.text+r.subtext))
            index_items.append(IndexItem(item=r, string=r.cmd))
        if len(index_items)>0:
            self.setIndexItems(index_items)
        return results

    def getCommands(self):
        commands = []
        
        src_paths=self.path_watch.split(",")
        #we add the default paths as well
        if self.path_default_project!="":
            src_paths.append(self.path_default_project)
        if self.path_default_shell!="":
            src_paths.append(self.path_default_shell)
        src_paths=list(set(src_paths))

        print("Directorys we are reading:",src_paths)
        if len(src_paths)>0:
            #we add the template folder next to us
            src_paths.append(self.plugin_dir/"templates")
            for src_path in src_paths:
                if os.path.exists(src_path):
                    #print("Files we found in "+src_path+":",self.readFiles(src_path))
                    for file_path in self.readFiles(src_path):
                        commands.extend(self.readProject(file_path))

            return sorted(commands, key=lambda s: s["title"].lower())
        return []


    def handleTriggerQuery(self, query):
        stripped = query.string.strip()

        results = []

        if stripped:
            # avoid rate limiting
            for _ in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            qs = query.string.strip().lower()
            for item in self.items:
                if qs in item.text.lower() or qs in item.subtext.lower() or qs in item.cmd.lower():      
                    query.add(item)

    
            if not results:
                results.append(Plugin.createFallbackItem(stripped))
            else:
                query.add(results)
                return

    
        query.add(
            StandardItem(
                id=md_id + "wed",
                text=md_name,
                subtext="Enter a noting to create a new one",
                iconUrls=self.iconUrls,
                actions=[
                    Action(
                        "Create command",
                        "Create command %s" % stripped,
                        lambda selected_project=stripped: runTerminal(
                            "bash " + self.newScript, self.baseFolder, True
                        ),
                    )
                ],
            ))
        src_paths=self.path_watch.split(",")
      
        if len(src_paths)>0:
            #first one is the default
            query.add(
                    StandardItem(
                    id=md_id + "open",
                    text=md_name,
                    subtext="Open default folder for new scripts",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            "Create command",
                            "Create command ",
                            lambda selected_project=stripped: runTerminal(
                                "nautilus " + src_paths[0], src_paths[0], True
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

    @property
    def path_watch(self):
        return self._path_watch

    @path_watch.setter
    def path_watch(self, value):
        self._path_watch = value
        self.writeConfig("path_watch", value)

    @property
    def path_default_shell(self):
        return self._path_default_shell

    @path_default_shell.setter
    def path_default_shell(self, value):
        self._path_default_shell= value
        self.writeConfig("path_default_shell", value)

    @property
    def path_default_project(self):
        return self._path_default_project

    @path_default_project.setter
    def path_default_project(self, value):
        self._path_default_project= value
        self.writeConfig("path_default_project", value)

    @property
    def path_alias(self):
        return self._path_alias

    @path_alias.setter
    def path_alias(self, value):
        self._path_alias= value
        self.writeConfig("path_alias", value)

    def configWidget(self):
        return [
            {
                "type": "lineedit",
                "property": "path_watch",
                "label": "folder to monitor, split by comma",
            },
             {
                "type": "lineedit",
                "property": "path_default_shell",
                "label": "folder for new shell scripts",
            }
            ,
             {
                "type": "lineedit",
                "property": "path_default_project",
                "label": "folder for new projects",
            } ,
             {
                "type": "lineedit",
                "property": "path_alias",
                "label": "path for bash alias",
            }
        ]