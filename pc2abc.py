#!/usr/bin/env python

# Object contains hierarchy
# tune-related data in class Tune
# A Tune contains a Stik which contains a list of Stik_bars 
# A Tune also contains a Muse
# A Muse has a list of Muse_parts
# Each part has a list of Muse_bars
# Each Muse_bar has a list of Misc_objects and a list of Notes and a list of Rests

#import re
from struct import unpack
import sys
#from collections import namedtuple
#from operator import  attrgetter
from itertools import groupby

Folop = 0

PCFILE = sys.argv[1] 
name_parts = PCFILE.split('.',1)	#Splits filename into 2 parts
file_stem=name_parts[0]
ABCFILE = file_stem + '.abc'
LOGFILE = file_stem + '.log'

#Default midi instruments
#Determined by the clef
midi_t	= 40 #treble clef instrument
midi_a	= 40 #alto clef instrument
midi_b	= 42 #bass clef instrument

if Folop:
    attribution= """%
% Original edition transcribed and edited by Albert Folop: 
% http://imslp.org/wiki/Category:Folop_Viol_Music_Collection
% That edition released under Creative Commons Attribution-NonCommercial-ShareAlike 3.0 licence
% (http://creativecommons.org/licenses/by-nc-sa/3.0/)
% This edition converted to abc by Steve West and also released under 
% Creative Commons Attribution-NonCommercial-ShareAlike 3.0 licence
% (http://creativecommons.org/licenses/by-nc-sa/3.0/)
%
"""
else:
    attribution = ""

class Music_object():
	kind=1

class Chord(Music_object):
	kind =5
	timecode = 0
	note_list=[]
	def __init__(self, timecode):
		self.timecode = timecode
		self.note_list=[]
	def add_note(self, note):
		self.note_list.append(note)
	def render(self, ABC, clef):
		ABC.write("[")
		for note in self.note_list:
			note.render(ABC, clef)
		ABC.write("]")

class Note(Music_object):
	kind=2
	offsets = [23, 13, 17, 11]
	abc_low_notes = ['C','D','E','F','G','A','B']
	abc_high_notes = ['c','d','e','f','g','a','b']
	abc_suffixes = [",,,", ",,", ",", "", "", "'", "''", "'''"]
	accidental=''
	pitch = 0
	dot =0
	tie_start = 0
	tie_end = 0
	length = 0
	timecode = 0
	beam_start = 0
	beam_end = 0
	tuplet=0
	cont = 0

	def __init__(self, accidental='', pitch=0, dot=0, 
		tie_start=0, tie_end=0, length=0, timecode=0, cont=0, tuplet=0, beam_start=0, beam_end=0):
		self.accidental=accidental
		self.pitch = pitch
		self.dot =dot
		self.tie_start = tie_start
		self.tie_end = tie_end
		self.length = length
		self.timecode = timecode
		self.cont=cont
		self.tuplet=tuplet
		self.beam_start = beam_start
		self.beam_end = beam_end
	def render(self, ABC, clef):
		if self.tuplet and self.cont:
			ABC.write("({n} ".format(n=self.tuplet))
		abcpitch = self.decode_pitch(clef)
		abclength = decode_length(self.length, self.dot)
		tie = ''
		if self.tie_start:
			tie="-"
		space = " "
		if self.beam_start:
			space = ""
		ABC.write(self.accidental+abcpitch+abclength+tie+space)
	def decode_pitch(self, clef):
		offset = self.offsets[clef]
		internalPitch = offset - self.pitch
		octave = internalPitch//7
		note = internalPitch%7
		notelist = self.abc_high_notes
		if octave<4:
			notelist = self.abc_low_notes
		print ("Pitch: {p}; Note: {n}; octave: {o}".format(p=self.pitch, n=note,o=octave))
		notesymbol = notelist[note]+self.abc_suffixes[octave]
		return notesymbol

