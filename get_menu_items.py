#!/usr/bin/env python3
import yaml

menu = {"menu_items": [], "exit_key": 'q', "text_main_menu": ""}

with open("settings.yaml", 'r') as stream:
    try:
        menu = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

menu_items = menu["menu_items"]
exit_key = menu["exit_key"]
text_main_menu = menu["text_main_menu"]
