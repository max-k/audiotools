#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# AudioTool.py - Gestion des fichiers audio
# max-k <max-k@post.com>
# version 4.0.2 - python 2.7
# 2011-01-14
# Require cuetools, bchunk, flac (Free Lossless Audio Codec),
# mac (Monkey's Audio), wvunpack (Wavpack), ttaenc (True Audio),
# shorten (Shorten), ffmpeg (ALAC),
# python-mutagen module to edit meta-tags,
# and lame to encode into mp3 format.

from os import path, getcwd, listdir, remove, chdir
from os.path import basename, dirname, getsize, isfile, splitext, join
from re import search, I, sub, findall
from string import strip, lstrip
from sys import argv, exit
from shutil import move
from mutagen.flac import FLAC
from mutagen.apev2 import APEv2
from mutagen.wavpack import WavPack
from mutagen.id3 import COMM
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
from time import sleep
import subprocess

extensions = ['.flac', '.wv', '.ape', '.tta', '.shn', '.wav', '.m4a']


class audioFile(object):

    def __init__(self, filename):
        print('\nLet\'s go !!\n')
        self._filename = filename
        self._basename = basename(self._filename)
        if path.dirname(self._filename) == '':
            self._dirname = getcwd()
        else:
            self._dirname = unicode(dirname(self._filename), "utf-8")
        self._filesize = getsize(self._filename) / 1048576
        self._splitname = splitext(self._basename)
        self._commentaire = 'ripp et encodage par max-k'
        self._track_list = []

    def runCmd(self, cmd):
        thread = subprocess.Popen(cmd, shell=True)
        returncode = thread.wait()
        if returncode != 0:
            print("An error as occured while executing a command.")
            print("A file must be corrupted.")
            sleep(120)
            exit(1)

    def unpackAll(self, format):
        print('Files unpacking ...\n')
        flaclist, apelist, wvlist, ttalist, shnlist, wavlist, alaclist = [], [], [], [], [], [], []
        for i in listdir(self._dirname):
            if search('"', i):
                i = i.replace('"', r'\"')
            if search('$', i):
                i = i.replace('$', r'\$')
            if search("flac$", splitext(i)[1], I):
                flaclist.append(join(self._dirname, i))
            elif search("ape$", splitext(i)[1], I):
                apelist.append(join(self._dirname, i))
            elif search("wv$", splitext(i)[1], I):
                wvlist.append(join(self._dirname, i))
            elif search("tta$", splitext(i)[1], I):
                ttalist.append(join(self._dirname, i))
            elif search("shn$", splitext(i)[1], I):
                shnlist.append(join(self._dirname, i))
            elif search("wav$", splitext(i)[1], I):
                wavlist.append(join(self._dirname, i))
            elif search("m4a$", splitext(i)[1], I):
                alaclist.append(join(self._dirname, i))
        flaclist.sort()
        apelist.sort()
        wvlist.sort()
        ttalist.sort()
        shnlist.sort()
        wavlist.sort()
        alaclist.sort()
        len_lists = len(flaclist + apelist + wvlist + ttalist + shnlist + wavlist + alaclist)
        if len_lists > len(flaclist) and len_lists > len(apelist) and len_lists > len(wvlist) and len_lists > len(ttalist) and len_lists > len(shnlist) and len_lists > len(wavlist) and len_lists > len(alaclist):
            print("unpack error : more than one file format in this directory !\n")
            self.Exit()
        elif flaclist != []:
            self.runCmd('flac -d ' + '"' + '" "'.join(flaclist) + '"')
        elif apelist != []:
            for i in apelist:
                self.runCmd('mac  "' + i + '" "' + splitext(i)[0] + '.wav" -d')
        elif wvlist != []:
            self.runCmd('wvunpack -ccyd ' + '"' + '" "'.join(wvlist) + '"')
        elif ttalist != []:
            self.runCmd('ttaenc -d "' + '" "'.join(ttalist) + '"')
        elif shnlist != []:
            counter = 1
            for i in shnlist:
                print('Unpacking file' + str(counter) + ' : ' + basename(i))
                self.runCmd('shorten -x "' + i + '" "' + splitext(i)[0] + '.wav"')
                counter = counter + 1
        elif alaclist != []:
            counter = 1
            for i in alaclist:
                print('Unpacking file' + str(counter) + ' : ' + basename(i))
                self.runCmd('ffmpeg -loglevel error -stats -i "' + i + '" "' + splitext(i)[0] + '.wav"')
                counter = counter + 1
        if format != "mp3":
            if apelist != [] or shnlist != []:
                self.runCmd('rm -f "' + i + '"')
            elif flaclist != []:
                self.runCmd('rm -f "' + '" "'.join(flaclist) + '"')
            elif ttalist != []:
                self.runCmd('rm -f "' + '" "'.join(ttalist) + '"')
            elif alaclist != []:
                self.runCmd('rm -f "' + '" "'.join(alaclist) + '"')
        print('\n')

    def encodeAll(self, format):
        print('Files encoding ...\n')
        wavlist = []
        for i in listdir(self._dirname):
            if search('"', i):
                i = i.replace('"', r'\"')
            if search('$', i):
                i = i.replace('$', r'\$')
            if search("wav$", splitext(i)[1], I):
                wavlist.append(join(self._dirname, i))
        wavlist.sort()
        if format == "mp3":
            for i in wavlist:
                self.runCmd('lame -V2 "' + i + '" "' + splitext(i)[0] + '.mp3" && rm "' + i + '"')
        else:
                self.runCmd('flac "' + '" "'.join(wavlist) + '" && rm "' + '" "'.join(wavlist) + '"')
        print('\n')

    def renameAll(self):
        print('Files renaming if possible.\n')
        filelist = []
        for i in listdir(self._dirname):
            if getsize(join(self._dirname, i)) / 1048576 < 150 and splitext(i)[1] in extensions:
                filelist.append(i)
        filelist.sort()
        for i in filelist:
                typeT = 0
                if search("tta$", splitext(i)[1], I) or search("shn$", splitext(i)[1], I) or search("wav$", splitext(i)[1], I):
                    typeT = 1
                elif search("flac$", splitext(i)[1], I):
                    try:
                        track = FLAC(join(self._dirname, i))
                    except:
                        track = {}
                elif search("m4a$", splitext(i)[1], I):
                    try:
                        track = MP4(join(self._dirname, i))
                    except:
                        track = {}
                elif search("mp3$", splitext(i)[1], I):
                    try:
                        track = MP3(join(self._dirname, i))
                    except:
                        track = {}
                elif search("wv$", splitext(i)[1], I):
                    try:
                        track = WavPack(join(self._dirname, i))
                    except:
                        track = {}
                elif search("ape$", splitext(i)[1], I):
                    try:
                        track = APEv2(join(self._dirname, i))
                    except:
                        track = {}
                if typeT != 1 and ( track.has_key('tracknumber') or track.has_key('track') or track.has_key('trkn') ):
                    if track.has_key('tracknumber'):
                        numT = track['tracknumber'][0].split("/")[0]
                    elif track.has_key('track'):
                        numT = track['track'][0]
                    else:
                        numT = str(track['trkn'][0][0])
                    if len(numT) < 2:
                        numT = '0' + numT
                        if track.has_key('tracknumber'):
                            track['tracknumber'] = numT
                        else:
                            track['track'] = numT
                        track.save()
                elif search("^\d\d", splitext(i)[0]):
                    numT = splitext(i)[0][:2]
                elif search("^\d", splitext(i)[0]):
                    numT = "0" + splitext(i)[0][:2]
                if typeT != 1 and track.has_key('title'):
                    titleT = " - ".join(track['title'])
                    if search("/", titleT):
                        titleT = sub("/", " - ", sub("\s/\s", " - ", " - ".join(track['title'])))
                        if search("^track\d\d$", splitext(basename(i))[0]):
                            track['title'] = titleT
                            track.save()
                else:
                    titleT = strip(lstrip(lstrip(lstrip(splitext(i)[0], "0123456789")), ".-_"))
                if search("`", titleT):
                    titleT = sub("`", "'", titleT)
                print('Renaming File : ' + i)
                print('  => ' + numT[:2] + "-" + titleT + splitext(i)[1])
                move(join(self._dirname, i), join(self._dirname, numT[:2] + "-" + titleT + splitext(i)[1]))
        print('\n')

    def restoreTags(self, format):
        print('Tags restoring.\n')
        counter = 0
        filelist = []
        motif = "flac$"
        if format == "mp3":
            motif = "mp3$"
        for i in listdir(self._dirname):
            if search(motif, splitext(i)[1], I):
                counter = counter + 1
                filelist.append(join(self._dirname, i))
        filelist.sort()
        for i in filelist:
            if search(motif, splitext(i)[1], I):
                if format == "mp3":
                    track = MP3(join(self._dirname, i), ID3=EasyID3)
                    track.add_tags(ID3=EasyID3)
                else:
                    track = FLAC(join(self._dirname, i))
                if search("^track\d\d", basename(i)):
                    tracknumber = splitext(basename(i))[0][-2:]
                    track['title'] = self._track_list[int(tracknumber) - 1]
                    track['tracknumber'] = tracknumber + '/' + str(counter)
                else:
                    track['tracknumber'] = splitext(basename(i))[0][:2] + '/' + str(counter)
                    track['title'] = splitext(basename(i))[0][3:]
                print('Tagging track ' + track['tracknumber'][0] + ' : ' + " ".join(track['title']))
                if hasattr(self, '_genre'):
                    track['genre'] = self._genre
                if hasattr(self, '_date'):
                    track['date'] = self._date
                if hasattr(self, '_album'):
                    if hasattr(self, '_date') and not search("^\d\d\d\d", self._album):
                        self._album = self._date + '-' + self._album
                    track['album'] = self._album
                if hasattr(self, '_artist'):
                    track['artist'] = self._artist
                if hasattr(self, '_album'):
                    track['album'] = self._album
                if format == "mp3":
                    track.save()
                    track = MP3(join(self._dirname, i))
                    track['COMM'] = COMM(encoding=3, lang='fra', desc=u'comment', text=[self._commentaire])
                else:
                    track['comment'] = self._commentaire
                track.save()
        print('\n')

    def cleanUp(self, extensions=['cue', 'log', 'txt', 'm3u', 'accurip']):
        print('Cue-sheet deleting (if exist).\n')
        for i in listdir(self._dirname):
            for ext in extensions:
                if search("{0}$".format(ext), splitext(i)[1], I):
                    remove(join(self._dirname, i))

    def moveAll(self, format):
        if format == "mp3":
            mv_ext = ".mp3"
            motif = "mp3$"
        mv_dir = join(self._dirname, basename(self._dirname) + ' -' + format.upper() + '-')
        self.runCmd('mkdir "' + mv_dir + '"')
        for i in listdir(self._dirname):
            if search(motif, splitext(i)[1], I):
                self.runCmd('mv "' + join(self._dirname, i) + '" "' + mv_dir + '/"')
        if isfile(join(self._dirname, "cover.jpg")):
            self.runCmd('cp "' + join(self._dirname, "cover.jpg") + '" "' + mv_dir + '/"')

    def Exit(self, wait=10):
        print('Job finished.')
        if len(argv) >= 3 and '--wait' in argv[2:]:
            print('Exit in {0} seconds.'.format(wait))
            sleep(wait)
        print('')
        exit(1)

