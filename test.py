from Tools import Tools

tools = Tools()
print(tools.format_unit(preset="kib", num=1024**2+100.10))
