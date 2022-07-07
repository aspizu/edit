import sys
import shutil


def setmode():
    """
    I don't know what the fuck this does but it does something to the terminal
    device as to not fuck me over.

    References:
      https://www.man7.org/linux/man-pages/man3/termios.3.html
      https://man7.org/linux/man-pages/man1/stty.1.html
      https://github.com/python/cpython/blob/3.10/Lib/tty.py
    """
    import termios

    IFLAG = 0
    LFLAG = 3
    CC = 6
    mode = termios.tcgetattr(sys.stdin)
    mode[LFLAG] = mode[LFLAG] & ~(termios.ECHO | termios.ICANON)
    mode[IFLAG] = mode[IFLAG] & ~(termios.IXON)
    #                                     ^^^^ Allow Ctrl+S and Ctrl+Q to be read
    mode[CC][termios.VMIN] = 1
    mode[CC][termios.VTIME] = 0
    termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, mode)


setmode()


class TC:
    """Terminal colors"""

    # Formatting
    rst = "\u001b[0m"

    # Regular Foreground
    blk = "\u001b[30m"
    red = "\u001b[31m"
    grn = "\u001b[32m"
    ylw = "\u001b[33m"
    blu = "\u001b[34m"
    pnk = "\u001b[35m"
    cyn = "\u001b[36m"
    wht = "\u001b[37m"

    # Bright Foreground
    blk_ = "\u001b[90m"
    red_ = "\u001b[91m"
    grn_ = "\u001b[92m"
    ylw_ = "\u001b[93m"
    blu_ = "\u001b[94m"
    pnk_ = "\u001b[95m"
    cyn_ = "\u001b[96m"
    wht_ = "\u001b[97m"

    # Regular Background
    blk__ = "\u001b[40m"
    red__ = "\u001b[41m"
    grn__ = "\u001b[42m"
    ylw__ = "\u001b[43m"
    blu__ = "\u001b[44m"
    pnk__ = "\u001b[45m"
    cyn__ = "\u001b[46m"
    wht__ = "\u001b[47m"

    # Bright Background
    blk___ = "\u001b[40m"
    red___ = "\u001b[41m"
    grn___ = "\u001b[42m"
    ylw___ = "\u001b[43m"
    blu___ = "\u001b[44m"
    pnk___ = "\u001b[45m"
    cyn___ = "\u001b[46m"
    wht___ = "\u001b[47m"


class TerminalInterface:
    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.width: int
        self.height: int
        self.width, self.height = self.size()

    def f(self):
        sys.stdout.flush()
        return self

    def w(self, s: str):
        sys.stdout.write(s)
        return self

    def wf(self, s: str):
        sys.stdout.write(s)
        sys.stdout.flush()
        return self

    def m(self, x: int, y: int):
        self.x = x + 1
        self.y = y + 1
        self.w(f"\u001b[{y+1};{x+1}H")
        return self

    def c(self):
        self.w("\u001b[2J\u001b[3J")
        return self

    def chf(self):
        return self.c().m(0, 0).f()

    def size(self) -> tuple[int, int]:
        """return (width, height)"""
        return shutil.get_terminal_size()


def readkey() -> str:
    a: str
    a = sys.stdin.read(1)
    if a == "\x1b":
        a = sys.stdin.read(2)
        if a == "[1":
            a = sys.stdin.read(3)
        elif a in ("[5", "[6"):
            sys.stdin.read(1)
    return a