class audioTrack(audioFile):

    def saveTags(self):
        print('Tags saving.\n')
        if search("flac$", splitext(self._basename)[1], I):
            try:
                track = FLAC(join(self._dirname, self._basename))
            except:
                print('No FLAC tag found\n')
        elif search("ape$", splitext(self._basename)[1], I):
            try:
                track = APEv2(join(self._dirname, self._basename))
            except:
                print ('No APE tag found\n')
        elif search("wv$", splitext(self._basename)[1], I):
            try:
                track = WavPack(join(self._dirname, self._basename))
            except:
                print ('No WV tag found\n')
        elif search("m4a$", splitext(self._basename)[1], I):
            try:
                track = MP4(join(self._dirname, self._basename))
            except:
                print ('No ALAC tag found\n')
        else:
            return
        try:
            if isinstance(track, MP4) and track.has_key('\xa9gen'):
                self._genre = " ".join(track['\xa9gen'])
            elif track.has_key('genre'):
                self._genre = " ".join(track['genre'])
            if self._genre:
                print('Genre : ' + self._genre)
            if isinstance(track, MP4) and track.has_key('\xa9day'):
                self._date = " ".join(track['\xa9day'])
            elif track.has_key('date'):
                self._date = " ".join(track['date'])
            elif track.has_key('year'):
                self._date = " ".join(track['year'])
            if self._date:
                print('Year : ' + self._date)
            if isinstance(track, MP4) and track.has_key('\xa9ART'):
                self._artist = " ".join(track['\xa9ART'])
            elif track.has_key('artist'):
                self._artist = " ".join(track['artist'])
            if self._artist:
                print('Artist : ' + self._artist)
            if isinstance(track, MP4) and track.has_key('\xa9alb'):
                self._album = " ".join(track['\xa9alb'])
            elif track.has_key('album'):
                self._album = " ".join(track['album'])
            if self._artist:
                print('Album : ' + self._artist)
            print('\n')
        except:
            track = {}


