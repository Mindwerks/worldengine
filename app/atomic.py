#!/usr/bin/env python
#
# atomic.py
# Copyright (c) 2001, Chris Gonnerman
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions
# are met:
# 
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer. 
# 
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution. 
# 
# Neither the name of the author nor the names of any contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""atomic.py -- atomic name generator

This module knows how to generate "random" names for RPG characters.
It does this by "atomizing" a source file of words (generally names)
and then shuffling the atom file to generate a new list.  It does
often regenerate the source names, especially when the atom file is
small.

If run as a command-line program, use the following options:

    -r atomfile    -- read the given atom file and add to the
                      current atom table.
    -a sourcefile  -- read in and atomize the given source file
                      adding to the current atom table.
    -d atomfile    -- dump the current atom table to the given
                      output file.
    nnn            -- generate nnn (a number) names and print
                      on standard output.

Options are executed strictly in sequence as given.  To create an atom
file from a source file (for instance):

    python atomic.py -a file.src -d file

To generate names from an atom file:

    python atomic.py -r file 10

You can merge atom files using this module; just give multiple -a
options, followed by a -d if you want to dump the results, or just
a number to generate names using the composite.

As a module (to be imported) you get the following classes and functions:

    AtomFile (class)    -- a file wrapper with a disabled close() method,
                           used internally and probably not useful otherwise.
    atomopen (function) -- opens a file; takes filename and mode options,
                           searches the default atom file directory if not
                           found in current directory, handles "-" filenames,
                           and uses AtomFile to disable closing of sys.stdin/
                           sys.stdout.
    Atomic (class)      -- the meat of the matter.  An Atomic instance has
                           the following methods:

                                .insert(atom)  -- inserts an atom into 
                                                  the table.
                                .word(word)    -- breaks a word into
                                                  atoms and inserts them
                                                  into the table.
                                .atomize(file) -- atomize the given file,
                                                  which may be a file-like
                                                  object with a .readline()
                                                  method or a filename as a
                                                  string.  inserts words
                                                  found into the current 
                                                  table.
                                .load(file)    -- loads an atom file, using
                                                  semantics similar to the
                                                  .atomize() method.
                                .name()        -- generate one name and
                                                  return it.
                                .dump(file)    -- dumps the current table
                                                  into the given file-like
                                                  object or filename.
"""

__version__ = "1.0"

import string, re, sys, random

ATOMLEN = 4
WORDLEN = 12
ATOMDIR = "/usr/local/share/atomic"


class AtomFile:
    __file_attributes = ('closed','mode','name','softspace')
    def __init__(self, file):
        self.fd = file
    def close(self):
        pass
    def flush(self):
        return self.fd.flush()
    def isatty(self):
        return self.fd.isatty()
    def fileno(self):
        return self.fd.fileno()
    def read(self, *args):
        return apply(self.fd.read, args)
    def readline(self, *args):
        return apply(self.fd.readline, args)
    def readlines(self, *args):
        return apply(self.fd.readlines, args)
    def seek(self, *args):
        return apply(self.fd.seek, args)
    def tell(self):
        return self.fd.tell()
    def write(self, str):
        return self.fd.write(str)
    def writelines(self, list):
        return self.fd.writelines(list)
    def __repr__(self): 
        return repr(self.fd)
    def __getattr__(self, name):
        if name in self.__file_attributes:
            return getattr(self.fd, name)
        else:
            return self.__dict__[name]
    def __setattr__(self, name, value):
        if name in self.__file_attributes:
            setattr(self.fd, name, value)
        else:
            self.__dict__[name] = value
    def __cmp__(self, file):
        """I'm not sure what the correct behavior is, and therefore 
        this implementation is just a guess."""
        if type(file) == type(self.fd):
            return cmp(self.fd, file)
        else:
            return cmp(self.fd, file.fd)


class AtomReader:
    def __init__(self, file):
        self.file = file
        self.line = ""
    def next(self):
        self.line = self.file.readline()
        return self.line
    def close(self):
        return self.file.close()


def atomopen(filename, mode):
    if filename == "-":
        if "r" in mode:
            return AtomFile(sys.stdin)
        else:
            return AtomFile(sys.stdout)
    try:
        fp = open(filename, mode)
    except IOError:
        fp = None
    if "r" in mode and fp is None:
        fp = open(ATOMDIR + "/" + filename, mode)
    return fp
    

class Atomic:

    def __init__(self):
        self.atomtbl = {}

    def insert(self, atom):
        atom = string.lower(atom)
        if not self.atomtbl.has_key(atom[:ATOMLEN-1]):
            self.atomtbl[atom[:ATOMLEN-1]] = {}
        self.atomtbl[atom[:ATOMLEN-1]][atom[ATOMLEN-1]] = 1
    
    def word(self, word):
    
        l = len(word)
    
        if l < (ATOMLEN-1):
            return
    
        self.insert("." + word[:ATOMLEN-1])
    
        for i in range(0, l - (ATOMLEN-1)):
            self.insert(word[i:i+ATOMLEN])
    
        self.insert(word[-1*(ATOMLEN-1):] + ".")
    
    def dump(self, fp):
    
        if type(fp) is type(""):
            fp = atomopen(fp, "w")
        else:
            fp = AtomFile(fp)
    
        keys = self.atomtbl.keys()
        keys.sort()
    
        for i in keys:
            fp.write("%s:%s\n" % (i, string.join(self.atomtbl[i].keys(),"")))
    
        fp.close()
    
    def atomize(self, fp):
    
        if type(fp) is type(""):
            fp = atomopen(fp, "r")
        else:
            fp = AtomFile(fp)
    
        wre = re.compile("[^a-zA-Z'-]")
    
        rdr = AtomReader(fp)

        while rdr.next():
            lst = wre.split(rdr.line)
            lst = filter(lambda x: len(x) > (ATOMLEN-1), lst)
            for w in lst:
                self.word(w)
    
        fp.close()
    
    def load(self, fp):
        if type(fp) is type(""):
            fp = atomopen(fp, "r")
        else:
            fp = AtomFile(fp)
        rdr = AtomReader(fp)
        while rdr.next():
            line = rdr.line[:-1]
            key, data = string.split(line, ":")
            for d in data:
                self.insert(key + d)
        fp.close()
    
    def name(self):
    
        keys = self.atomtbl.keys()
        starts = filter(lambda x: x[0] == ".", keys)
    
        # find a start
        name = random.choice(starts)
    
        # process, looking for termination
    
        while 1:
            # find the next part
            p = self.atomtbl[name[-1*(ATOMLEN-1):]].keys()
            if len(name) > (WORDLEN * 2 / 3) and '.' in p:
                return name[1:]
            name += random.choice(p)
            if name[-1] == '.' or len(name) > WORDLEN:
                return name[1:-1]


if __name__ == "__main__":

    if len(sys.argv) <= 1:
        sys.stderr.write( \
            "Usage: atomic.py [ -r file ] [ -a file ] [ -d file ] [ nn ]\n")
        sys.exit(0)

    atom = Atomic()

    i = 1

    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "-r":
            i += 1
            atom.load(sys.argv[i])
        elif arg == "-a":
            i += 1
            atom.atomize(sys.argv[i])
        elif arg == "-d":
            i += 1
            atom.dump(sys.argv[i])
        else:
            n = int(sys.argv[i])
            lst = []
            for i in range(n):
                print atom.name()
        i += 1

