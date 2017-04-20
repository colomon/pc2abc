#!/usr/bin/env python

# Object contains hierarchy
# tune-related data in class Tune
# A Tune contains a Stik which contains a list of Stik_bars 
# A Tune also contains a Muse
# A Muse has a list of Muse_parts
# Each part has a list of Muse_bars
# Each Muse_bar has a list of Misc_objects and a list of Notes and a list of Rests

import re
from struct import unpack
import sys
from collections import namedtuple

LOGFILE = sys.argv[1] + '.log'
PCFILE = sys.argv[1] + '.PC'


class Music_object():
	kind=0

class Note(Music_object):
	kind=2
	accidental=0
	pitch = 0
	dot =0
	tie_start = 0
	tie_end = 0
	length = 0
	timecode = 0
	beam_start = 0
	beam_end = 0
	def __init__(self, accidental=0, pitch=0, dot=0, 
		tie_start=0, tie_end=0, length=0, timecode=0, beam_start=0, beam_end=0):
		self.accidental=accidental
		self.pitch = pitch
		self.dot =dot
		self.tie_start = tie_start
		self.tie_end = tie_end
		self.length = length
		self.timecode = timecode
		self.beam_start = beam_start
		self.beam_end = beam_end


class Rest(Music_object):
	kind=3
	length = 0
	timecode =0
	def __init__(self, length=0, timecode=0):
		self.length = length
		self.timecode =timecode

class Misc_object(Music_object):
	kind=1

class Muse_bar():
	clef = 0
	key	= 0
	beats = 0
	unit = 0
	misc_list = []
	note_list = []
	rest_list = []
	event_list = []
	def __init__(self, key=0, clef=0, beats=0, unit=0):
		self.clef = clef
		self.key	= key
		self.beats = beats
		self.unit = unit
		self.note_list = []
		self.rest_list = []
		self.event_list= []
		self.misc_list = []
	def add_note(self, some_note):
		self.note_list.append(some_note)
	def add_rest(self, some_rest):
		self.rest_list.append(some_rest)
	def sort_events(self):
		notes_and_rests= self.note_list + self.rest_list
		self.event_list = sorted(notes_and_rests, key=lambda x: x.timecode, reverse=True)

class Muse_part():
	part_number = 0
	bar_list = []
	def __init__(self, number):
		self.part_number=number
		self.bar_list = 0
	def add_bar(self, some_bar):
		self.bar_list.append(some_bar)

class Tune():
	title=0
	composer=0
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
	num=0
	middle=0
	visible=0
	end=0
	data=[]
	def __init__(self, start, num, middle, visibility, end):
		self.start=start
		self.num = num
		self.middle=middle
		self.visible= visibility
		self.end = end



class stik_data():
	contents=0
	def __init__(self, c):
		self.contents=c
	

class font_data():
	contents=0
	def __init__(self,stuff):
		self.contents = stuff

barhead=namedtuple('barhead',['clef', 'key', 'beats', 'unit'])



def read_barhead(FILE,LOG):
	pos = FILE.tell()
	headbytes = FILE.read(8)
	log (LOG, pos, headbytes)
	headstuff= unpack('B4sBBB', headbytes)
	#log(LOG, FILE.tell(),headstuff)
	key_clef=headstuff[0]
	print ('Clefkey: ', key_clef, 'Beats: ', headstuff[2], 'Unit: ', headstuff[3])
	clef=key_clef%64
	key=key_clef//64
	bardata=barhead(clef,key,headstuff[2],headstuff[3])
	return bardata

def read_barstuff(FILE, LOG):
	pos = FILE.tell()
	headbytes = FILE.read(8)
	log (LOG, pos, headbytes)
	headstuff= unpack('B4sBBB', headbytes)
	key_clef=headstuff[0]
	print ('Clefkey: ', key_clef, 'Beats: ', headstuff[2], 'Unit: ', headstuff[3])
	clef=key_clef%64
	key=key_clef//64
	new_muse_bar = Muse_bar(key, clef, beats=headstuff[2], unit=headstuff[3])
	return new_muse_bar

