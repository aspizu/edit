import sys
from termios import *
from shutil import get_terminal_size


def isascii(c: str) -> bool:
    return 32 <= ord(c) <= 126 or c in "\n\t"


# fmt: off
reset  = "\033[0m"
bold   = "\033[1m"
italic = "\033[3m"
ulined = "\033[4m"

black  = "\033[30m"
red    = "\033[31m"
green  = "\033[32m"
yellow = "\033[33m"
blue   = "\033[34m"
pink   = "\033[35m"
cyan   = "\033[36m"
white  = "\033[37m"

bgblack  = "\033[40m"
bgred    = "\033[41m"
bggreen  = "\033[42m"
bgyellow = "\033[43m"
bgblue   = "\033[44m"
bgpink   = "\033[45m"
bgcyan   = "\033[46m"
bgwhite  = "\033[47m"

brblack  = "\033[90m"
brred    = "\033[91m"
brgreen  = "\033[92m"
bryellow = "\033[93m"
brblue   = "\033[94m"
brpink   = "\033[95m"
brcyan   = "\033[96m"
brwhite  = "\033[97m"

brbgblack  = "\033[100m"
brbgred    = "\033[101m"
brbggreen  = "\033[102m"
brbgyellow = "\033[103m"
brbgblue   = "\033[104m"
brbgpink   = "\033[105m"
brbgcyan   = "\033[106m"
brbgwhite  = "\033[107m"
# fmt: on

width, height = get_terminal_size()


def f():
    sys.stdout.flush()


def w(s: str):
    sys.stdout.write(s)


def wf(s: str):
    w(s)
    f()


def m(x: int, y: int):
    w(f"\u001b[{y+1};{x+1}H")


def h():
    m(0, 0)


def c():
    w("\u001b[2J\u001b[3J")


def chf():
    c()
    h()
    f()


def setmode():
    """
    I don't know what the fuck this does but it does something to the terminal
    device as to not fuck me over.

    References:
      https://www.man7.org/linux/man-pages/man3/termios.3.html
      https://man7.org/linux/man-pages/man1/stty.1.html
      https://github.com/python/cpython/blob/3.10/Lib/tty.py
    """
    IFLAG = 0
    LFLAG = 3
    CC = 6
    mode = tcgetattr(sys.stdin)
    mode[LFLAG] = mode[LFLAG] & ~(ECHO | ICANON)
    mode[IFLAG] = mode[IFLAG] & ~(IXON | IXOFF)
    #                             ^^^^ Allow Ctrl+S and Ctrl+Q to be read
    mode[CC][VMIN] = 1
    mode[CC][VTIME] = 0
    tcsetattr(sys.stdin, TCSAFLUSH, mode)


def read() -> str:
    key = sys.stdin.read(1)
    if isascii(key) and key != "\t":
        return key
    elif key == "\t":
        return "TAB"
    elif key == "\x7f":
        return "BACKSPACE"
    elif key == "\x01":
        return "CTRL_A"
    elif key == "\x02":
        return "CTRL_B"
    elif key == "\x04":
        return "CTRL_D"
    elif key == "\x05":
        return "CTRL_E"
    elif key == "\x06":
        return "CTRL_F"
    elif key == "\x07":
        return "CTRL_G"
    elif key == "\x08":
        return "CTRL_H"
    elif key == "\x0b":
        return "CTRL_K"
    elif key == "\x0c":
        return "CTRL_L"
    elif key == "\x0e":
        return "CTRL_N"
    elif key == "\x0f":
        return "CTRL_O"
    elif key == "\x10":
        return "CTRL_P"
    elif key == "\x11":
        return "CTRL_Q"
    elif key == "\x12":
        return "CTRL_R"
    elif key == "\x13":
        return "CTRL_S"
    elif key == "\x14":
        return "CTRL_T"
    elif key == "\x15":
        return "CTRL_U"
    elif key == "\x16":
        return "CTRL_V"
    elif key == "\x17":
        return "CTRL_W"
    elif key == "\x18":
        return "CTRL_X"
    elif key == "\x19":
        return "CTRL_Y"
    elif key == "\x1b":
        key = sys.stdin.read(1)
        if key == "\t":
            return "ALT_TAB"
        elif key == "[":
            key = sys.stdin.read(1)
            if key == "1":
                key = sys.stdin.read(1)
                if key == ";":
                    key = sys.stdin.read(1)
                    if key == "2":
                        key = sys.stdin.read(1)
                        if key == "A":
                            return "SHIFT_UP_ARROW"
                        elif key == "B":
                            return "SHIFT_DOWN_ARROW"
                        elif key == "C":
                            return "SHIFT_RIGHT_ARROW"
                        elif key == "D":
                            return "SHIFT_LEFT_ARROW"
                    if key == "3":
                        key = sys.stdin.read(1)
                        if key == "A":
                            return "ALT_UP_ARROW"
                        elif key == "B":
                            return "ALT_DOWN_ARROW"
                        elif key == "C":
                            return "ALT_RIGHT_ARROW"
                        elif key == "D":
                            return "ALT_LEFT_ARROW"
                    if key == "5":
                        key = sys.stdin.read(1)
                        if key == "A":
                            return "CTRL_UP_ARROW"
                        elif key == "B":
                            return "CTRL_DOWN_ARROW"
                        elif key == "C":
                            return "CTRL_RIGHT_ARROW"
                        elif key == "D":
                            return "CTRL_LEFT_ARROW"
            elif key == "5":
                key = sys.stdin.read(1)
                if key == "~":
                    return "PG_UP"
            elif key == "6":
                key = sys.stdin.read(1)
                if key == "~":
                    return "PG_DOWN"
            elif key == "A":
                return "UP_ARROW"
            elif key == "B":
                return "DOWN_ARROW"
            elif key == "C":
                return "RIGHT_ARROW"
            elif key == "D":
                return "LEFT_ARROW"
            elif key == "H":
                return "HOME"
            elif key == "F":
                return "END"
            elif key == "Z":
                return "SHIFT_TAB"
        elif isascii(key):
            return f"ALT_{key}"
    return key
