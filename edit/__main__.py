import terminal as term
from buffer import Buffer

term.setmode()

buffer = Buffer("test_file.py")

while True:
    buffer.render()
    try:
        buffer.editor()
    except KeyboardInterrupt:
        break

term.chf()
