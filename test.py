bits = 0xc0

def bit(n, thing):
	if n==1:
		return thing & 1
	return thing & (1<<n-1)

for i in range (8):
	print ("Bit {i} is {x}".format(i=i+1, x= bit(i+1,bits)))