class Buffer:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.msg = ""
        self.ter: TerminalInterface = TerminalInterface()
        self.cx: int = 0
        self.cy: int = 0
        self.scroll: int = 0
        self.buf: list[str] = []
        self.reload()

    def reload(self):
        with open(self.filename, "r") as fp:
            self.buf = fp.read().split("\n")

    def save(self):
        with open(self.filename, "w") as fp:
            fp.write("\n".join(self.buf))

    def run(self):
        while True:
            self.render()
            try:
                self.keyhandle()
            except KeyboardInterrupt:
                break
        self.ter.chf()

    def render(self):
        self.ter.chf()
        for y, line in enumerate(
            self.buf[self.scroll : self.scroll + self.ter.height - 1]
        ):
            self.ter.w(
                (TC.blk__ if (self.cy == self.scroll + y) else "")
                + TC.blk_
                + str(1 + self.scroll + y).rjust(4)
                + " "
                + TC.wht
                + line[: self.ter.width - 5].ljust(self.ter.width - 5)
                + "\n"
                + TC.rst
            )
        self.ter.wf(
            f"{TC.blu__} -- INSERT --   {self.cx}:{self.cy}  {self.msg}".ljust(
                self.ter.width + 5
            )
            + TC.rst
        )
        self.ter.m(5 + self.cx, self.cy - self.scroll).f()

    def keyhandle(self):
        key = readkey()
        self.msg = repr(key)
        if key == "[C":
            self.move_cursor_right()
        elif key == "[D":
            self.move_cursor_left()
        elif key == ";5C":
            self.move_cursor_right_word()
        elif key == ";5D":
            self.move_cursor_left_word()
        elif key == "[A":
            self.move_cursor_up()
        elif key == "[B":
            self.move_cursor_down()
        elif key == "[F":
            self.move_end()
        elif key == "[H":
            self.move_home()
        elif key == "[6":
            self.scroll_down()
        elif key == "[5":
            self.scroll_up()
        elif ord(" ") <= ord(key) <= ord("~"):
            self.insert_char(key)
        elif key == "\x7f":
            self.delete()
        elif key == "\n":
            self.insert_linebreak()
        elif key == "\x13":
            self.save()
        elif key == "\t":
            for i in range(4):
                self.insert_char(" ")

    def move_rightbound(self):
        self.cx = min(len(self.buf[self.cy]), self.cx)

    def move_cursor_right(self):
        self.cx = min(len(self.buf[self.cy]), self.cx + 1)

    def move_cursor_left(self):
        self.cx = max(0, self.cx - 1)

    def move_cursor_right_word(self):
        self.move_cursor_right()
        if self.cx < len(self.buf[self.cy]) and self.buf[self.cy][self.cx].isalpha():
            self.move_cursor_right_word()

    def move_cursor_left_word(self):
        self.move_cursor_left()
        if 0 < self.cx and self.buf[self.cy][self.cx].isalpha():
            self.move_cursor_left_word()

    def move_cursor_down(self):
        self.cy = min(len(self.buf) - 1, self.cy + 1)
        self.move_rightbound()
        if self.cy - self.ter.height + 5 > self.scroll:
            self.scroll_down()

    def move_cursor_up(self):
        self.cy = max(0, self.cy - 1)
        self.move_rightbound()
        if self.cy - 5 < self.scroll:
            self.scroll_up()

    def insert_char(self, char: str):
        line = self.buf[self.cy]
        self.buf[self.cy] = line[: self.cx] + char + line[self.cx :]
        self.move_cursor_right()

    def delete(self):
        # Delete linebreak
        if self.cx == 0:
            if self.cy != 0:
                line = self.buf.pop(self.cy)
                self.cy -= 1
                self.cx = len(self.buf[self.cy])
                self.buf[self.cy] += line
        # Delete indentation
        elif 4 <= self.cx and self.buf[self.cy][self.cx - 4 : self.cx] == " " * 4:
            for i in range(4):
                self.delete_char()
        else:
            self.delete_char()

    def delete_char(self):
        line = self.buf[self.cy]
        self.buf[self.cy] = line[: self.cx - 1] + line[self.cx :]
        self.move_cursor_left()

    def insert_linebreak(self):
        left = self.buf[self.cy][: self.cx]
        right = self.buf[self.cy][self.cx :]
        self.buf[self.cy] = right
        self.buf.insert(self.cy, left)
        self.move_cursor_down()
        self.cx = 0

    def move_end(self):
        self.cx = len(self.buf[self.cy])

    def move_home(self):
        self.cx = 0

    def scroll_up(self):
        self.scroll = max(0, self.scroll - 1)

    def scroll_down(self):
        self.scroll += 1


BUF = Buffer(sys.argv[1])
BUF.run()
