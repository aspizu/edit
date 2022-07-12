from typing import Union
import terminal as term


def isid(c: str) -> bool:
    return c.isalnum() or c in "_"


def render_buffer(
    buf: list[str],
    cx,
    cy,
    sx1,
    sy1,
    sx2,
    sy2,
    scroll,
    errs: dict[int, str],
    self,
):
    term.chf()
    color = term.white
    quoted = False
    y = scroll
    while y < min(term.height - 1 + scroll, len(buf)):
        if cy == y:
            term.w(term.bgblack)
        elif y in errs:
            term.w(term.bgred)
        term.w(str(1 + y).rjust(3) + " " + color)
        x = 0
        while x < len(buf[y]):
            if sx1 + sy1 + sx2 + sy2 != 0:
                if x == sx1 and y == sy1:
                    color = term.bgwhite + term.black
                    term.w(color)
                elif x == sx2 and y == sy2:
                    color = term.white + term.bgblack
                    term.w(color)
            if quoted:
                term.w(buf[y][x])
                if buf[y][x] == '"':
                    quoted = False
                    color = term.white
                    term.w(color)
            else:
                if buf[y][x] == '"':
                    quoted = True
                    color = term.brgreen
                    term.w(color)
                elif buf[y][x] == "#":
                    term.w(term.brblack)
                term.w(buf[y][x])
            x += 1
        term.w(" " * (term.width - len(buf[y]) - 4) + "\n" + term.reset)
        y += 1
    term.w(term.bgwhite + term.black)
    term.w(f" -- INSERT --  {self.filename}  {1+self.cx}:{1+self.cy}".ljust(term.width))
    term.w(term.reset)
    term.m(4 + cx, cy - scroll)
    term.f()


class Buffer:
    def __init__(self, filename: str = None):
        self.filename: Union[str, None] = filename
        self.buf: list[str] = [""]
        self.errs: dict[int, str] = {}
        if self.filename:
            self.reload()
        self.cx: int = 0
        self.cy: int = 0
        self.scroll: int = 0
        self.sx1: int = 0
        self.sy1: int = 0
        self.sx2: int = 0
        self.sy2: int = 0

    def reload(self):
        with open(self.filename, "r") as fp:
            self.buf = fp.read().split("\n")

    def write(self):
        with open(self.filename, "w") as fp:
            fp.write("\n".join(self.buf))

    def render(s):
        render_buffer(
            s.buf, s.cx, s.cy, s.sx1, s.sy1, s.sx2, s.sy2, s.scroll, s.errs, s
        )

    def editor(self):
        key = term.read()
        functions = {
            # fmt: off
            # KEY COMBINATION    COMMAND
            # ---------------    -------
            "RIGHT_ARROW":       self.move_cursor_right,
            "LEFT_ARROW":        self.move_cursor_left,
            "CTRL_RIGHT_ARROW":  self.move_cursor_right_wb,
            "CTRL_LEFT_ARROW":   self.move_cursor_left_wb,
            "UP_ARROW":          self.move_cursor_up,
            "DOWN_ARROW":        self.move_cursor_down,
            "PG_UP":             self.scroll_up,
            "PG_DOWN":           self.scroll_down,
            "HOME":              self.move_cursor_home,
            "END":               self.move_cursor_end,
            "BACKSPACE":         self.delete,
            "SHIFT_RIGHT_ARROW": self.select_right,
            "SHIFT_LEFT_ARROW":  self.select_left,
            # fmt: on
        }
        if key in functions:
            functions[key]()
        elif term.isascii(key):
            self.insert(key)

    def cursor_rightbound(self):
        self.cx = min(len(self.buf[self.cy]), self.cx)

    def move_cursor_home(self):
        self.cx = 0

    def move_cursor_end(self):
        self.cx = len(self.buf[self.cy])

    def move_cursor_right(self):
        self.cx = min(len(self.buf[self.cy]), self.cx + 1)

    def move_cursor_left(self):
        self.cx = max(0, self.cx - 1)

    def move_cursor_left_wb(self):
        self.move_cursor_left()
        if self.cx == len(self.buf[self.cy]):
            return
        flag = self.buf[self.cy][self.cx].isalnum()
        while 0 < self.cx and self.buf[self.cy][self.cx].isalnum() == flag:
            self.move_cursor_left()

    def move_cursor_right_wb(self):
        self.move_cursor_right()
        if self.cx == len(self.buf[self.cy]):
            return
        flag = self.buf[self.cy][self.cx].isalnum()
        while (
            self.cx < len(self.buf[self.cy])
            and self.buf[self.cy][self.cx].isalnum() == flag
        ):
            self.move_cursor_right()

    def move_cursor_down(self):
        self.cy = min(len(self.buf) - 1, self.cy + 1)
        self.cursor_rightbound()
        if self.cy - term.height + 5 > self.scroll:
            self.scroll_down()

    def move_cursor_up(self):
        self.cy = max(0, self.cy - 1)
        self.cursor_rightbound()
        if self.cy - 5 < self.scroll:
            self.scroll_up()

    def scroll_up(self):
        self.scroll = max(0, self.scroll - 1)

    def scroll_down(self):
        self.scroll += 1

    def insert(self, c: str):
        ln = self.buf[self.cy]
        if c == "\n":
            right = ln[self.cx :]
            left = ln[: self.cx]
            self.buf[self.cy] = right
            self.buf.insert(self.cy, left)
            self.cy += 1
            self.cx = 0
            return
        self.buf[self.cy] = ln[: self.cx] + c + ln[self.cx :]
        self.move_cursor_right()

    def delete(self):
        if self.cx == 0:
            if self.cy == 0:
                return
            self.cx = len(self.buf[self.cy - 1])
            self.buf[self.cy - 1] += self.buf.pop(self.cy)
            self.cy -= 1
            return
        ln = self.buf[self.cy]
        self.buf[self.cy] = ln[: self.cx - 1] + ln[self.cx :]
        self.move_cursor_left()

    def select_right(self):
        ...

    def select_left(self):
        ...
