#!/usr/bin/env python3
import curses
import os
import sys

logfile = open(sys.argv[1], 'w') if len(sys.argv) > 1 else None
ASCII_SHADING = ['.', ':', '-', '=', '+', '*', '#', '%', '@']
ASCII_LINES = ['/', '|', '\\', '-', '_', '=', '[', ']']
ASCII_NUMS = ['1','2','3','4','5','6','7','8','9','0']


def log(log_line):
    if logfile:
        logfile.write(log_line + "\n")
        logfile.flush()


def logf(log_line):
    if logfile:
        logfile.write(log_line)
        logfile.flush()


def main(stdscr):
    brush = len(ASCII_SHADING) - 1
    brush_pallet = ASCII_SHADING

    lines, cols = stdscr.getmaxyx()

    log("can change colors: " + str(curses.can_change_color()))
    log("COLORS: " + str(curses.COLORS))

    canvas_lines = lines - 2
    canvas = curses.newwin(canvas_lines, cols, 0, 0)
    command_line = curses.newwin(1, cols, canvas_lines + 1, 0)

    pallet_displayed = False

    canvas.keypad(True)

    def get_dimensions():
        nonlocal lines, cols, canvas_lines, command_line
        lines, cols = stdscr.getmaxyx()
        canvas_lines = lines - 2
        canvas.resize(canvas_lines, cols)
        command_line.resize(1, cols)
        command_line.mvwin(canvas_lines + 1, 0)
        draw_borders()

    def draw_borders():
        stdscr.hline(lines - 2, 0, '~', cols)
        stdscr.refresh()

    draw_borders()

    def left():
        (y, x) = canvas.getyx()
        if x >= 1:
            canvas.move(y, x - 1)

    def right():
        (y, x) = canvas.getyx()
        if x < cols - 1:
            canvas.move(y, x + 1)

    def up():
        (y, x,) = canvas.getyx()
        if y >= 1:
            canvas.move(y - 1, x)

    def down():
        (y, x) = canvas.getyx()
        if y < canvas_lines - 1:
            canvas.move(y + 1, x)

    def command():
        nonlocal pallet_displayed
        command_line.clear()
        pallet_displayed = False
        command_line.keypad(True)
        y, x = canvas.getyx()
        command_line.move(0, 0)
        command_line.insch(':')
        command_line.refresh()
        waiting_command = True
        while waiting_command:
            curses.echo(True)
            cmd = command_line.getch()
            if cmd == 27:
                command_cleanup(y, x)
                waiting_command = False
            elif cmd == ord('w'):
                command_line.clear()
                write(y, x)
                return
            elif cmd == ord('o'):
                command_line.clear()
                open_file(y, x)
                return
            elif cmd == ord('b'):
                change_brush_pallet(y, x)
                return
            elif cmd == ord('c'):
                clear(y, x)
                return

    def command_cleanup(last_y, last_x):
        curses.echo(False)
        command_line.clear()
        command_line.refresh()
        curses.flash()
        canvas.move(last_y, last_x)

    def arr_to_string(arr, y, x):
        str_builder = ""
        for i in range(y):
            for j in range(x):
                if arr[i][j]:
                    str_builder += chr(canvas.inch(i, j))
                else:
                    str_builder += " "
            str_builder += '\n'
        return str_builder

    def write(last_y, last_x):
        y, x = canvas.getmaxyx()
        chars = [[False for i in range(x)] for j in range(y)]
        log("y: " + str(len(chars)))
        log("x: " + str(len(chars[0])))

        for line in range(y):
            for col in range(x):
                if canvas.inch(line, col) != 32:
                    chars[line][col] = True

        text = arr_to_string(chars, y, x)

        curses.echo(True)
        command_line.insstr(0, 0, "write to: ")
        filename = command_line.getstr(0, 10).decode() + '.txt'
        path = '/Users/grimlock/pigeons/ascii_wizard'

        with open(os.path.join(path, filename), 'w') as file:
            file.write(str(y) + ':' + str(x) + '\n')
            file.write(text)

        command_cleanup(last_y, last_x)

    def open_file(last_y, last_x):
        canvas_max_y, canvas_max_x = canvas.getmaxyx()
        path = '/Users/grimlock/pigeons/ascii_wizard'
        command_line.insstr(0, 0, "open: ")
        filename = command_line.getstr(0, 6).decode() + '.txt'
        with open(os.path.join(path, filename), 'r') as file:
            canvas_size = file.readline()
            pic_max_y, pic_max_x = canvas_size.split(':')

            pic_max_y = int(pic_max_y)
            pic_max_x = int(pic_max_x)

            crop_y = pic_max_y > canvas_max_y
            crop_x = pic_max_x > canvas_max_x
            for trace_lines in range(pic_max_y | canvas_max_y if crop_y else pic_max_y):
                for trace_columns in range(pic_max_x | canvas_max_x if crop_x else pic_max_x):
                    canvas.insch(trace_lines, trace_columns, file.read(1))
                file.readline()

        command_cleanup(last_y, last_x)

    def change_brush_pallet(last_y, last_x):
        nonlocal brush_pallet, brush
        command_line.clear()
        command_line.insstr(0, 0, "pallet:")
        new_pallet = str(command_line.getstr(0, 7)).lower()
        if "shade" in new_pallet:
            brush_pallet = ASCII_SHADING
        elif "line" in new_pallet:
            brush_pallet = ASCII_LINES
        elif "num" in new_pallet:
            brush_pallet = ASCII_NUMS
        else:
            command_cleanup(last_y, last_x)

        if brush > len(brush_pallet) - 1:
            brush = len(brush_pallet) - 1

        command_cleanup(last_y, last_x)

    def clear(last_y, last_x):
        command_line.clear()
        command_line.addstr(0, 0, "for real? (Y/n):")
        command_line.refresh()

        confirm = str(chr(command_line.getch(0, 16))).lower()
        log(confirm)
        if "y" in confirm:
            canvas.clear()
            canvas.refresh()
        else:
            command_line.clear()
            command_line.addstr(0, 0, "clear aborted")

        command_cleanup(last_y, last_x)

    def cycle_brush(step):
        nonlocal brush, brush_pallet, pallet_displayed
        if (brush + step < len(brush_pallet)) & (brush + step >= 0):
            brush += step;
            pallet_displayed = False

    def delete():
        (y, x) = canvas.getyx()
        canvas.delch(y, x)
        canvas.insch(y, x, 32)

    def paint():
        (y, x) = canvas.getyx()
        canvas.delch(y, x)
        canvas.insch(y, x, brush_pallet[brush])

    def display_pallet():
        nonlocal pallet_displayed
        command_line.clear()
        for i in range(len(brush_pallet)):
            if i == brush:
                command_line.insch(0, i + i, brush_pallet[i], curses.A_REVERSE)
            else:
                command_line.insch(0, i + i, brush_pallet[i])
        pallet_displayed = True
        command_line.refresh()

    while True:
        if not pallet_displayed:
            display_pallet()

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
            stdscr.clear()
        elif c == ord(' '):
            paint()
        elif c == ord('c'):
            command()
        elif c == ord('x'):
            delete()
        elif c == ord(':'):
            command()
        elif c == curses.KEY_SLEFT:
            cycle_brush(-1)
        elif c == curses.KEY_SRIGHT:
            cycle_brush(1)


curses.wrapper(main)
