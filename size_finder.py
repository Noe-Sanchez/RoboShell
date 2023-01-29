import curses
w = curses.initscr()

for i in range(5000, 0, -1):
    try:
        curses.newwin(1, i)
        print("Columns", i)
        break
    except Exception as e:
        pass
for i in range(5000, 0, -1):
    try:
        curses.newwin(i, 1)
        print("Lines",i)
        break
    except Exception as e:
        pass
exit()