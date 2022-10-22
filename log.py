from os import makedirs, listdir, remove
from os.path import normpath, exists, join, isdir, basename, splitext, split, getsize
from os.path import split as ospath_split
from platform import platform, architecture, node, machine
from time import localtime, strftime, time
from types import FunctionType
from typing import Optional

from psutil import virtual_memory


class Logging:
    """
    日志写入
    """

    def __init__(self, log_file: str = None, full_log_file=None, log_def_info: FunctionType = None):
        """
        初始化日志写入
        :param log_file: log文件位置, 支持自动创建文件夹和文件
        :param full_log_file: 完整日志输出位置(即使用log_type = 2时输出的位置), 支持自动创建文件夹和文件
        :param log_def_info: 回调函数, 应返回默认写入(即创建文件时)的日志内容(末尾不会自动换行)
        """
        self.full_log_file = full_log_file
        self.__log_file_name = None
        self.__log_path = None
        self.__log_dir_created: bool = False

        self.log_file = "./log/$(now_time)$.log" if log_file is None else log_file

        self.time_f = "%Y-%m-%d"
        self.time_f_all = "%Y-%m-%d %H:%M:%S:$MS"
        self.default_encode = "utf-8"

        if log_def_info is not None:
            self.default_log_info = log_def_info()
        else:
            self.default_log_info = self.set_def_log_info()

        self.init()
        self.write_log(None)

    @staticmethod
    def set_def_log_info():
        try:
            from wmi import WMI

            w = WMI()

            gpu_lst = []
            for v in w.Win32_VideoController():
                gpu_lst.append(v.caption)

            cpu_lst = []
            for c in w.Win32_Processor():
                cpu_lst.append(c.name)

        except ImportError as e:
            cpu_lst = "Unknown: System does not support"
            gpu_lst = "Unknown: System does not support"

        try:
            mem = virtual_memory()
            total_mem = round(mem.total / 1024 / 1024 / 1024, 3)  # 转化为Gib
        except Exception as e:
            total_mem = "Unknown"

        return "{}\n{}\nsystem-version: {}\nsystem-bit: {}\ncpu-type: {}\ncomputer-name: {}" \
               "\ntotal-memory: {} Gib\nCPU: {}\nGPU: {}\n{}\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime()),
                                                                       "-" * 100, platform(),
                                                                       architecture()[0], machine(),
                                                                       node(), total_mem, str(cpu_lst), str(gpu_lst),
                                                                       "-" * 100)

    def init(self):
        self.__log_path = ospath_split(self.log_file)[0]
        self.__log_file_name = basename(self.log_file)

        log_path_file_list = splitext(self.__log_file_name)

        self.full_log_file = join(self.__log_path, log_path_file_list[0] + ".full" + log_path_file_list[1])

        if not exists(self.__log_path) or not isdir(self.__log_path):  # 没有log文件夹
            try:
                makedirs(self.__log_path)
                if exists(self.__log_path) and isdir(self.__log_path):
                    self.__log_dir_created = True
                else:
                    print(f"[{self.get_ftime_date()}] log文件夹 ({self.__log_path}) 创建失败: 未知错误")
            except Exception as e:
                print(f"[{self.get_ftime_date()}] log文件夹 ({self.__log_path}) 创建失败: {e}")
        else:
            self.__log_dir_created = True

    def get_ftime_date(self):
        return strftime(self.time_f, localtime())

    def get_ftime(self):
        res = strftime(self.time_f_all, localtime())
        return res.replace("$MS", "%03d" % int(time() % 1 * 100))

    def write_log(self, info: Optional[str], add_time: bool = True, log_type: int = 1, encoding: str = None,
                  filename: str = None):
        self.init()
        # 文件编码格式化
        encoding = encoding if encoding is not None else self.default_encode

        # log文件名称格式化
        if filename is not None:
            filename = filename.rstrip()
            filename = filename if filename[-4:] == ".log" else filename + ".log"

        # info内容格式化
        if info is not None:
            info = info if type(info) == str else str(info)
            info = info if info[-2:] == "\n" else info + "\n"
            info = info if add_time is not True else f"[{self.get_ftime()}] {info}"

        # 文件名初始化
        if log_type == 1:
            if filename is not None:
                _filename = join(self.__log_path, filename)
            else:
                _filename = self.log_file.replace("$(now_time)$", self.get_ftime_date())
        elif log_type == 2:
            if filename is not None:
                _filename = join(self.__log_path, filename)
            else:
                _filename = self.full_log_file.replace("$(now_time)$", self.get_ftime_date())
        else:
            print(f"[{self.get_ftime()}] log_type 错误, 已停止写入")
            return

        _filename = normpath(_filename)

        if not exists(_filename) and not isdir(_filename):
            try:
                with open(_filename, "w+", encoding=encoding) as cf:
                    cf.write(self.default_log_info)
            except Exception as e:
                print(f"[{self.get_ftime()}] {_filename} 创建失败: {e}")
        else:
            if not isdir(_filename):
                info = info if info is not None else ""
                try:
                    with open(_filename, "a+", encoding=encoding) as log_f:
                        log_f.write(info)
                except Exception as e:
                    print(f"[{self.get_ftime()}] {_filename} 写入失败: {e}")
            else:
                print(f"[{self.get_ftime()}] {_filename} 是一个文件夹")

    def clear_log(self, include_this: bool = False):
        """
        删除所有日志文件
        :param include_this: 为 True 时删除自身的log文件, False 时不删除
        :return: 共删除的文件大小 (kib)
        """
        try:
            files = listdir(self.__log_path)
        except Exception as e:
            print(f"读取当前文件夹错误: {e}")
            return

        total_filesize = 0
        for file in files:
            _filename = split(self.log_file.replace("$(now_time)$", self.get_ftime_date()))[-1]  # 当前log文件名
            _full_filename = split(self.full_log_file.replace("$(now_time)$", self.get_ftime_date()))[-1]  # 当前full_log

            if (file != _filename and file != _full_filename) or include_this:  # 如果不删除自己
                try:
                    filename = join(self.__log_path, file)
                    filesize = getsize(filename)
                    remove(filename)
                    total_filesize += filesize
                except Exception as e:
                    print(f"删除{file}错误: {e}")

        return total_filesize / 1024
