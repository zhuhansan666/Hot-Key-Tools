import sys
import ttkbootstrap as ttk
from io import StringIO
from traceback import format_exc


argvs = sys.argv[1:]

stdout = StringIO(newline="\n")
sys.stdout = stdout

try:
    exec(argvs[0])
except IndexError:
    sys.exit(-1)
except Exception as e:
    print(f"运行发生错误: {format_exc()}")

sys.stdout = sys.__stdout__

root = ttk.Window(themename="flatly")
root.title("Cmd输出")

textbox = ttk.Text()
textbox.insert(1.0, stdout.getvalue())  # 必须1.0, 不能1
textbox.configure(state='disabled')
textbox.pack()

screen_size = root.winfo_screenwidth(), root.winfo_screenheight()
width, height = 896, 636
x, y = round((screen_size[0] - width) / 2), round((screen_size[1] - height) / 2)
root.resizable(width=False, height=False)
root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == '__main__':
    root.update()
    root.mainloop()
    sys.exit(0)
