#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#UploadTool.py - Gestion des albums uploadés sur le serveur
#max-k <max-k@post.com>
#version 0.1 - python 3.4.3
#2015-07-27
#Require python-mutagen

upload_dir = "/data/data-zik/data/upload"
zik_dir = "/data/data-zik/data/ZIK"
user = 'root'
group = 'http'
dir_mode = 0o775
file_mode = 0o664

from os import listdir, makedirs, rename, walk, chown, chmod, sep
from os.path import isdir, isfile, join, splitext, basename, dirname, relpath
from sys import argv, exit
from time import sleep
from re import search, I
from pwd import getpwnam
from mutagen.flac import FLAC

class Directory:

    def __init__(self, name):
        self.name = name
        self.path = join(upload_dir, self.name)
        self.cover = isfile(join(self.path, 'cover.jpg'))
        self.tags = {}
        self.errors = []
        self.checkAll()

    def checkAll(self):
       if not self.cover:
           self.errors.append('Missing album art')
       self.checkTags()
       if 'genre' in self.tags:
           self.checkTarget()

    def checkTags(self):
        taglist = ['date', 'genre', 'album', 'artist']
        files = [f for f in listdir(self.path) if search("flac$", splitext(f)[1], I)]
        for filename in files:
            try:
                tags = FLAC(join(upload_dir, self.name, filename))
            except:
                self.errors.append("A track has no tag at all")
                return
            tracktags = {t: tags[t][0] for t in taglist if t in list(tags) and len(tags[t]) > 0}
            if len(list(tracktags)) != 4:
                self.errors.append("Required tag missing for at least one track")
                return
            if self.tags == {}:
                self.tags.update(tracktags)
            diff = [t for t in list(self.tags) if self.tags[t] != tracktags[t]]
            if len(diff) > 0:
                self.errors.append("Tags are different between tracks")
                return

    def checkTarget(self):
        for root, dirs, files in walk(zik_dir):
            depth = relpath(root, zik_dir).count(sep)
            if ((depth == 1 and basename(root) != 'Soundtrack') or (basename(root) == 'Soundtrack')) and self.name in dirs:
                _root = root
                if root != 'Soundtrack':
                    _root = dirname(root)
                self.errors.append("Target directory already exists in genre {}".format(basename(_root)))
        if self.tags['genre'] == 'Soundtrack':
            self.target = join(zik_dir, self.tags['genre'], self.name)
        else:
            self.target = join(zik_dir, self.tags['genre'], self.tags['artist'], self.name)

    def integrate(self):
        global dir_mode, file_mode, user, group
        if len(self.errors) == 0:
            if not isdir(dirname(self.target)):
                try:
                    makedirs(dirname(self.target))
                    for root, dirs, files in walk(dirname(dirname(self.target))):
                        chown(root, getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                        chmod(root, dir_mode)
                        for mydir in dirs:
                            chown(join(root, mydir), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                            chmod(join(root, mydir), dir_mode)
                        for myfile in files:
                            chown(join(root, myfile), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                            chmod(join(root, myfile), file_mode)
                except Exception as e:
                    self.errors.append('Unable to create target directory : {}'.format(e))
                    return
            try:
                rename(self.path, self.target)
                for root, dirs, files in walk(dirname(dirname(self.target))):
                    chown(root, getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                    chmod(root, dir_mode)
                    for mydir in dirs:
                        chown(join(root, mydir), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                        chmod(join(root, mydir), dir_mode)
                    for myfile in files:
                        chown(join(root, myfile), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                        chmod(join(root, myfile), file_mode)
            except Exception as e:
                directory.errors.append('Unable to move to target directory : {}'.format(e))

def verify(succeed):
    if len(succeed) == 0:
        print("\nNothing to verify")
        return
    print("\nDirectories tags verification :")
    for directory in succeed:
        print("\n   * {}".format(directory.name))
        print("    -> Genre : {}".format(directory.tags['genre']))
        print("    -> Artist : {}".format(directory.tags['artist']))
        print("    -> Year : {}".format(directory.tags['date']))
        print("    -> Album : {}".format(directory.tags['album']))
        print("    -> Target : {}".format(dirname(directory.target)))

def askConfirmation(directories):
    if len(directories) == 0:
        print("\nNo directory has been uploaded")
        return False
    print("\nSource directory : {}".format(upload_dir))
    print("Destination directory : {}".format(zik_dir))
    succeed = [d for d in directories if len(d.errors) == 0]
    failed = [d for d in directories if len(d.errors) > 0]
    if len(succeed) == 0:
        print("\nNothing to integrate")
    else:
        if len(succeed) == 1:
            print("\nFollowing directory will be integrated :\n")
        else:
            print("\nFollowing directories will be integrated :\n")
        for directory in succeed:
            print("   * {}".format(directory.name))
            print("    -> Target : {}".format(dirname(directory.target)))
    if len(failed) <= 1:
        print("\n {} directory will be skippped because of errors.".format(len(failed)))
    else:
        print("\n {} directories will be skippped because of errors.".format(len(failed)))
    answer = 'v'
    while answer.lower() == 'v':
        answer = input("\nWhat do you want to do ([p]roceed, [q]uit, [a]bort, [v]erify, show [e]rrors) ? ")
        if answer.lower() == 'v':
            verify(succeed)
        if answer.lower() == 'e':
            printFailed(directories)
        if answer.lower() not in ('a', 'p', 'q'):
            answer = 'v'
    if answer.lower() == 'p':
        return True
    return False

def printFailed(directories):
    failed = [d for d in directories if len(d.errors) > 0]
    if len(failed) == 0:
        print("\nNothing to show")
    else:
        if len(failed) == 1:
            print("\nFailed directory :\n")
        else:
            print("\nFailed directories :\n")
        for directory in failed:
            print("   * {}".format(directory.name))
            print("    -> Errors : {}".format("\n                ".join(directory.errors)))

def printSummary(directories, confirmation):
    succeed = [d for d in directories if len(d.errors) == 0]
    print("\n######## Summary ########\n")
    if len(succeed) > 0:
        _should = ''
        if confirmation == False:
            _should = 'should '
        if len(succeed) == 1 and confirmation == False:
            print("1 directory {}have been successfully integrated.\n".format(_should))
        elif len(succeed) == 1:
            print("1 directory has been successfully integrated.\n")
        else:
            print("{} directories {}have been successfully integrated.\n".format(len(succeed), _should))
    printFailed(directories)

def usage():
    print('\nUsage : `python UploadTool.py`')
    exit(1)

if __name__ == '__main__':

    if len(argv) != 1 or not isdir(upload_dir):
        usage()

    directories = []
    for _dir in listdir(upload_dir):
        directory = Directory(_dir)
        directories.append(directory)

    confirmation = askConfirmation(directories)
    if confirmation:
        for directory in directories:
            directory.integrate()

    printSummary(directories, confirmation)

    print("\nJob finished")
    exit(0)