def read_note(FILE,LOG):
	pos = FILE.tell()
	notebytes = FILE.read(28)
	log (LOG, pos, notebytes)
	#Type Stemdir Dot 2bytes Pitch 11bytes time length 5bytes Beamfrom(short)  Beamto(short)
	# B     B     B     2s    B     11s     B      B     5s     H                H
	notedata = unpack('BBB2sB11sBB5sHH', notebytes)
	dot_field = notedata[2]
	type=notedata[0]
	new_note = Note(
		accidental=0, 
		pitch=notedata[4], 
		dot=bit(1,dot_field), 
		tie_start=bit(6,dot_field), 
		tie_end=bit(5,dot_field), 
		length=notedata[7], 
		timecode=notedata[6], 
		beam_start=notedata[9], 
		beam_end=notedata[10])
	if bit(4,type):
		new_note.accidental='='
	elif bit(3, type):
		new_note.accidental = '_'
	elif bit(2, type):
		new_note.accidental = '^'
	if new_note.tie_start:
		dot_data = get_bytes(PCFILE,LOG,12)
	if type in [0x42, 0x43, 0x47, 0x4a, 0x4b, 0xca]:
		dummy = get_bytes(PCFILE, LOG, 2)
	return new_note

	

class bar(): 
	barheader = 0
	misclist = []
	notelist = []
	def __init__(self,header,misclist,notelist):
		self.header=header
		self.misclist = misclist
		self.notelist = notelist


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

def get_char(FILE,LOG):
	pos=FILE.tell()
	byte = unpack('c', FILE.read(1))
	log(LOG, pos, byte)
	return byte

def get_short(FILE,LOG):
	pos=FILE.tell()
	[s] = unpack('H', FILE.read(2))
	log_short(LOG, pos, s)
	return s

def bit(n, thing):
	if n==1:
		return thing & 1
	return thing & (1<<n-1)

offset = 0

with open(LOGFILE, 'w') as LOG, open(PCFILE, 'r') as PCFILE:
	tune = Tune()	#Make a new tune
	start_sequence =  get_bytes(PCFILE, LOG, 26)
	print (''.join(start_sequence))
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
	stiklist=[]
	for b in range(tune.num_bars+1):
		print ("Processing stik bar {n}".format(n=b))
		new_stik = stik_header(get_bytes(PCFILE, LOG, 8), 
						get_short(PCFILE, LOG),
						get_bytes(PCFILE,LOG,7),
						get_char(PCFILE,LOG),
						get_bytes(PCFILE, LOG, 10))
		if new_stik.num:
			stikdata_list=[]
			for i in range(new_stik.num):
				d = stik_data(get_bytes(PCFILE, LOG, 8))
			stikdata_list.append(d)
			new_stik.data = stikdata_list
		stiklist.append(new_stik)
	#Read the muse
	museassertion = get_bytes(PCFILE, LOG,4)
	print (museassertion)
	for p in range(tune.num_parts):
		this_part = Muse_part(p)
		print ("Processing part {n}".format(n=p+1))
		logprint (LOG, "Processing part {n}".format(n=p+1))
		for b in range(tune.num_bars):
			print ("Processing notes for bar {n}".format(n=b+1))
			logprint (LOG, "Processing notes for bar {n}".format(n=b+1))
			#barheader = read_barhead(PCFILE,LOG)
			new_muse_bar = read_barstuff(PCFILE,LOG)
			misclist=[]
			notelist=[]
			misclength= get_short(PCFILE,LOG)
			if misclength:
				print (" {n} miscellaneous items".format(n=misclength))
				for i in range(misclength):
					miscdata =0
					misc_type=get_short(PCFILE,LOG)
					if misc_type==0x18:
						miscdata=get_bytes(PCFILE,LOG,34)
					elif misc_type==0x12:
						dummy = get_bytes(PCFILE, LOG, 24)
						stringlength=get_short(PCFILE,LOG)
						miscdata = get_bytes(PCFILE, LOG, stringlength)
					
					misclist.append(misc_type)
					misclist.append(miscdata)
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
			rests_length = get_short(PCFILE,LOG)
			if rests_length:
				print (" {n} rests".format(n=rests_length))
				for i in range(rests_length):
					slot3_data=get_bytes(PCFILE,LOG,10)
			residue = get_bytes(PCFILE,LOG,12)
			
					
			

			

