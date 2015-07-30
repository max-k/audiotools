#!/usr/bin/env python
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
from shutil import rmtree
from sys import argv, exit
from time import sleep
from re import search, I
from pwd import getpwnam
from mutagen.flac import FLAC

def usage():
    print('\nUsage : `python UploadTool.py`')
    exit(1)

def checkCover(directory):
    global error
    if not isfile(join(upload_dir, directory, 'cover.jpg')):
        error="Missing album art"

def getTracks(directory):
    global error
    tracks = []
    for flacfile in listdir(join(upload_dir, directory)):
        if search("flac$", splitext(flacfile)[1], I):
            try:
                track = FLAC(join(upload_dir, directory, flacfile))
            except:
                error = "No tags found for file {}".format(flacfile)
                return []
            tracks.append(track)
    return tracks

def checkTags(tracks):
    global error
    for track in tracks:
        if 'date' not in track.keys():
            error = "Date tag is missing"
            return
        if 'genre' not in track.keys():
            error = "Genre tag is missing"
            return
        if 'album' not in track.keys():
            error = "Album tag is missing"
            return
        if 'artist' not in track.keys():
            error = "Artist tag is missing"
            return

def compareTags(tracks):
    global error
    for track in tracks[1:]:
        if track['date'][0] != tracks[0]['date'][0]:
            error = "Year tag is different between tracks"
            return
        if track['genre'][0] != tracks[0]['genre'][0]:
            error = "Genre tag is different between tracks"
            return
        if track['album'][0] != tracks[0]['album'][0]:
            error = "Album tag is different between tracks"
            return
        if track['artist'][0] != tracks[0]['artist'][0]:
            error = "Artist tag is different between tracks"
            return

def checkTarget(directory, tracks):
    global error
    for root, dirs, files in walk(zik_dir):
        depth = relpath(root, zik_dir).count(sep)
        if ((depth == 1 and dirname(root) != 'Soundtrack') or (basename(root) == 'Soundtrack')) and directory in dirs:
            _root = root
            if root != 'Soundtrack':
                _root = dirname(root)
            error = "Target directory already exists in genre {}".format(basename(_root))
    target = join(zik_dir, tracks[0]['genre'][0], tracks[0]['artist'][0], directory)
    if tracks[0]['genre'][0] == 'Soundtrack':
        target = join(zik_dir, tracks[0]['genre'][0], directory)
    return target

def checkDirectories(failed, succeed):
    global error
    error = None
    for directory in listdir(upload_dir):
        checkCover(directory)
        if error == None:
            tracks = getTracks(directory)
        if error == None:
            checkTags(tracks)
        if error == None:
            compareTags(tracks)
        if error == None:
            target = checkTarget(directory, tracks)
        if error == None:
            succeed.update({directory: {'tags': tracks[0], 'target': target}})
        else:
            failed.update({directory: {'error': error}})

def verifySucceed(succeed):
    if len(succeed) == 0:
        print("\nNothing to verify")
        return
    print("\nDirectories tags verification :")
    for directory in succeed.keys():
        print("\n   * {}".format(directory))
        print("    -> Genre : {}".format(succeed[directory]['tags']['genre'][0]))
        print("    -> Artist : {}".format(succeed[directory]['tags']['artist'][0]))
        print("    -> Year : {}".format(succeed[directory]['tags']['date'][0]))
        print("    -> Album : {}".format(succeed[directory]['tags']['album'][0]))
        print("    -> Target : {}".format(dirname(succeed[directory]['target'])))

def askConfirmation(failed, succeed):
    if len(failed) == 0 and len(succeed) == 0:
        print("\nNothing to upload")
        return False
    print("\nSource directory : {}".format(upload_dir))
    print("Destination directory : {}".format(zik_dir))
    if len(succeed) == 0:
        print("\nNothing to integrate")
    else:
        print("\nFollowing directories will be integrated :\n")
        for directory in succeed.keys():
            print("   * {}".format(directory))
            print("    -> Target : {}".format(succeed[directory]['target'][len(zik_dir):]))
    print("\n {} directories will be skippped because of errors.".format(len(failed)))
    answer = 'v'
    while answer.lower() == 'v':
        answer = input("\nWhat do you want to do ([p]roceed, [a]bort, [v]erify) ? ")
        if answer.lower() == 'v':
            verifySucceed(succeed)
        if answer.lower() not in ('a', 'p'):
            answer = 'v'
    if answer.lower() == 'p':
        return True
    succeed = {}
    return False

def integrateDirectories(failed, succeed):
    to_delete = []
    for directory in succeed.keys():
        source_dir = join(upload_dir, directory)
        target_dir = succeed[directory]['target']
        if not isdir(dirname(target_dir)):
            try:
                makedirs(dirname(target_dir))
                for root, dirs, files in walk(dirname(dirname(target_dir))):
                    chown(root, getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                    chmod(root, dir_mode)
                    for mydir in dirs:
                        chown(join(root, mydir), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                        chmod(join(root, mydir), dir_mode)
                    for myfile in files:
                        chown(join(root, myfile), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                        chmod(join(root, myfile), file_mode)
            except Exception as e:
                succeed[directory]['error'] = "Unable to create target directory : {}".format(e)
                failed.update({directory: succeed[directory]})
                to_delete.append(directory)
                continue
        try:
            rename(source_dir, target_dir)
            for root, dirs, files in walk(dirname(dirname(target_dir))):
                chown(root, getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                chmod(root, dir_mode)
                for mydir in dirs:
                    chown(join(root, mydir), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                    chmod(join(root, mydir), dir_mode)
                for myfile in files:
                    chown(join(root, myfile), getpwnam(user).pw_uid, getpwnam(group).pw_uid)
                    chmod(join(root, myfile), file_mode)
        except Exception as e:
            succeed[directory]['error'] = "Unable to move to target directory : {}".format(e)
            failed.update({directory: succeed[directory]})
            to_delete.append(directory)
            continue
        #try:
        #    rmtree(source_dir)
        #except Exception as e:
        #    succeed[directory]['error'] = "Unable to remove source directory : {}".format(e)
        #    failed.update({directory: succeed[directory]})
        #    to_delete.append(directory)
                
    for directory in to_delete:
        del succeed[directory]

def printSummary(failed, succeed):
    print("\n######## Summary ########\n")
    if len(succeed) > 0:
        print("{} directories have been successfully integrated.\n".format(len(succeed)))
    if len(failed) > 0:
        print("\nFailed directories :\n")
        for directory in failed.keys():
            print("   * {}".format(directory))
            print("    -> Error : {}".format(failed[directory]['error']))

if __name__ == '__main__':

    if not isdir(upload_dir):
        usage()

    if len(argv) != 1:
        usage()

    failed = {}
    succeed = {}

    checkDirectories(failed, succeed)
    if askConfirmation(failed, succeed):
        integrateDirectories(failed, succeed)
    printSummary(failed, succeed)

    print("\nJob finished")
    exit(0)

