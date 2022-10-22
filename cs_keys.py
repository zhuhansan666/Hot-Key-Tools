from random import random, randint
import string

types = ['start', 'cmd']
crtl = 'ctrl'
control_keys = ['alt', 'shift', 'shift+alt', 'alt+shift', '']
# str(random.randint(1, 1000)): {'type': types[random.randint(0, 1)], 'info': str(random.random())},
__cs_keys = {

}


def cs_keys(count: int) -> dict:
    for v in range(count):
        __cs_keys[crtl + '+' + control_keys[randint(0, 2)] + '+' + string.ascii_lowercase[randint(0, 25)]] = {
            'type': "cmd",
            'info': 'ECHO ' + str(random())}
    return __cs_keys