def decode_length(l,d):
	#Crotchet is 0a, minim 0b etc
	#convert to abc "L=1/64" initially
	abc_lengths = [1, 2, 8, 16, 32 ,64, 128, 256, 512, 1024]
	try:
		abc128_length = abc_lengths[l-5]
		lengths = [32,16,8,2,1] # eighth note is base
		if Folop:
			lengths = [64,32,16,8,2,1] # quarter note is base
		if d:
			abc128_length += abc128_length//2
		for divisor in lengths:
			if abc128_length%divisor == 0:
				numerator = abc128_length//divisor
				denominator = lengths[0]//divisor
				if denominator == 1:
					if numerator == 1:
						return ""
					else:
						return str(numerator)
				else:
					return str(numerator) + "/" + str(denominator)
	except:
		fatal("Note length {l} out of range".format(l=l))
		
class Rest(Music_object):
	kind=3
	length = 0
	timecode =0
	def __init__(self, length=0, timecode=0):
		self.length = length
		self.timecode =timecode
	def render(self, ABC, clef):
		l = decode_length(self.length, 0)
		ABC.write("z" + l + " " )
		
class Misc_object(Music_object):
	kind=1

class Clef_change(Music_object):
	kind = 0
	timecode = 0
	clef = 0
	abc = ""
	def __init__(self, timecode, clef):
		self.timecode= timecode
		self.clef = clef
		self.abc = "[K: clef={c}] ".format(c=pc2abc_clef(self.clef))
		tune.current_clef = clef
	def render(self, ABC, clef):
		ABC.write(self.abc)
		tune.current_clef = self.clef

class Fermata(Music_object):
	kind=6
	timecode=0
	def __init__(self, timecode):
		self.timecode=timecode
	def render(self, ABC, clef):
		ABC.write("!fermata!")

class Muse_bar():
	clef = 0
	key	= 0
	beats = 0
	unit = 0
	volta=''
	misc_list = []
	info_list = []
	note_list = []
	rest_list = []
	event_list = []
	decoration_list = []
	stik=0
	def __init__(self, key=0, clef=0, beats=0, unit=0,stik=0):
		self.clef = clef
		self.key	= key
		self.beats = beats
		self.unit = unit
		self.stik=stik
		self.volta=''
		self.note_list = []
		self.rest_list = []
		self.event_list= []
		self.misc_list = []
		self.info_list = []
		self.decoration_list = []
	def add_note(self, some_note):
		self.note_list.append(some_note)
	def check_tied_accidentals(self):
		#Check for the special case where the first note ina bar is tied
		#from the previous bar and has an accidental applied
		first_note = self.note_list[0]
		if first_note.tie_end and first_note.accidental:
			for n in range(1, len(self.note_list)):
				if self.note_list[n].pitch == first_note.pitch:
					if not self.note_list[n].accidental:
						self.note_list[n].accidental = first_note.accidental
					return
		return
	def add_rest(self, some_rest):
		self.rest_list.append(some_rest)
	def add_misc(self, some_misc):
		self.misc_list.append(some_misc)
	def add_info(self, some_info):
		self.info_list.append(some_info)
	def add_decoation(self, decoration):
		self.decoration_list.append(decoration)
	def sort_events(self):
		notes_and_rests= self.info_list + self.note_list + self.rest_list  
		self.event_list = sorted(notes_and_rests, key=lambda x: x.timecode, reverse=False)
	def find_chords(self):
		#Check note list for chords
		timecode_list = [n.timecode for n in self.note_list]
		if len(timecode_list) == len(set(timecode_list)):
			return
		print ("Chords found!")
		new_note_list=[]
		for key, group in groupby(self.note_list, lambda x: x.timecode):
			item_list=[x for x in group]	# Turn iterator into a list
			if len(item_list) == 1: 		# Not a chord
				new_note_list.append(item_list[0])
			else:
				new_chord = Chord(timecode=key)
				for n in item_list:
					new_chord.add_note(n)
				new_note_list.append(new_chord)
		self.note_list = new_note_list
   	def render(self, ABCFILE):
		if self.clef != tune.current_clef:
			ABCFILE.write("[K: clef={c}]".format(c=pc2abc_clef(self.clef)))
			tune.current_clef=self.clef
		if self.key != tune.key:
			ABCFILE.write("[K:{k}]".format(k=pc2abc_key(self.key)))
			tune.key=self.key
		if (self.beats != tune.beats) or (self.unit != tune.unit):
			tune.time_sig = make_time_sig(self.beats, self.unit)
			tune.beats = self.beats
			tune.unit = self.unit
			ABCFILE.write("[M:{t}] ".format(t=tune.time_sig))
		if self.volta and not self.volta.isspace():
			ABCFILE.write("[{v} ".format(v=self.volta))
		self.find_chords()
		for decoration in self.decoration_list:
			ABCFILE.write(decoration)
			ABCFILE.write(" ")
		self.sort_events()
		if len(self.event_list):
			for event in self.event_list:
				event.render(ABCFILE, tune.current_clef)
			ABCFILE.write(" {b} ".format(b=self.stik.render_line()))
		elif Folop:
			ABCFILE.write (" Z ")
			ABCFILE.write(" {b} ".format(b=self.stik.render_line()))
	def visibility(self):
		#Bar is visible if the visibility bit is set in the Stik, or we haven't had a type 3 barline yet
		if self.stik.visible:
			return 1
		stik_index=tune.stik_list.index(self.stik)
		for i in range(stik_index):
			if tune.stik_list[i].line_type==3:
				return 0
		return 1

