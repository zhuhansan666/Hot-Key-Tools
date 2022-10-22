# Python Wheels Import
from os import path as os_path
from os import makedirs, remove
from sys import argv
from json import dumps, loads, JSONDecodeError
from math import ceil


# My Files Import

# End Import


class Tools:
    def __init__(self):
        self.format_unit_presets = {
            "kb": {"TB": 1000 ** 3, "GB": 1000 ** 2, "MB": 1000, "KB": 1},
            "kib": {"TIB": 1024 ** 3, "GIB": 1024 ** 2, "MIB": 1024, "KIB": 1},
            "time": {"day": 3600 * 24, "hour": 3600, "min": 60, "second": 1, "MS": 0.001}
        }

    @staticmethod
    def get_current_path():
        p = os_path.normpath(argv[0])
        p = os_path.split(p)[0]
        if len(p) > 0:
            return p
        else:
            return "./"

    @staticmethod
    def is_num(string: str, _type: str = "float"):
        """
        判断字符串是否为合法数字字符
        :param string: 字符串
        :param _type: 类型, float / int
        :return: True / False
        """
        try:
            num = float(string)
            if _type == "int":
                if num % 1 == 0:
                    return True
                else:
                    return False
            elif _type == "float":
                return True
        except Exception as e:
            return False

    def format_unit(self, preset: str = None, units: dict = None, num: float = None, target_num: float = 0.9,
                    sep=" ", sep_unit="", auto_fill: bool = True) -> tuple:
        """
        格式化数字单位 (如TB、GB、MB、KB)
        :param preset: 预设, 为None使用units
        :param units: 单位dict (如 {"TB": 1000*1000*1000, "GB": 1000*1000, "MB": 1000, "KB": 1}) (单位必须从大到小)
        :param num: 数值
        :param target_num: 单位最小值目标, 大于此值即视为此单位合适
        # :param keep_figures: 保留的位数
        :param sep: 分割单位的字符
        :param sep_unit: 分割单位与数字的字符
        :param auto_fill: 自动填充为0的单位
        :return: ((num, 单位, num, 单位...), 格式化完的string, 单位间以sep分割) / ((), error_info), 剩余的num
        """
        if preset is None and units is None:
            return (), "未使用预设或未使用手动"
        elif num is None:
            return (), "num 不能为 None"
        else:
            if units is None:
                _units = self.format_unit_presets.get(preset.lower(), None)
                if units is None and _units is None:
                    return (), "预设未找到且未使用手动"
                elif units is not None and _units is None:
                    print("WARING: 未找到预设现已使用手动")
                units = _units

            result_string = ""
            result_lst = []
            unit = ""
            for unit, mathsort in units.items():
                if mathsort == 0:
                    mathsort = 1
                _num = num / mathsort  # 当前值

                if _num > target_num:
                    _num_ceil = ceil(_num)
                    if abs(_num_ceil - _num) < 1E-6:  # 小于 1/10^6 视为向上的整数
                        _num = _num_ceil
                    else:
                        _num = int(_num)

                    result_lst.append(_num)
                    result_lst.append(unit)
                    result_string = f"{result_string}{sep}{_num}{sep_unit}{unit}"
                    num -= _num * mathsort  # 减去使用的值
                elif len(result_string) > 0 and auto_fill and num > 0:  # 自动填充在中间的为0的单位
                    result_string = f"{result_string}{sep}0{sep_unit}{unit}"

            sep_long = len(sep)
            result_string = result_string[sep_long:]  # 去除分割字符 (sep)
            if num < 0 or abs(num - 0) < 1E-6:
                num = 0
            # else:
                # print(num)
                # end_index = len(sep_unit)+len(unit)
                # result_string = result_string[:end_index] + "." + str(round(num, 3))[2:] + result_string[end_index:]
                # result_lst[-2] += round(num, 3)
            return tuple(result_lst), result_string, float(str(num)[:7])


