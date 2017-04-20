#!/usr/bin/env python
from struct import unpack
from collections import namedtuple

FILENAME = '2072.PC'
READFILE_LOG = '2072.rflog'
STIK_COUNT = 78

#FILENAME = 'sonata.pc'
#STIK_COUNT = 14

Preamble = namedtuple('Preamble', [
  'fixed_header', 'version', 'b_byte', 'c_object', 'num_parts',
  'd_object', 'num_bars', 'e_object', 'font_names'
  ])
Preamble2 = namedtuple('Preamble2', [
  'c_object', 'd_short', 'e_short', 'f_short', 'g_object', 'h_object',
  'i_short', 'j_short'
  ])

STIKEntry = namedtuple('STIKEntry', [
  'a_bytes', 'num_things', 'b_bytes', 'visible', 'c_bytes', 'index', 'things'
  ])

STIKThing = namedtuple('STIKThing', [
  'a_bytes'
  ])

MUSEHeader = namedtuple('MUSEHeader', [
  'time_signature', 'b_short', 'c_short', 'd_object', 'e_object', 'f_short'
  ])

def unpack_field(count, fmt, FILE):
  return unpack_mystery(count, fmt, FILE)[0]

def unpack_mystery(count, fmt, FILE):
  return unpack(fmt, F.read(count))

with open(FILENAME, 'r') as F:
  # preamble
  preamble = Preamble(
    F.read(26),                       # fixed_header
    unpack_field(1, 'B', F),          # version??
    unpack_field(1, 'B', F),          # b
    unpack_mystery(186, '186B', F),   # c
    unpack_field(2, 'H', F),          # num parts
    unpack_mystery(4, '4B', F),       # d
    unpack_field(2, 'H', F),          # num bars!
    unpack_mystery(70, '70B', F),     # e
    [])
  font_count = unpack_field(2, 'H', F)
  for i in range(font_count):
    preamble.font_names.append(unpack_field(34, '34s', F))

  # rest of the preamble
  preamble2 = Preamble2(
    unpack_mystery(16, '16B', F), # c
    unpack_field(2, 'H', F),      # d
    unpack_field(2, 'H', F),      # e
    unpack_field(2, 'H', F),      # f
    unpack_mystery(40, '40B', F), # g
    unpack_mystery(40, '40B', F), # h
    unpack_field(2, 'H', F),      # i
    unpack_field(2, 'H', F)       # j
    )

  # check we've hit STIK
  assert F.read(4) == 'STIK'

  # read the STIK
  stik_entries = []
  for i in range(STIK_COUNT):
    entry = STIKEntry(
      unpack_mystery(8, '8B', F),   # a
      unpack_field(2, 'H', F),      # num things
      unpack_mystery(7, '7B', F),  # b
      unpack_field(1, 'B', F),      # visible
      unpack_mystery(8, '8B', F),  # c
      unpack_field(2, 'H', F),      # index
      []
      )
    for j in range(entry.num_things):
      entry.things.append(
        STIKThing(unpack_mystery(8, '8B', F))
      )
    stik_entries.append(entry)

  # check we've hit MUSE
  assert F.read(4) == 'MUSE'

  # parse notes header
  museheader = MUSEHeader(
    unpack_mystery(8, '8B', F),
    unpack_field(2, 'H', F),
    unpack_field(2, 'H', F),
    unpack_mystery(24, '24B', F),
    unpack_mystery(10, '10B', F),
    unpack_field(2, 'H', F)
    )

  print F.tell()

print preamble
print preamble2
for entry in stik_entries:
  print "%d: %d %s %s %s" % (entry.index, entry.visible, entry.a_bytes, entry.b_bytes, entry.c_bytes)

print "num bytes in STIK: %d" % (len(stik_entries)*28 + sum([e.num_things*8 for e in stik_entries]))
print museheader


# (note data)
# 05 03
# (10 bytes of tie data)
#
