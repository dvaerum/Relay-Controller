import sys

__author__ = 'alt_mulig'


debug = False
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    debug = True


def my_print(*args, sep=' ', end='\n', file=None):
    if debug:
        print(*args, sep=sep, end=end, file=file)


def debug_print(*args, sep=' ', end='\n', file=None):
    if debug:
        print(*args, sep=sep, end=end, file=file)


def main():
    global debug
    debug = True
    my_print("tester", "1212", end='\n\n')


if __name__ == '__main__':
    main()