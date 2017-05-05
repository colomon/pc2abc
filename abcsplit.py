#!/usr/bin/python
import argparse
import os
import re

rubric = "#include <ficta.abp>\n#include <rests.abp>\n"

parser = argparse.ArgumentParser(description='Strip parts from an abc file')
parser.add_argument("filename", help="filename of the abc file to be converted")
parser.add_argument("-n", "--name", help="specify the root name to use for created files")

parser.parse_args()
args = parser.parse_args()
filename = args.filename
name_parts = filename.split('.',1)	#Splits filename into 2 parts
name=name_parts[0]
if args.name:
	name= args.name

class Voice():
	filename=''
	clef = ''
	def __init__(self, voice_name, clef):
		self.voice_name = voice_name
		self.clef = clef
		self.filename = 'v' + voice_name + '.abn'
		with open(self.filename, 'w') as VOICE:
			VOICE.close()	#SO we don't keep on appending to it
	def add_line(self, line):
		with open(self.filename, 'a') as VOICE:
			print ("Writing: {l}".format(l=line))
			VOICE.write(line)


voices = {}
current_voice_name =0
current_voice = 0
keyline = ''
scoreline=''
xline=''
header=''
preheader=''
with open (filename,"r") as SOURCE:
	for line in SOURCE:
		print (line)
		if not xline:
			if re.match(r'^X:.*', line):
				xline = line
			else:
				preheader+=line
			continue
		if not keyline:
			if re.match(r'^K:(\w)',line):
				keyline=line
			elif  re.match(r'^%%score.*', line):
				scoreline=line

			else:
				header += line
			continue
		m = re.match(r'^V\:(\d)\s+clef=(\w+)', line)
		if m:
			current_voice_name=m.group(1)
			clef=m.group(2)
			if current_voice_name not in voices.keys():
				new_voice = Voice(current_voice_name, clef)
				voices[current_voice_name] = new_voice
			current_voice = voices[current_voice_name]
		else:
			if current_voice:
				current_voice.add_line(line)
with open (name+'.abp', 'w') as ABP:
	ABP.write("%#Instrument: viol\n")
	ABP.write("%#Voices:{n}\n".format(n=len(voices)))
	inst_string=''
	for v in voices.keys():
		clef=voices[v].clef
		inst={'treble' : 'Tr', 'alto' : 'T', 'bass' : 'B'}[clef]
		inst_string += inst
	ABP.write("%#Voicing:{v}\n".format(v=inst_string))
	ABP.write(rubric)
	ABP.write(preheader)
	ABP.write(xline)
	ABP.write(header)
	ABP.write(scoreline)
	ABP.write(keyline)
	for v in voices.keys():
		ABP.write('V:{n} clef={c}\n'.format(n=v, c=voices[v].clef))
		ABP.write("#include v{n}.abn\n".format(n=v))
with open (name+'_parts.abp', 'w') as ABP:
	ABP.write(rubric)
	ABP.write(preheader)
	ABP.write('\n')
	for v in sorted(voices.keys()):
		ABP.write('X:{v}\n'.format(v=v))
		ABP.write(header)
		ABP.write(keyline.rstrip())
		ABP.write(" clef={c}\n".format(c=voices[v].clef))
		ABP.write("#include v{n}.abn\n\n".format(n=v))
		
with open ('Makefile', 'w') as MAKE:
	MAKE.write("include abc.mk\nabcoptions= -O= -c\nall : ")
	MAKE.write ("{name}.ps {name}.mid {name}_parts.ps\n".format(name=name))
		
			
				
			
			
		

