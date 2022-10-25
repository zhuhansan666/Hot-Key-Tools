import sys

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog as tkf
from threading import Thread
from typing import Union, Dict
from tkinter import messagebox
from time import time, sleep
import logging as log_out
from hooker import Hooker
from g import config, logging

log_out.basicConfig(level=log_out.DEBUG, style='{',  # filename='./DEBUG.LOG',
                    format='{pathname} [{asctime}] :\
                    \n\tfrom {funcName}() line({lineno}) {levelname}: {message}',
                    datefmt='%Y-%m-%d %H:%M:%S')
loger = log_out.getLogger('GUI-DEBUG')
loger.debug('2555555555')


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
        self.__main_obj = Hooker(self.__events)
        self.__main_obj.hook_keys()
        while self.__main_thread_running:
            t1 = time()
            result = self.__config.load()  # 读取config的内容
            self.__check_runtype_write_log(result, "write config error")
            self.__main_obj.reset(self.__events)
            self.__config.result = self.__events
            self.__config.write()
            sleep_time = time() - t1
            if sleep_time > self.__main_thread_cycle_time:
                sleep(sleep_time)
            else:
                sleep(self.__main_thread_cycle_time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # GUI 控件 值初始化
        self.add_button = ttk.Button()
        self.find_button = ttk.Button()
        self.re_button = ttk.Button()
        self.del_button = ttk.Button()

        # GUI 数据初始化
        self.__yn_button_re = True
        self.button_style = None
        self.__config = config
        self.__focusing = ''
        self.__hooking = False
        self.__treeview = ttk.Treeview()

        # 配置数据加载
        self.__config.load()
        if self.__config.result == {}:
            self.__config.result = {'ctrl+alt+o': {'type': 'cmd', 'info': 'echo This command of the ctrl+alt+o'}}
            result = self.__config.write()
            self.__check_runtype_write_log(result, "write config error")
        self.__events = self.__config.result
        self.__config.write()

        # Hooker 初始化
        self.__main_thread_running = True
        self.__main_thread_cycle_time = 0.1
        self.__main_thread = Thread(target=self.__main_thread_func, daemon=True)
        self.__main_thread.start()

        # GUI 控件
        self.init_controls()

    def init_controls(self):
        colors = [
            ""
        ]

        self.title(f"HotLeyTools - start from {time():.3f}")
        self.geometry('1400x650')
        self.resizable(False, False)
        # 显示信息的控件
        info_control = ttk.Frame(self)

        self.button_style = ttk.Style()
        self.button_style.configure('button_not.TButton', background='#c2c2c2')
        self.button_style.configure('button_add.TButton', background='#eb6864')
        self.button_style.configure('button_find.TButton', background='#007175')

        self.__treeview = ttk.Treeview(master=info_control, columns=['0', '1', '2'], show=HEADINGS, height=25)
        self.__treeview.heading(0, text="热键")
        self.__treeview.heading(1, text="类别")
        self.__treeview.heading(2, text="指令")
        self.__treeview.column(0, width=200, anchor=CENTER)
        self.__treeview.column(1, width=200, anchor=CENTER)
        self.__treeview.column(2, width=1000, anchor=CENTER)

        # 数据初始化
        self.reload_treeview(self.__treeview)

        # 功能控件
        cmd_control = ttk.Frame(self)
        self.add_button = ttk.Button(
            master=cmd_control, text='添加热键', command=self.__add, width=10, style='button_add.TButton')
        self.find_button = ttk.Button(
            master=cmd_control, text='查找热键', command=self.__find, width=10, style='button_find.TButton')
        self.re_button = ttk.Button(
            master=cmd_control, text='修改热键', command=self.__find, width=10, style='button_not.TButton')
        self.del_button = ttk.Button(
            master=cmd_control, text='删除热键', command=self.__del, width=10, style='button_not.TButton')

        # 控件显示
        self.add_button.pack(pady=10, ipadx=10, ipady=10, side=TOP, anchor=N)
        self.find_button.pack(pady=10, ipadx=10, ipady=10, side=TOP, anchor=N)
        self.re_button.pack(pady=10, ipadx=10, ipady=10, side=TOP, anchor=N)
        self.del_button.pack(pady=10, ipadx=10, ipady=10, side=TOP, anchor=N)

        cmd_control.pack(side=RIGHT, padx=20)
        info_control.pack(side=RIGHT, padx=20)
        self.__treeview.pack(side=LEFT, anchor=NE, fill=X)
        self.__treeview.bind('<Button-1>', lambda event: self.__focusing_in())

        self.protocol("WM_DELETE_WINDOW", self.exit)  # tk监听窗口关闭事件

    @staticmethod
    def add_ui() -> Union[Dict, None]:
        """
        添加热键的UI窗口函数
        :return :UI获得的新增热键 [dict]
        """
        # key = None
        # mode = None
        # start_file = None
        # cmd = None
        info = None

        def __get_key_str() -> str:
            """
            获取热键
            :return: 获取的热键 [str]
            """
            __key = ''

            def __run_ui():
                """获取热键的UI"""
                nonlocal __key

                def __get_keys(e):
                    nonlocal __key
                    __keys_d = __hooker.get_now_keys()
                    __key = '+'.join(__keys_d['down'])
                    __msg_label.config(text=__key)

                def __ok():
                    __add_win.quit()
                    __add_win.destroy()

                def __focus_set(e) -> None:
                    __msg.config(text='添加热键\n请点击按键以录入热键')

                __add_win = ttk.Window()
                __add_win.geometry('300x200')
                __add_win.title('HotLeyTools')
                __add_win.resizable(False, False)
                __msg = ttk.Label(__add_win, text="添加热键\n请点击此窗口")
                __msg.pack()
                __msg_label = ttk.Label(__add_win, text="")
                __msg_label.pack()
                __ok_check = ttk.Frame(__add_win)
                ttk.Button(__ok_check, text="确认", command=__ok).pack(side=LEFT)
                ttk.Button(__ok_check, text="取消", command=__ok).pack(side=LEFT)
                __ok_check.pack(pady=20)
                __hooker = Hooker({})
                __hooker.hook_events()
                __add_win.bind('<Any-Key>', __get_keys)
                __add_win.bind('<Button-1>', __focus_set)
                __add_win.mainloop()

            __run_ui()
            return __key

        def __get_mode() -> str:
            """
            获取模式
            :return: 获取的模式 [str]
            """
            __mode = ''

            def __run_ui():
                nonlocal __mode

                def __set_mode_start():
                    nonlocal __mode
                    __mode = 'start'
                    __ok()

                def __set_mode_cmd():
                    nonlocal __mode
                    __mode = 'cmd'
                    __ok()

                def __ok():
                    __add_win.quit()
                    __add_win.destroy()

                __add_win = ttk.Window()
                __add_win.geometry('300x200')
                __add_win.title('HotLeyTools')
                __add_win.resizable(False, False)
                ttk.Label(__add_win, text="请选择模式").pack()
                __ok_check = ttk.Frame(__add_win)
                ttk.Button(__ok_check, text="打开", command=__set_mode_start).pack(side=LEFT)
                ttk.Button(__ok_check, text="命令", command=__set_mode_cmd).pack(side=LEFT)
                __ok_check.pack(pady=20)
                ttk.Button(__add_win, text="取消", command=__ok).pack(side=RIGHT, padx=10)
                __add_win.mainloop()

            __run_ui()
            return __mode

        def __get_cmd():
            """
            获取命令
            :return: 获取的命令 [str]
            """
            __cmd = ''

            def __run_ui():
                nonlocal __cmd

                def __ok():
                    nonlocal __cmd
                    __cmd = __ent.get()
                    __add_win.quit()
                    __add_win.destroy()

                __add_win = ttk.Window()
                __add_win.geometry('300x200')
                __add_win.title('HotLeyTools')
                __add_win.resizable(False, False)
                ttk.Label(__add_win, text="请输入命令").pack()
                __ent = ttk.Entry(master=__add_win)
                __ent.pack()
                ttk.Button(__add_win, text="确认", command=__ok).pack(side=RIGHT, padx=10)
                __add_win.mainloop()

            __run_ui()
            return __cmd

        str_key = __get_key_str()
        loger.info(f"str_key: {str_key}")
        if str_key != '':
            str_mode = __get_mode()
            loger.info(f"str_mode: {str_mode}")
            if str_mode != '':
                if str_mode == 'start':
                    start_file = tkf.askopenfilename(title='请选择打开的文件')  # 获取要打开的文件路径
                    info = start_file
                elif str_mode == 'cmd':
                    cmd = __get_cmd()
                    info = cmd
                return {str_key: {'type': str_mode, 'info': info}}
        else:
            return None

        # 检测快捷键，实时改变窗口
        # 录入快捷键 询问功能（创建功能选项卡）
        # 选择文件打开 : 创建选项文件窗口 / cmd 命令 输入文字窗口

    def __add(self):
        hot_key_dict = self.add_ui()
        for key, type_info in hot_key_dict.items():
            self.__events[key] = type_info
        # 通过获得的热键字典 添加热键至self.__events
        self.__config.write()
        print(self.__get_focusing(self.__focusing))
        self.reload_treeview(self.__treeview)

    def __find(self):
        ...
        self.reload_treeview(self.__treeview)

    def __revise(self):
        ...
        if self.__yn_button_re:
            return None
        self.__config.write()
        self.reload_treeview(self.__treeview)

    def __del(self):
        ...
        if self.__yn_button_re:
            return None
        del self.__events[self.__get_focusing(self.__focusing)]
        self.__config.write()
        self.reload_treeview(self.__treeview)

    @staticmethod
    def __event_dict2tuple(events_dict):
        format_events_list = []
        for k, v in events_dict.items():
            func_type = v.get("type", "code")
            if func_type == "start":
                mode = "打开"
            elif func_type == "cmd":
                mode = "命令"
            else:
                mode = "源码"
            info = v.get("info", "")
            format_events_list.append((k, mode, info))
        return format_events_list

    @staticmethod
    def treeview_clear(treeview: ttk.Treeview):
        items = treeview.get_children()
        for item in items:
            treeview.delete(item)

    def reload_treeview(self, treeview: ttk.Treeview):
        t = Thread(target=lambda: self.__reload_treeview(treeview), daemon=True)
        t.start()

    def __reload_treeview(self, treeview: ttk.Treeview):
        self.__main_obj.reset(self.__events)
        loger.debug(f'self.__events : {self.__events}')
        self.treeview_clear(self.__treeview)
        events_list = self.__event_dict2tuple(self.__events)
        loger.debug(f'events_list: {events_list}')
        for v, i in zip(events_list, range(len(events_list))):
            treeview.insert("", END, values=v, iid=i)

    def __focusing_in(self):

        self.__focusing = self.__treeview.focus()
        if self.__yn_button_re and self.__get_focusing(self.__focusing):
            self.button_style.configure('button_re.TButton', background='#fff152')
            self.button_style.configure('button_del.TButton', background='#28b62c')

            self.re_button.configure(style='button_re.TButton')
            self.del_button.configure(style='button_del.TButton')

            self.__yn_button_re = False
        # print(self.__config.result.get(self.__get_focusing(self.__focusing), None))

    def __get_focusing(self, focusing):
        """
        返回在快捷键Treeview中正在点击的快捷键
        :return: 快捷键Treeview中正在点击的快捷键
        """
        key_list = list(self.__events)
        if focusing == '':
            return None
        else:
            focusing_key_index = int(focusing)
        return key_list[focusing_key_index]

    def exit(self):
        self.__main_thread_running = False
        self.__main_thread.join(0.5)
        self.quit()
        sys.exit(0)


if __name__ == '__main__':
    test = Settings(title="", themename="flatly")
    test.mainloop()
