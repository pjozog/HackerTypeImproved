#!/usr/bin/env python

import os
import sys
import time
from threading import Thread

from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

CHARS_PER_KEYPRESS = 30

#Reads a character from stdin, but doesn't echo to terminal
class GetChar:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = GetCharWindows()
        except ImportError:
            try:
                self.impl = GetCharMacCarbon()
            except Exception, e:
                self.impl = GetCharUnix()

    def __call__(self): return self.impl()


class GetCharUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if (ch == '`'):
                sys.exit(0)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)
        return ch

class GetCharMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

class GetCharWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

#Prints a string, character by character
class HackerTypePrinter:
    def __init__(self, string, delay=.02):
        self.string = string
        self.delay = delay

    def __repr__(self):
        return self.string

    def write(self, f=sys.stdout):
        for char in self.string:
            if (char == '\n'):
                print '\r',
            f.write(char)
            f.flush()
            time.sleep(self.delay)

#Queues frantic keypresses from the user
class HackerTypeQueue(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.l = []
        self.getChar = GetChar()

    def run(self):
        while True:
            char = self.getChar()
            if (len(self.l) < 2):
                self.l.append(char)

#Prints a file named fileName to the screen, as in Hollywood hacking scenes
class HackerType:
    def __init__(self, fileName):
        self.file = open(fileName, 'r')
        lexer = get_lexer_for_filename(self.file.name)
        self._filecontent = highlight(''.join(self.file.readlines()),
                                      lexer,
                                      TerminalFormatter())
        self._counter = 0
        self.queue = HackerTypeQueue()

    def __repr__(self):
        s = self._filecontent[self._counter:self._counter+CHARS_PER_KEYPRESS]
        self._counter += CHARS_PER_KEYPRESS
        return str(s)

    def run(self):
        self.queue.start()

        while True:
            if (len(self.queue.l) > 0):
                printer = HackerTypePrinter(self.__repr__(), .001)
                printer.write()
                self.queue.l.pop()

if __name__ == '__main__':

    if len(sys.argv) == 1:
        infile = sys.argv[0]
    else:
        infile = sys.argv[1]

    try:
        hackerType = HackerType(infile)
        hackerType.run()
    except ClassNotFound, e:
        print 'Error: %s does not appear to be source code.' % infile
        print 'How can you hack without source code?'
        print
        print
        print
        print '...idiot.'