class audioAlbum(audioFile):

    def checkCueSheet(self):
        print('Checking if cue-sheet exists.\n')
        count = 0
        number = 1
        for i in listdir(self._dirname):
            if search("cue$", splitext(i)[1], I):
                count = count + 1
                move(join(self._dirname, i), join(self._dirname, 'fic' + str(count) + '.cue'))
                if count == 1:
                    print(str(count) + 'st cue-sheet file moved to fic' + str(count) + '.cue.\n')
                elif count == 2:
                    print(str(count) + 'nd cue-sheet file moved to fic' + str(count) + '.cue.\n')
                elif count == 3:
                    print(str(count) + 'rd cue-sheet file moved to fic' + str(count) + '.cue.\n')
                else:
                    print(str(count) + 'th cue-sheet file moved to fic' + str(count) + '.cue.\n')
        if count == 0:
            print('No cue-sheet file.\n')
            if not search("wv$", splitext(self._filename)[1][-2:], I):
                print("Error : cue-sheet file missing !\n")
                self.Exit()
        else:
            if count > 1:
                print('There is more than one cue-sheet file.')
                print('Checking wich of them is the best.\n')
                print('(not implemented yet. lol)\n')
            else:
                print('There is only one cue-sheet file.\n')
            move(join(self._dirname, 'fic' + str(number) + '.cue'), join(self._dirname, self._splitname[0] + '.cue'))
            print('fic' + str(number) + '.cue moved to ' + self._splitname[0] + '.cue.\n')