class Muse_part():
	part_number = 0
	bar_list = []
	clef=''
	def __init__(self, number):
		self.part_number=number
		self.bar_list = []
		self.clef=''
	def add_bar(self, some_bar):
		self.bar_list.append(some_bar)

class Tune():
	title=''
	composer=0
	beats=0
	unit =0
	current_clef=''
	time_sig=''
	stik_list=[]
	part_list = []
	num_bars = 0
	num_parts = 0
	def add_part(self, some_part):
		self.part_list.append(some_part)

class part_data():
	param1 = 0
	param2 = 0
	param3 = 0
	param4 = 0
	def __init__(self):
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.param4 = 0

class stik_header():
	start = 0
	line_type=0
	num=0
	mid1=0
	mid2=0
	visible=0
	end=0
	data=[]
	def __init__(self, start, line_type, mid1, num, mid2, visibility, end):
		self.start=start
		self.num = num
		self.mid1=mid1
		self.line_type=line_type
		self.mid2=mid2
		self.visible= visibility
		self.end = end
	def render_line(self):
		if self.line_type in [0x0006, 0x0106]:
			return ":|"
		elif self.line_type in [0x0107, 0x0156, 0x0056]:
			return "::"
		elif self.line_type==0x0003:
			return "|]"
		elif self.line_type in [0x0005, 0x0050, 0x0150]:
			return "|:"
		else:
			return "|"

class stik_data():
	contents=0
	def __init__(self, c):
		self.contents=c
	
class font_data():
	contents=0
	def __init__(self,stuff):
		self.contents = stuff

def read_barstuff(FILE, LOG):
	pos = FILE.tell()
	headbytes = FILE.read(8)
	log (LOG, pos, headbytes)
	headstuff= unpack('B4sBBB', headbytes)
	key_clef=headstuff[0]
	print ('Clefkey: ', key_clef, 'Beats: ', headstuff[2], 'Unit: ', headstuff[3])
	clef=key_clef%16
	key=key_clef//16
	new_muse_bar = Muse_bar(key, clef, beats=headstuff[2], unit=headstuff[3])
	return new_muse_bar

def read_rest(FILE,LOG):
	pos = FILE.tell()
	notebytes = FILE.read(10)
	log (LOG, pos, notebytes)
	#    time  length  pos
	# 00 08  00 0a  00 fc 00 00 00 00 
	restdata = unpack('BBBBBB4B', notebytes)
	new_rest = Rest( length=restdata[3], timecode=restdata[1])
	return new_rest

def read_stik_head(FILE,LOG):
	pos = FILE.tell()
	stikbytes = FILE.read(28)
	log (LOG, pos, stikbytes)
	stikdata = unpack('2sH4sH7sb10s', stikbytes)
	#LOG.write("\nCreating new stik item with num {n} and visibility {v}\n".format(n=stikdata[1], v=stikdata[3]))
	new_stik = stik_header(start=stikdata[0], line_type=stikdata[1], mid1=stikdata[2], num=stikdata[3], mid2=stikdata[4], visibility=stikdata[5], end=stikdata[6])
	return new_stik


def read_note(FILE,LOG):
	pos = FILE.tell()
	notebytes = FILE.read(28)
	log (LOG, pos, notebytes)
