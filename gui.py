import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from threading import Thread
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
        self.add_button = ttk.Button()
        self.find_button = ttk.Button()
        self.re_button = ttk.Button()
        self.del_button = ttk.Button()

        self.__yn_button_re = True
        self.button_style = None
        self.__config = config
        self.__focusing = ''
        self.__hooking = False
        self.__treeview = ttk.Treeview()
        #########################
        config.load()
        self.__config.result = config.result
        ########################
        if self.__config.result == {}:
            self.__config.result = self.__events
            result = self.__config.write()
            self.__check_runtype_write_log(result, "write config error")
        else:
            self.__events = self.__config.result
        self.__config.write()

        self.__main_thread_running = True
        self.__main_thread_cycle_time = 0.1
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
    def add_ui():
        key = ''

        def get_keys(event):
            nonlocal key
            keys_d = hooker.get_now_keys()
            key = '+'.join(keys_d['down'])
            msg_label.config(text=key)

        def ok():
            add_win.destroy()

        add_win = ttk.Window()
        add_win.geometry('300x200')
        add_win.title('HotLeyTools')
        add_win.resizable(False, False)
        ttk.Label(add_win, text="添加热键\n请点击按键以录入热键").pack()
        msg_label = ttk.Label(add_win, text="")
        msg_label.pack()
        ok_check = ttk.Frame(add_win)
        ttk.Button(ok_check, text="确认", command=ok).pack(side=LEFT)
        ttk.Button(ok_check, text="取消", command=ok).pack(side=LEFT)
        ok_check.pack(pady=20)
        hooker = Hooker({})
        hooker.hook_events()

        add_win.bind('<Any-Key>', get_keys)
        add_win.mainloop()
        # 检测快捷键，实时改变窗口
        # 录入快捷键 询问功能（创建功能选项卡）
        # 选择文件打开 : 创建选项文件窗口 / cmd 命令 输入文字窗口
        ...
        return str

    def __del(self):
        ...
        del self.__events[self.__get_focusing(self.__focusing)]
        self.__config.write()
        self.reload_treeview(self.__treeview)

    def __find(self):
        ...
        self.reload_treeview(self.__treeview)

    def __add(self):
        hot_key_dict = self.add_ui()
        # 通过获得的热键字典 添加热键至self.__events
        self.__config.write()
        print(self.__get_focusing(self.__focusing))
        self.reload_treeview(self.__treeview)

    def __revise(self):
        ...
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
            loger.debug(f'focusing           : {focusing}')
            loger.debug(f'focusing_key_index : {focusing_key_index}')
            loger.debug(f'key_list           : {key_list}\n')
        return key_list[focusing_key_index]

    def exit(self):
        self.__main_thread_running = False
        self.__main_thread.join(0.5)
        self.quit()


if __name__ == '__main__':
    test = Settings(title="", themename="flatly")
    test.mainloop()