#    def __init__(self):
#        print argv[1]
#        self.checkCueSheet()

    def splitAlbum(self):
        print('Album spliting ...\n')
        nameWithoutExt = self._splitname[0]
        if search('"', nameWithoutExt):
            nameWithoutExt = nameWithoutExt.replace('"', r'\"')
        chdir(self._dirname)
        self.runCmd('bchunk -w "' + nameWithoutExt + '.wav" "' + nameWithoutExt + '.cue" track && rm "' + nameWithoutExt + '.wav"')
        print('\n')

    def parseCue(self):
        print('Tagging from cue-sheet...\n')
        with open(join(self._dirname, self._splitname[0] + '.cue')) as cuesheet:
            print('Parsing ' + self._splitname[0] + '.cue.\n')
            for line in cuesheet:
                line = sub("\\r$", "", sub("\\n$", "", sub("\\xef\\xbb\\xbf", "", line)))
                print(line.split())
                try:
                    line.decode("UTF-8")
                except:
                    line = line.decode("ISO-8859-15")
                if search('GENRE', line):
                    self._genre = strip(lstrip(sub("GENRE", "", sub("REM", "", line))), '"')
                    print('Genre : ' + self._genre)
                elif search('DATE', line):
                    self._date = findall("\d\d\d\d", strip(sub("DATE", "", sub("REM", "", line))))[0]
                    print('Year : ' + self._date)
                elif search('^PERFORMER', line):
                    self._artist = strip(lstrip(sub("PERFORMER", "", line)), '"')
                    print('Artist : ' + self._artist)
                elif search('^TITLE', line):
                    self._album = strip(lstrip(sub("TITLE", "", line)), '"')
                    print('Album : ' + self._album)
                elif search('TITLE', line):
                    self._track_list.append(strip(lstrip(sub("TITLE", "", line)), '"'))
            if self._track_list != []:
                print('\nTrack list :\n')
                count = 0
                for i in self._track_list:
                    count = count + 1
                    if len(str(count)) == 1:
                        str_count = '0' + str(count)
                    else:
                        str_count = str(count)
                    print('* Track' + str(count) + ' : ' + i)
                print ('\n')
            else:
                print('Nothing about track titles.\n')