#Type Stemdir Dot 2bytes Pitch 8bytes Cont  2b  time length byte Tuplet bytes Beamfrom(short)  Beamto(short)
# B     B     B     2s    b     8s      B   2s   B      B    B     B     3s     H                H
# 0     1     2     3     4      5      6   7    8      9    10    11    12     13               14
	notedata = unpack('BBB2sb8sB2sBBBB3sHH', notebytes) 
	dot_field = notedata[2]
	type=notedata[0]
	new_note = Note(
		accidental='', 
		pitch=notedata[4], 
		dot=bit(1,dot_field), 
		tie_start=bit(6,dot_field), 
		tie_end=bit(5,dot_field), 
		length=notedata[9], 
		timecode=notedata[8], 
		cont =notedata[6],
		tuplet = notedata[11],
		beam_start=notedata[14], 
		beam_end=notedata[13])
	if bit(4,type):
		new_note.accidental='='
	elif bit(3, type):
		new_note.accidental = '_'
	elif bit(2, type):
		new_note.accidental = '^'
	if new_note.tie_start:
		dot_data = get_bytes(PCFILE,LOG,12)
	if new_note.tuplet and new_note.cont:
		pos=FILE.tell()
		notebytes = FILE.read(26)
		log(LOG,pos,notebytes)
		dummy1, tuplet, dummy2 = unpack('BB24s', notebytes)
		new_note.tuplet=tuplet
	if type in [0x42, 0x43, 0x46, 0x47, 0x4a, 0x4b, 0xc3, 0xca, 0xcb]:
		dummy = get_bytes(PCFILE, LOG, 2)
	return new_note

def logprint(file, string):
	file.write("\n" + string + "\n")

def log(file, pos, chars):
	file.write ('{0:04x}'.format(pos) +": ")
	for c in chars:
		file.write(( '{0:02x}'.format(ord(c))) +" ")
	file.write("\n")

def log_short(file,pos,num):
	file.write ('{0:04x}'.format(pos) +": ")
	file.write(( '{0:04x}'.format(num)) )
	file.write("\n")
	
def get_bytes(FILE,LOG, n):
	pos=FILE.tell()
	fmt = '{n}c'.format(n=n)
	bytes = unpack(fmt, FILE.read(n))
	log(LOG, pos, bytes)
	return bytes

def get_string(FILE,LOG, n):
	pos=FILE.tell()
	bytes=FILE.read(n)
	fmt = '{n}s'.format(n=n)
	[text] = unpack(fmt, bytes)
	log(LOG, pos, bytes)
	return text

def get_char(FILE,LOG):
	pos=FILE.tell()
	[byte] = unpack('c', FILE.read(1))
	log(LOG, pos, byte)
	return byte

def get_short(FILE,LOG):
	pos=FILE.tell()
	[s] = unpack('H', FILE.read(2))
	log_short(LOG, pos, s)
	return s

def get_misc18(FILE,LOG):
	pos=FILE.tell()
	buffer=FILE.read(24)
	log(LOG,pos,buffer)
	part1,extras,part1a = unpack('20sH2s',buffer)
	if extras:
		extras+=1
	pos=FILE.tell()
	part2 = FILE.read(10+extras)
	log(LOG,pos,part2)
	return part2	
    
  # misc12 string fields
  # 00 00 50 0b fc ff fd fb 01 00 56 01 12 00 de 13 8d 03 00 00 04 00 6b 00 title (beef in the cupboard)
  # 00 00 b0 0c 05 00 cf fb 09 00 09 02 07 00 89 0c 8d 03 00 00 03 00 01 00 title (Festival Reel)
  # 00 00 80 08 fd ff 15 fa 01 00 56 01 0c 00 a5 10 c0 02 00 00 03 00 03 00 title (french chanson)
  # 00 00 40 08 03 00 eb fb 01 00 00 00 07 00 42 18 ab 01 00 00 08 00 30 00 title (8. Belle sans sy...)
  
  # 00 00 50 0b 03 00 75 fd 01 00 00 00 04 00 96 06 8d 01 00 00 03 00 02 00 compooser (Emile)
  
  # 00 00 40 0a fe ff 1f fa 01 00 00 00 07 00 b1 04 ab 01 00 00 03 00 04 00 composer? (Lombart)
  # 00 00 40 01 01 00 55 fb 01 00 56 01 0a 00 0a 0c 95 01 00 00 04 00 10 00 composer (Pierre Attaignant (1529))

  # 00 00 30 0a fb ff a0 03 01 00 56 01 07 00 4b 03 a6 01 00 00 02 00 1d 00 (Lyric)
  
  # 00 00 60 08 02 00 00 03 01 00 00 00 07 00 8a 03 ab 01 00 00 02 00 1d 00 page number (2270-1)
  # 00 00 60 01 01 00 b4 fd 15 00 19 01 01 00 98 01 2b 01 00 00 02 00 1f 00 Fine
  

