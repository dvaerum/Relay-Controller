import sys

__author__ = 'alt_mulig'


debug = 2
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":
        debug = 1
    elif sys.argv[1] == "debug2":
        debug = 2


def my_print(*args, sep=' ', end='\n', file=None):
    if debug >= 1:
        print(*args, sep=sep, end=end, file=file)
        sys.stdout.flush()


def debug_print(*args, sep=' ', end='\n', file=None):
    if debug >= 2:
        print(*args, sep=sep, end=end, file=file)
        sys.stdout.flush()



def main():
    global debug
    debug = True
    my_print("tester", "1212", end='\n\n')


if __name__ == '__main__':
    main()
