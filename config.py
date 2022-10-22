from os import path as os_path
from threading import Thread
from json import dumps, loads
from time import sleep

from Tools import FileTools


class Config:
    """
    读取和操作配置文件
    """

    def __init__(self, file: str = None):
        """
        读取和操作配置文件 __init__
        :param file: 文件 [str]
        """
        # self.running = True
        self.loading = False
        self.writing = False

        self.result = {}
        self.inited = False
        self.__file_tools = FileTools()

        self.file = file

        self.__default_error = [0, "Success"]
        self.__error = [0, "Success"]
        self.__errors = []

        self.__dict = {}
        self.__str = {}

        self.init()

    def __init_error(self):
        self.__error = self.__default_error

    def __init_errors(self):
        self.__errors = []

    def __return_errors(self):
        if len(self.__errors) > 0:
            errors = self.__errors
            self.__errors = []
            return -1, errors
        else:
            return 0, []

    def __update_errors(self):
        if self.__error[0] != [0]:
            self.__errors.append(self.__error)
            self.__init_error()

    def __check_init(self):
        if not self.inited:
            self.__error = [-2, "Not inited."]
            self.__update_errors()
            return False
        else:
            return True

    def init(self):
        """
        初始化, 在创建object时传入文件名可不调用
        :return: None
        """
        self.__init_errors()
        try:
            self.file = os_path.abspath(self.file)
        except Exception as e:
            pass

        if self.file is None:
            self.__error = [-1, f"""\"self.file\" must be filepath, not \"{self.file}\""""]
            self.__update_errors()
        else:
            if os_path.exists(self.file):
                if os_path.isdir(self.file):
                    self.__error = [-2, """\"self.file\" must be file, file not \"dir\""""]
                    self.__update_errors()
                else:
                    self.inited = True
            else:
                # self.__error = [-2, f"""\"{self.file}\" not found"""]
                # self.__update_errors()
                self.__file_tools.create_file(self.file)

    def load(self):
        """
        加载 (重新加载)
        :return: (error_code[int, 0 正常], errors [list[Exception]]
        """
        self.__init_error()
        self.__init_errors()

        if not self.__check_init():
            return -1, self.__errors

        full_filename, file_suffix = os_path.splitext(self.file)
        if file_suffix == ".json":
            result = self.__file_tools.read_json(self.file)
            if result[0] != 0:
                self.__error = [-3, f"""\"{self.file}\" read error: {result[-1]}"""]
                self.__update_errors()
            else:
                result = result[-1]  # 将文件内容 (dict) 设置为 result
                self.__dict = result

                self.result = self.__dict
        else:
            self.__error = [-4, f"""WARING: file type \"{file_suffix}\" dose not support, it will open by text"""]
            self.__update_errors()

            result = self.__file_tools.read_file(self.file)
            if result[0] != 0:
                self.__error = [-3, f"""\"{self.file}\" read error (text mode): {result[-1]}"""]
                self.__update_errors()
            else:
                result = result[-1]

                self.__str = result  # 将文件内容 (str) 设置为 result

                self.result = self.__str

        return self.__return_errors()

    def __thread_load(self):
        self.loading = True
        self.load()
        self.loading = False

    def thread_load(self):
        """
        使用多线程load
        :return:
        """
        t = Thread(target=self.__thread_load, daemon=True)
        t.start()

        return self.__return_errors()

    def write(self):
        """
        写入或创建 配置文件
        :return: (error_code[int, 0 正常], errors [list[Exception]]
        """
        self.__init_error()
        self.__init_errors()

        # if not self.__check_init():
        #     return -1, self.__errors

        full_filename, file_suffix = os_path.splitext(self.file)
        if file_suffix == ".json":
            result = self.__file_tools.write_json(self.file, self.result)
            if result[0] != 0:
                self.__error = [-3, f"""\"{self.file}\" write error: {result[-1]}"""]
                self.__update_errors()

        else:
            self.__error = [-4, f"""WARING: file type \"{file_suffix}\" dose not support, it will open by text"""]
            self.__update_errors()

            if len(self.result) <= 0:
                self.result = ""

            result = self.__file_tools.write_file(self.file, self.result)
            if result[0] != 0:
                self.__error = [-3, f"""\"{self.file}\" read error (text mode): {result[-1]}"""]
                self.__update_errors()

        return self.__return_errors()

    def __thread_write(self):
        self.writing = True
        self.write()
        self.writing = False

    def thread_write(self):
        """
        使用多线程write
        :return:
        """
        t = Thread(target=self.__thread_write, daemon=True)
        t.start()

        return self.__return_errors()