def get_misc12(FILE,LOG):
	pos=FILE.tell()
	buffer=FILE.read(24)
	log(LOG,pos,buffer)
	part1, vertical_position, stringflag, part2= unpack('7sbH14s', buffer)
	if stringflag:
		stringlength=get_short(PCFILE,LOG)
		miscdata = get_string(PCFILE, LOG, stringlength)
		if vertical_position < 0:
			return miscdata
		# vertical_position > 0 (ie below the staff) may also be interesting?
	return ''

def get_clefchange(FILE,LOG):
	pos=FILE.tell()
	buffer=FILE.read(24)
	log(LOG,pos,buffer)
	#part1, c1, c2, part2, timecode, part3 = unpack('12sBB3sB6s', buffer)
	part1, timecode, part2, c1, c2, part3 = unpack('3sB8sBB10s', buffer)
	info_obj = Clef_change(timecode, c2)
	return info_obj
    
    # 00 00 00 00 03 00 c5 fd 0c 00 40 01 01 00 88 00 80 01 00 00 00 00 31 00 00 00 00 00 5b ff ab fc 00 00 d0 0e 01 1st ending
    # 00 00 ff 0f d6 00 ab fd 0c 00 40 01 01 00 88 00 80 01 00 00 00 00 32 00 00 00 ff 0f 2a 00 ab fc 01 00 ff 0f 15 2nd ending Early
    # 00 00 ff 11 01 01 15 fd 0c 00 40 01 01 00 71 00 80 01 00 00 00 00 20 00 00 00 ff 11 41 00 ab fc 01 00 10 05 00 Fine ending Early

def get_volta(FILE,LOG):
	pos=FILE.tell()
	buffer=FILE.read(54)
	log(LOG,pos,buffer)
	part1, volta, part2, bar_offset, part3= unpack('22ss9sb21s',buffer)
	return volta, bar_offset

def get_decoration(FILE,LOG):
	pos=FILE.tell()
	buffer=FILE.read(36)
	log(LOG,pos,buffer)
	timecode, residue, extra = unpack('H32sH', buffer)
	if extra:
		pos=FILE.tell()
		buffer=FILE.read(10*extra)
		log(LOG,pos,buffer)
	return Fermata(timecode)

def bit(n, thing):
	if n==1:
		return thing & 1
	return thing & (1<<n-1)

def fatal(string):
	print ("FATAL ERROR:")
	print("   "+ string)
	exit()

def pc2abc_key(pc_key):
	abckeys=['Gb','Db','Ab','Eb','Bb','F','C','G','D','A','E','B']
	try:
		return (abckeys[pc_key-1])
	except:
		fatal ("Out of range PC key: {k}".format(k=pc_key))

def pc2abc_clef(pc_clef):
	abcclefs=["treble","C4","alto","bass"]
	try:
		return (abcclefs[pc_clef])
	except:
		fatal ("Out of range PC clef: {k}".format(k=pc_clef))

def make_time_sig(beats, units):
		denominator = ['?','?','?','512','256','128','64','32','16','8','4','2','1','?','?'][units]
		time_sig="{n}/{d}".format(n=beats, d=denominator)
		return time_sig

