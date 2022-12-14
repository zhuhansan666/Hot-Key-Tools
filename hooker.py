from os import startfile, path
from typing import Dict
import keyboard
import time
from subprocess import run
import sys
from g import app_config
from Tools import FileTools


class Hooker:

    def __init__(self, set_event_dict: Dict[str, Dict[str, str]]):
        self.__file_tools = FileTools()
        self.__app_config = app_config

        self.old_event = None  # keyboard event 类型
        self.__now_events_list = []
        self.__now_keys_dict = {'up': [], 'down': []}
        self.__events_dict = {}
        self.__string_events_dict = set_event_dict.copy()
        self.__yn_new_hooker = True
        for key_ in set_event_dict:
            self.__events_dict[self.__key_str_to_param(key_)] = set_event_dict[key_]

    def reset(self, set_event_dict: Dict[str, Dict[str, str]]):
        self.__events_dict = {}
        for key_ in set_event_dict:
            self.__events_dict[self.__key_str_to_param(key_)] = set_event_dict[key_]

    @staticmethod
    def __key_str_to_param(key_str: str) -> tuple:

        param = []
        key_list = key_str.split('+')
        for key in key_list:
            param.append(('down', None, key))
            if key == key_list[-1]:
                param.append(('up', None, key))
        return tuple(param)

    def run_func(self, run_info: Dict[str, str]):
        info_type = run_info['type']
        info = run_info['info']

        if info_type == 'start':
            startfile(info, operation='open')
        elif info_type == 'cmd':
            if sys.platform[:3] == 'win':
                run(f"python EXEC.py -S {info}", shell=True)
            elif sys.platform[:3] == 'lin':
                run(f"python3 EXEC.py -S {info}", shell=True)

    def callback(self, event):
        if event != self.old_event:
            self.__now_events_list.append(event)
            for set_event in self.__events_dict:
                end_key = keyboard.KeyboardEvent(*set_event[-1])
                if event == end_key and event.event_type == 'up':
                    for now_event, set_event_ed in zip(self.__now_events_list, set_event):
                        if now_event != keyboard.KeyboardEvent(*set_event_ed):
                            break
                    else:
                        self.run_func(self.__events_dict[set_event])
                        self.__now_events_list.clear()
                        break
                else:
                    if event != end_key and event.event_type != 'up':
                        break
            else:
                self.__now_events_list.clear()
            self.old_event = event

    def __events2hot_key(self, event: keyboard.KeyboardEvent):
        if event != self.old_event:
            self.__now_events_list.append(event)
            for e in self.__now_events_list:
                if e.name not in self.__now_keys_dict['down'] or e.name not in self.__now_keys_dict['up']:
                    if e.event_type == 'down':
                        self.__now_keys_dict['down'].append(e.name)
                    else:
                        self.__now_keys_dict['up'].append(e.name)
            self.__now_events_list.clear()
        self.old_event = event

    def get_now_keys(self) -> dict:
        return self.__now_keys_dict

    def hook_keys(self):
        """
        hook_events() 后不可hook_keys()
        """
        if self.__yn_new_hooker:
            keyboard.hook(callback=self.callback)
            self.__yn_new_hooker = False
        else:
            raise '已创建hooker,不可再次创建'

    def hook_events(self):
        """
        hook_keys() 后不可hook_events()
        """
        if self.__yn_new_hooker:
            keyboard.hook(callback=self.__events2hot_key)
            self.__yn_new_hooker = False
        else:
            raise '已创建hooker,不可再次创建'


if __name__ == '__main__':
    event_dict = {
        'ctrl+e': {'type': 'cmd', 'info': r"ipconfig"},
    }

    hooker = Hooker(event_dict)
    hooker.hook_keys()
    while True:
        time.sleep(0.1)
