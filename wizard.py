import curses
import sys

logfile = open(sys.argv[1], 'w') if len(sys.argv) > 1 else None
ascii_ramp = {' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'}


def log(log_line):
    if logfile:
        logfile.write(log_line + "\n")
        logfile.flush()


def main(stdscr):
    lines, cols = stdscr.getmaxyx()

    canvas_height = int(lines * 2 / 3)
    bottom_hud_height = lines - canvas_height - 1

    canvas_width = int(cols * 2 / 3)
    side_hud_width = cols - canvas_width - 1

    log("can change colors: " + str(curses.can_change_color()))
    log("COLORS: " + str(curses.COLORS))

    def resize_window_dimensions():
        nonlocal canvas_height, bottom_hud_height, canvas_width, side_hud_width
        canvas_height = int(lines * 2 / 3)
        bottom_hud_height = lines - canvas_height - 1

        canvas_width = int(cols * 2 / 3)
        side_hud_width = cols - canvas_width - 1

    canvas = curses.newwin(canvas_height, canvas_width, 0, 0)
    bottom_hud = curses.newwin(bottom_hud_height, canvas_width, canvas_height + 3, 0)
    side_hud = curses.newwin(canvas_height, side_hud_width, 0, canvas_width + 3)

    dimensions_h = curses.newwin(2, canvas_width, canvas_height + 1, 0)
    dimensions_v = curses.newwin(canvas_height, 2, 0, canvas_width + 1)

    v_border_line = curses.newwin(lines, 1, 0, canvas_width)
    h_border_line = curses.newwin(1, cols, canvas_height, 0)

    color_square = curses.newwin(bottom_hud_height, side_hud_width, canvas_height + 1, canvas_width + 1)

    cell_array = [[(1000, 1000, 1000) for x in range(canvas_width)] for y in range(canvas_height)]

    def draw_hud_borders():
        v_border_line.vline('|', lines)
        h_border_line.hline('-', cols)

        v_border_line.insch(canvas_height, 0, '+')

        h_border_line.refresh()
        v_border_line.refresh()

    draw_hud_borders()

    def draw_canvas_dimensions():
        for i in range(canvas_width):
            char = chr(65 + (i % 26))
            dimensions_h.insch(0, i, char)
            dimensions_h.insch(1, i, str(int(i / 26)))

        for i in range(canvas_height):
            dimensions_v.insch(i, 0, str(int(i / 10 % 10)))
            dimensions_v.insch(i, 1, str(int(i % 10)))

        dimensions_v.refresh()
        dimensions_h.refresh()

    draw_canvas_dimensions()

    canvas.keypad(True)

    def draw_color_splotch():
        y, x = color_square.getmaxyx()
        log(str(x) + ' | ' + str(y))
        center_x = int(x / 2)
        center_y = int(y / 2)
        iter = int(x / 6) | int(y / 6) if y < x else int(x / 6)
        draw_start_y = center_y - iter

        for i in range(iter):
            draw_start_x = center_x - (1 + 2 * (i - 1))
            for j in range(2 + (4 * (i - 1))):
                color_square.insch(draw_start_y + i, draw_start_x + j, ' ', curses.A_REVERSE)

        for i in range(2 + (4 * (iter - 1))):
            color_square.insch(center_y, center_x - (1 + 2 * (iter - 1)) + i, ' ', curses.A_REVERSE)
        draw_start_y = center_y + iter

        for i in range(iter):
            draw_start_x = center_x - (1 + 2 * (i - 1))
            for j in range(2 + (4 * (i - 1))):
                color_square.insch(draw_start_y - i, draw_start_x + j, ' ', curses.A_REVERSE)

        color_square.refresh()

    draw_color_splotch()

    def reset_windows():
        nonlocal bottom_hud, canvas, side_hud
        bottom_hud.resize(bottom_hud_height, cols)
        canvas.resize(canvas_height, cols)
        side_hud.resize(canvas_height, side_hud_width)
        draw_hud_borders()

    def print_coords():
        (y, x) = canvas.getyx()
        x_location = str(chr((x % 26) + 65)) + str(int(x / 26))
        y_location = str(int(y / 10 % 10)) + str(int(y % 10))
        readout = x_location + ", " + y_location
        color_square.addstr(0, 1, readout)
        color_square.refresh()

    def get_dimensions():
        nonlocal lines, cols
        lines, cols = stdscr.getmaxyx()

    def left():
        (y, x) = canvas.getyx()
        if x >= 1:
            canvas.move(y, x - 1)

    def right():
        (y, x) = canvas.getyx()
        if x < canvas_width - 1:
            canvas.move(y, x + 1)

    def up():
        (y, x,) = canvas.getyx()
        if y >= 1:
            canvas.move(y - 1, x)

    def down():
        (y, x) = canvas.getyx()
        if y < canvas_height - 1:
            canvas.move(y + 1, x)

    def command():
        cmd = canvas.getch()

    def paint():
        (y, x) = canvas.getyx()
        canvas.delch(y, x)
        canvas.insch(y, x, ' ', curses.A_REVERSE)

    def delete():
        (y, x) = canvas.getyx()
        canvas.delch(y, x)

    while True:
        print_coords()
        c = canvas.getch()
        if c == curses.KEY_LEFT or c == ord('h'):
            left()
        elif c == curses.KEY_RIGHT or c == ord('l'):
            right()
        elif c == curses.KEY_UP or c == ord('k'):
            up()
        elif c == curses.KEY_DOWN or c == ord('j'):
            down()
        elif c == curses.KEY_RESIZE:
            log('lines = ' + str(lines) + "| cols = " + str(cols))
            get_dimensions()
            resize_window_dimensions()
            reset_windows()
        elif c == ord(' '):
            paint()
        elif c == ord('c'):
            command()
        elif c == ord('x'):
            delete()


curses.wrapper(main)