def render_tune(tune):
	print ("Rendering tune with {p} parts and {b} bars".format(p=tune.num_parts, b=tune.num_bars))
	try:
		firstpart=tune.part_list[0]
	except:
		fatal ("Can't find any parts to process!")
	try:
		firstbar=firstpart.bar_list[0]
		tune.key=firstbar.key
		tune.beats=firstbar.beats
		tune.unit=firstbar.unit
		tune.time_sig=make_time_sig(tune.beats, tune.unit)
	except:
		fatal ("Can't find any bars to extract key!")
	with open(ABCFILE, 'w') as ABC:
		ABC.write("%abc-2.1\n")
		ABC.write(attribution)
		ABC.write(get_strings(tune))
		ABC.write("%%measurenb 0\n%%squarebreve\n")
		ABC.write("\nX:1\n")
		if tune.title:
			ABC.write(tune.title)
		else:
			ABC.write("T:Unknown\n")
		if tune.composer:
			ABC.write(tune.composer)
		if Folop:
			ABC.write("L:1/4\n")
		else:
			ABC.write("L:1/8\n")
		#p = str([x+1 for x in list(range(tune.num_parts))]).strip('[],')
		p=""
		for x in range(tune.num_parts):
			p+= str(x+1) + " "
		ABC.write("%%score [ {p}]\n".format(p=p))
		ABC.write("%%linebreak\n")
		ABC.write("M:"+tune.time_sig+"\n")
		ABC.write("K:{k}\n".format(k=pc2abc_key(tune.key)))
		for p in range(len(tune.part_list)):
			part = tune.part_list[p]
			try:
				firstbar=part.bar_list[0]
				ABC.write("%\nV:{v} clef={c}\n".format(v=p+1, c= pc2abc_clef(firstbar.clef)))
				mid =[ str(midi_t), str(midi_a), str(midi_a), str(midi_b)]
				try:
					midi_inst = mid[firstbar.clef]
				except:
					midi_inst = "41"
				ABC.write("%%MIDI program {n}\n".format(n=midi_inst))
				part.clef=pc2abc_clef(firstbar.clef)
				tune.current_clef=firstbar.clef
				tune.beats=firstbar.beats
				tune.unit = firstbar.unit
				tune.time_sig=make_time_sig(firstbar.beats, firstbar.unit)
			except:
				fatal ("Can't find any bars in part {p}!".format(p=p+1))
			barcount = 1
			newlineflag=0
			for bar in part.bar_list:
				print ("{b}: {v}".format(b=barcount, v=tune.stik_list[barcount].visible))
				if  bar.visibility():
					newlineflag=0
					bar.render(ABC)
					if not barcount%5:
						if barcount<len(part.bar_list):
							ABC.write("%Bar {n}\n".format(n=barcount))	
							newlineflag=1
				barcount+=1
			if not newlineflag:
				ABC.write("\n")
		if Folop:
			ABC.write("%\n%\n%#Folop:{n}\n".format(n=file_stem))

def get_strings(tune):
	misc_strings=""
	titlestring=""
	composerstring=""
	finds=0
	for p in tune.part_list:
		for bar in p.bar_list:
			if len(bar.misc_list):
				finds+=1
			for m in reversed(bar.misc_list):
				misc_strings += "% " + m + "\n"
				if finds==1:
					titlestring+="T:{s}\n".format(s=m)
				if finds==2 and len(m) > 0:
					composerstring+="C:{c}\n".format(c=m)
	tune.title=titlestring
	tune.composer=composerstring
	return misc_strings

