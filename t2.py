#!/usr/bin/env python
import re
import struct
import sys

LOGFILE = sys.argv[1] + '.rflog'
PCFILE = sys.argv[1] + '.PC'

with open(LOGFILE, 'r') as LOG:
  with open(PCFILE, 'r') as PC:
    offset = 0
    for line in LOG:
      m = re.match(r'^trace:file:ReadFile 0x.. 0x...... ([0-9]+) .*$', line)
      if not m: next
      count = int(m.group(1))
      print '%5x (%3x): %s' % (offset, count, ' '.join(['%02x'%x for x in struct.unpack('%dB'%count, PC.read(count))]))
      offset += count
