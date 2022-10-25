import sys
import locale
import ttkbootstrap as ttk
from subprocess import Popen, PIPE, STDOUT

coding = locale.getdefaultlocale()[1]
print(coding)


# str_io = StringIO()


class redirect:
    content = ""

    def write(self, str):
        self.content += str

    def flush(self):
        self.content = ""


r = redirect()
sys.stdout = r

root = ttk.Window(themename="flatly")

screen_size = root.winfo_screenwidth(), root.winfo_screenheight()
width, height = 896, 636
x, y = round((screen_size[0] - width) / 2), round((screen_size[1] - height) / 2)
root.resizable(width=False, height=False)
root.geometry(f"{width}x{height}+{x}+{y}")
root.title("Cmd输出")

textbox = ttk.Text()
textbox.pack()

out = 'NULL'
if len(sys.argv) >= 3:
    if sys.argv[1] in ('-S', '-E'):
        mode = sys.argv[1]
        info = ' '.join(sys.argv[2:])
        if mode == '-E':
            exec(info)
            out = r.content
        else:
            starting = Popen(info, stdout=PIPE, shell=True)
            starting.wait()
            out = starting.stdout.read().decode(coding)
            while starting.returncode != 0:
                out = starting.stdout.read().decode(coding)
                textbox.insert(1.0, chars=out)

    else:
        out = '参数错误'
else:
    out = '参数不足'

textbox.insert(1.0, chars=out)
textbox.configure(state='disabled')
root.mainloop()