if __name__ == '__main__':

    if not (len(argv) >= 2 and all(x[2:] in ['mp3', 'disc', 'track', 'wait'] for x in argv[2:])):
        print('\nUsage : `python2 AudioTool.py filename [--mp3] [--track] [--disc]`')
        print('Filename must be fully qualified or in current directory.')
        print('Supported formats : flac, wavpack (wv), monkey\'s audio (ape),')
        print('trueaudio (tta), shorten (shn) or ALAC (m4a).\n')
        print('  *  --mp3 Generate mp3 instead of flac files')
        print('  *  --track Force input file to be a track (useful if track is > 150Mb)')
        print('  *  --mp3 Force input file to be a disc (useful if disc is < 150Mb)')
        print('  *  --wait Wait a bit when job is finished\n')
    else:
        output_format = 'flac'
        if len(argv) >= 3 and '--mp3' in argv[2:]:
            output_format = 'mp3'
        if isfile(argv[1]):
            print('\n' + argv[1] + ' is a file.\n')
            if isfile(getcwd() + '/' + argv[1]):
                print(argv[1] + ' is in current directory.\n')
                arg_file = join(getcwd(), argv[1])
            else:
                print(argv[1] + ' is fully qualified.\n')
                arg_file = argv[1]
            if splitext(arg_file)[1] in extensions:
                mb_size = getsize(arg_file) / 1048576
                if len(argv) >= 3 and '--track' in argv[2:]:
                    input_type = 'track'
                    print('Track type forced.')
                elif len(argv) >= 3 and '--disc' in argv[2:]:
                    input_type = 'disc'
                    print('Disc type forced.')
                elif mb_size < 150:
                    input_type = 'track'
                    print(argv[1] + ' is smaller than 150Mb.\n')
                else:
                    input_type = 'disc'
                    print(argv[1] + ' is bigger than 150Mb.\n')
                if input_type == 'track':
                    myfile = audioTrack(arg_file)
                    myfile.saveTags()
                    myfile.renameAll()
                    myfile.unpackAll(output_format)
                    myfile.encodeAll(output_format)
                    myfile.restoreTags(output_format)
                else:
                    myfile = audioAlbum(arg_file)
                    myfile.checkCueSheet()
                    myfile.unpackAll(output_format)
                    myfile.splitAlbum()
                    myfile.encodeAll(output_format)
                    myfile.parseCue()
                    myfile.restoreTags(output_format)
                    myfile.renameAll()
                if output_format != 'mp3':
                    myfile.cleanUp()
                else:
                    myfile.moveAll(output_format)
                myfile.Exit()
            else:
                print(argv[1] + ' : ' + splitext(arg_file)[1] + ' unsupported format.')
                print('Supported formats : flac, wavpack, monkey\'s audio, trueaudio, shorten, wav.\n')
        else:
            print('\n"' + unicode(argv[1]) + '"' + ' is not a file !')
