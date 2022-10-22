from os import getenv, path


class AppConfig:
    def __init__(self):
        appdata = getenv("appdata", None)
        if appdata is None:
            appdata = "./"
        else:
            appdata = path.join(appdata, "./Hot-Key-Tools")
        self.config_file = path.abspath(path.normpath(path.join(appdata, "./Config/Config.json")))

        self.log_file = None

        tmp = getenv("tmp", None)
        if tmp is None:
            tmp = "./"

        self.cmd_temppath = path.abspath(path.normpath(tmp))


if __name__ == '__main__':
    test = AppConfig()
    print(test.__dict__)
