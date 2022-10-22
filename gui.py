import random

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from threading import Thread
from time import time, sleep

import cs_keys
from hooker import Hooker
from g import config, logging


# root = ttk.Window(themename="superhero")
#
# b1 = ttk.Button(root, text="Submit", bootstyle="success")
# b1.pack(side=LEFT, padx=5, pady=10)
#
# b2 = ttk.Button(root, text="Submit", bootstyle="info-outline")
# b2.pack(side=LEFT, padx=5, pady=10)
#
# root.mainloop()


class Settings(ttk.Window):
    @staticmethod
    def __check_runtype_write_log(func_result: tuple, tip: str = ""):
        """
        判断运行是否成功并写入日志
        :param func_result: 支持的函数的返回值
        :param tip: 提示
        :return: None
        """
        if len(tip) > 0 and tip[-1] != ":":  # 自动添加冒号
            tip = f"{tip}:"

        if func_result[0] != 0:  # error_code 不为 0 视为错误
            logging.write_log(f"In main.py ERROR: {tip} {func_result[-1]}")  # 为错误信息 func_result[-1]

    def __main_thread_func(self):
        self.__main_obj = Hooker(self.__config.result)
        self.__main_obj.hook()
        while self.__main_thread_running:
            t1 = time()
            result = self.__config.load()
            self.__check_runtype_write_log(result, "write config error")
            self.__main_obj.reset(self.__config.result)
            self.__config.write()
            sleep_time = time() - t1
            if sleep_time > self.__main_thread_cycle_time:
                sleep(sleep_time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__config = config
        self.__focusing = ''
        self.__hooking = False
        self.__treeview = None  # ttk.Treeview
        #########################
        # self.__config.result = cs_keys.cs_keys(10)
        self.__config.result = {
            'ctrl+e': {'type': 'cmd', 'info': 'echo 15555555'}
        }
        ########################
        if self.__config.result == {}:
            self.__config.result = self.__events
            result = self.__config.write()
            self.__check_runtype_write_log(result, "write config error")
        else:
            self.__events = self.__config.result
        self.__config.write()

        self.__main_thread_running = True
        self.__main_thread_cycle_time = 0.5
        self.__main_thread = Thread(target=self.__main_thread_func, daemon=True)
        self.__main_thread.start()

        self.init_controls()

    def init_controls(self):
        colors = [
            ""
        ]

        # table_data = [
        #     ("South Island, New Zealand", 1),
        #     ("Paris", 2),
        #     ("Bora Bora", 3),
        #     ("Maui", 4),
        #     ("Tahiti", 5),
        # ]
        self.title(f"HotLeyTools - start from {time():.3f}")
        self.geometry('1400x650')
        self.resizable(False, False)
        # 显示信息的控件
        info_control = ttk.Frame(self)

        button_style = ttk.Style()
        button_style.configure('button_add.TButton', background='#eb6864')
        button_style.configure('button_del.TButton', background='#28b62c')
        button_style.configure('button_find.TButton', background='#007175')
        button_style.configure('button_re.TButton', background='#fff152')

        self.__treeview = ttk.Treeview(master=info_control, columns=['0', '1', '2'], show=HEADINGS, height=25)
        self.__main_obj.reload_treeView(self.__treeview)
        self.__treeview.heading(0, text="热键")
        self.__treeview.heading(1, text="类别")
        self.__treeview.heading(2, text="指令")
        self.__treeview.column(0, width=200, anchor=CENTER)
        self.__treeview.column(1, width=200, anchor=CENTER)
        self.__treeview.column(2, width=1000, anchor=CENTER)

        # 功能控件
        cmd_control = ttk.Frame(self)
        ttk.Button(
            master=cmd_control, text='添加热键', command=self.__add, width=10, style='button_add.TButton').pack(pady=10)
        ttk.Button(
            master=cmd_control, text='删除热键', command=self.__del, width=10, style='button_del.TButton').pack(pady=10)
        ttk.Button(
            master=cmd_control, text='查找热键', command=self.__find, width=10, style='button_find.TButton').pack(pady=10)
        ttk.Button(
            master=cmd_control, text='修改热键', command=self.__find, width=10, style='button_re.TButton').pack(pady=10)

        cmd_control.pack(side=RIGHT, padx=20)
        info_control.pack(side=RIGHT, padx=20)
        self.__treeview.pack(side=LEFT, anchor=NE, fill=X)
        self.__treeview.bind('<Button-1>', lambda event: self.__focusing_in())

        self.protocol("WM_DELETE_WINDOW", self.exit)  # tk监听窗口关闭事件

    def __del(self):
        ...

    def __find(self):
        ...

    def __add(self):
        self.__config.write()
        print(self.__get_focusing(self.__focusing))

    def __revise(self):
        ...

    def __focusing_in(self):
        self.__focusing = self.__treeview.focus()
        # print(self.__config.result.get(self.__get_focusing(self.__focusing), None))

    def __get_focusing(self, focusing):
        """
        返回在快捷键Treeview中正在点击的快捷键
        :return: 快捷键Treeview中正在点击的快捷键
        """
        key_list = list(self.__config.result.keys())
        if focusing == '':
            return None
        else:
            focusing_key_index = int(focusing[1:], 16) - 1
        return key_list[focusing_key_index]

    def exit(self):
        self.__main_thread_running = False
        self.__main_thread.join(0.5)
        self.quit()


if __name__ == '__main__':
    test = Settings(title="", themename="flatly")
    test.mainloop()