tune = Tune()	#Make a new tune
with open(LOGFILE, 'w') as LOG, open(PCFILE, 'r') as PCFILE:
	
	start_sequence =  get_bytes(PCFILE, LOG, 26)
	print (''.join(start_sequence))
	if Folop:
		[unknown1] = get_char(PCFILE,LOG)
	[version] = get_char(PCFILE, LOG)
	version_number = '{0:02x}'.format(ord(version))
	print ("Version: {v}".format(v=version_number))
	unknown2 = get_bytes(PCFILE, LOG, 186)  
	tune.num_parts = get_short( PCFILE, LOG)        
	unknown3 = get_bytes(PCFILE, LOG, 4) 
	tune.num_bars = get_short(PCFILE, LOG)  
   	unknown4= get_bytes( PCFILE, LOG, 70)
	num_fonts = get_short( PCFILE, LOG) 
	print ("Number of parts: {p}".format(p=tune.num_parts))
	print ("Number of bars: {b}".format(b=tune.num_bars))
	print ("Number of fonts: {f}".format(f=num_fonts))
	print (tune.__dict__)
	
	fontlist =[]
	for i in range(num_fonts):
		f = font_data(get_bytes(PCFILE, LOG, 34))
		fontlist.append(f)
	unknown5 = get_bytes(PCFILE, LOG, 16)
	partlist=[]
	for i in range(tune.num_parts):
		new_part = part_data()
		new_part.param1 = get_short(PCFILE, LOG)
		partlist.append(new_part)
	for part in partlist:
		part.param2 = get_char(PCFILE, LOG)
	for part in partlist:
		part.param3 = get_bytes(PCFILE, LOG, 40)
	for part in partlist:
		part.param4 = get_short(PCFILE, LOG)
		print (part.__dict__)
	stikassertion = get_bytes(PCFILE, LOG,4)
	print (stikassertion)
	#Read the STIK
	#stiklist=[]
	for b in range(tune.num_bars+1):
		print ("Processing stik bar {n}".format(n=b+1))
		logprint (LOG, "Processing Stik for bar {n}".format(n=b+1))
		new_stik = read_stik_head(PCFILE,LOG)
		if new_stik.num:
			stikdata_list=[]
			for i in range(new_stik.num):
				d = stik_data(get_bytes(PCFILE, LOG, 8))
			stikdata_list.append(d)
			new_stik.data = stikdata_list
		tune.stik_list.append(new_stik)
	#for i in range(tune.num_bars+1):
	#	print ("Stik {n}: Visibility {v}; num {num}".format(n=1+i, v=tune.stik_list[i].visible, num=tune.stik_list[i].num))
	#exit()
	#Read the muse
	museassertion = get_bytes(PCFILE, LOG,4)
	print (museassertion)
	for p in range(tune.num_parts):
		this_part = Muse_part(p)
		print ("Processing part {n}".format(n=p+1))
		logprint (LOG, "Processing part {n}".format(n=p+1))
		stored_volta = '';
		for b in range(tune.num_bars):
			print ("Processing notes for bar {n}".format(n=b+1))
			logprint (LOG, "Processing notes for bar {n}".format(n=b+1))
			#barheader = read_barhead(PCFILE,LOG)
			new_muse_bar = read_barstuff(PCFILE,LOG)
			if len(stored_volta) > 0:
				new_muse_bar.volta=stored_volta
				stored_volta = ''
			new_muse_bar.stik =tune.stik_list[b+1]
			misclist=[]
			#notelist=[]
			misclength= get_short(PCFILE,LOG)
			if misclength:
				print (" {n} miscellaneous items".format(n=misclength))
				for i in range(misclength):
					miscdata =0
					misc_type=get_short(PCFILE,LOG)
					if misc_type in [0x18, 0x19]:
						miscdata=get_misc18(PCFILE,LOG)
					elif misc_type==0x12:
						miscdata = get_misc12(PCFILE,LOG)
						if miscdata == "Fine":
							new_muse_bar.add_decoation("+fine+")
						else:
							new_muse_bar.add_misc(miscdata)
					elif misc_type==0x15:
						dummy = get_bytes(PCFILE, LOG, 34)
						#MF sign to be processed
					elif misc_type==0x000e:
						miscdata = get_clefchange(PCFILE, LOG)
						new_muse_bar.add_info(miscdata)
					elif misc_type==0x30:
						volta, offset = get_volta(PCFILE,LOG)
						if offset == 0:
							new_muse_bar.volta = volta
						elif offset == 1:
							stored_volta = volta
			notes_length = get_short(PCFILE,LOG)
			if notes_length:
				print (" {n} notes".format(n=notes_length))
				for i in range(notes_length):
					#note_data = get_bytes(PCFILE, LOG, 28)
					new_note = read_note(PCFILE, LOG)
					print "Note starts {a} {b}".format( 
						a=new_note.pitch, b=new_note.length)
					#print (note_data)
					#notelist.append(note_data)
				#new_muse_bar.append_note(new_note)
					new_muse_bar.add_note(new_note)
					new_muse_bar.check_tied_accidentals()
			rests_length = get_short(PCFILE,LOG)
			if rests_length == 0x0318:
				dec = get_decoration(PCFILE, LOG)
				new_muse_bar.info_list.append(dec)
			elif rests_length:
				print (" {n} rests".format(n=rests_length))
				for i in range(rests_length):
					new_rest=read_rest(PCFILE,LOG)
					new_muse_bar.add_rest(new_rest)
			residue = get_bytes(PCFILE,LOG,12)
			this_part.add_bar(new_muse_bar)
		tune.add_part(this_part)
render_tune(tune)
					
			

			