class FileTools:
    @staticmethod
    def create_file(filename: str, encode: str = "UTF-8", mode: str = "w+", cover_file: bool = False,
                    def_info: str = ""):
        """
        创建文件
        :param filename: 文件绝对路径加包含后缀的文件名
        :param encode: 编码
        :param mode: 操作模式
        :param cover_file: 是否自动覆盖文件
        :param def_info: 默认内容
        :return [error code, error info / filename]
         error code 0 -> 成功,
         -1 -> 创建文件夹错误,
         -2 -> 创建文件错误,
         -3 -> 删除文件错误,
         -4 -> 未开启cover_file但文件存在,
         -5 -> 删除文件夹错误
        """
        path, file = os_path.split(filename)
        if not os_path.exists(path):
            try:
                makedirs(path)
            except Exception as e:
                return -1, e

        if not os_path.exists(filename):
            pass
        else:
            if os_path.isdir(filename):
                try:
                    remove(filename)
                except Exception as e:
                    return -5, e
            else:
                if cover_file:
                    try:
                        remove(filename)
                    except Exception as e:
                        return -3, e
                else:
                    return -4, f"{filename} 存在"

        try:
            with open(filename, mode, encoding=encode) as f:
                f.write(def_info)
            return 0, filename
        except Exception as e:
            return -2, e

    @staticmethod
    def read_file(filename: str, encode: str = "UTF-8", mode: str = "r+"):
        """
        读取文件
        :param filename: 文件名
        :param encode: 文件编码
        :param mode: 读取模式
        :return: tuple(error code, error / file info)
        error code: 0 -> 正常, -1 -> 错误
        """
        try:
            with open(filename, mode, encoding=encode) as f:
                r = f.read()
            return 0, r
        except Exception as e:
            return -1, e

    def read_json(self, filename, encode: str = "UTF-8", mode: str = "r+"):
        """
        读取 json 文件
        :param filename: 文件名
        :param encode: 文件编码
        :param mode: 读取模式
        :return: tuple(error code, error / file info)
        error code: 0 -> 正常, -1 -> 文件读取错误, -2 -> 将json加载为dict错误
        """
        res = self.read_file(filename, encode, mode)
        if res[0] == 0:
            try:
                json_info = loads(res[1])
                return 0, json_info
            except JSONDecodeError as e:
                return -2, "Json load error: ".format(e)
            except Exception as e:
                return -1, e
        else:
            return res

    @staticmethod
    def write_file(filename, info: str, encode: str = "UTF-8", mode: str = "w+",
                   newline="\n"):
        """
        写入文件
        :param filename: 文件名
        :param info: 内容
        :param encode: 文件编码
        :param mode: 读取模式
        :param newline: 使用\n换行
        :return: tuple(error code, error / "Success")
        error code: 0 -> 正常, -1 -> 文件读取错误
        """
        try:
            with open(filename, mode, encoding=encode, newline=newline) as f:                f.write(info)
            return 0, "Success"
        except Exception as e:
            return -1, e

    def write_json(self, filename, info: dict, encode: str = "UTF-8", mode: str = "w+"):
        """
        写入 json 文件
        :param filename: 文件名
        :param info: 内容
        :param encode: 文件编码
        :param mode: 读取模式
        :return: tuple(error code, error / "Success")
        error code: 0 -> 正常, -1 -> 文件读取错误, -2 -> 将dict加载为json错误
        """
        try:
            json_info = dumps(info, indent=4)
        except Exception as e:
            return -2, e

        res = self.write_file(filename, json_info + "\n", encode, mode)

        return res

    def is_true_path(self, file, create: bool = False):
        """
        判断是否为一个合法的绝对路径 (注意会在实际路径上操作)
        :param file: 文件
        :param create: 是否创建 (即测试创建成功后是否删除你)
        :return: tuple (是否为合法路径, 是否创建成功)
        """
        try:
            res = self.create_file(file)
            if res[0] != 0 and res[0] != -4 and res[0] != -5:
                return False, False
            if not create:
                try:
                    remove(file)
                except Exception as e:
                    return True, False
            return True, True
        except Exception as e:
            return True, False
