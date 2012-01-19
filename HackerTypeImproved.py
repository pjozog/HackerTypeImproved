#!/usr/bin/env python

import os
import sys
import time
from threading import Thread

CHARS_PER_KEYPRESS = 30

#Reads a character from stdin, but doesn't echo to terminal
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

#Prints a string, character by character
class HackerTypePrinter:
    def __init__(self, string, delay=.02):
        self.string = string;
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
        self.getChar = GetCharUnix()

    def run(self):
        while True:
            char = self.getChar()
            if (len(self.l) < 1):
                self.l.append(char)

#Prints a file named fileName to the screen, as in Hollywood hacking scenes
class HackerType:
    def __init__(self, fileName):
        self.file = open(fileName, 'r')
        self._filecontent = self.file.readlines()
        self._filecontent = ''.join(self._filecontent)
        self._counter = 0
        self._getChar = GetCharUnix()
        self.queue = HackerTypeQueue()

    def __repr__(self):
        s = self._filecontent[self._counter:self._counter+CHARS_PER_KEYPRESS]
        self._counter += CHARS_PER_KEYPRESS
        return str(s)

    def run(self):
        self.queue.start()

        while True:
            if (len(self.queue.l) > 0):
                printer = HackerTypePrinter(self.__repr__(), .005)
                printer.write()
                self.queue.l.pop()

if __name__ == '__main__':
    hackerType = HackerType('HackerTypeImproved.py')
    hackerType.run()
