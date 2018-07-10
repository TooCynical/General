import math
import random

def delay(s1, s2, s3, l):
	d1 = (s2 + l) / float(s1)
	d2 = l * (l + s2)
	d3 = (s3 + 1 - l) / float(s2)
	d4 = (1-l) * (1 - l + s3)
	return d1 + d2 + d3 + d4

def cmp(s11, s21, s31, l1, s12, s22, s32, l2):
	v1 = delay(s11, s21, s31, l1)
	v2 = delay(s12, s22, s32, l2)
	avg = 0.5 * (v1 + v2)

	GR1 = GR(s11, s12)
	GR2 = GR(s21, s22)
	GR3 = GR(s31, s32)
	AM1  = AM(l1, l2)

	v3 = delay(GR1, GR2, GR3, AM1)

	convex = (avg > v3)
	if not convex:
		print s11, s21, s31, l1
		print "Delay (1): \t", v1 
		print s12, s22, s32, l2
		print "Delay (2): \t", v2 
		print "Delay (avg): \t", avg
		print GR1, GR2, GR3, AM1
		print "Delay (cc): \t", v3 


	return convex

def chain_delay_derivative():
    n = len(s)
    l_derivatives = []
    
    for i in xrange(n):
      l_derivatives.append()  
        

def chain_delay(s, l):
	n = len(s)
	delay = 0
	for i in range(n - 1):
		delay += (s[i+1] + l[i]) / float(s[i])
		delay += l[i] * (l[i] + s[i+1])
	return delay

def AM(x1, x2):
	return (x1 + x2) / 2.0

def GR(x1, x2):
	return math.sqrt(x1 * x2)
 
def is_local_min(s, l):
    val = chain_delay(s,l)


if __name__ == "__main__":
	t = 100000
	mini = 10.
	
	n = 3
	u, v = 1, 5
	epsilon = 0.01
      
	print chain_delay([3, 3, 3], [0.5, 0.5])

	for i in xrange(t):
		s = [random.uniform(u, v) for dummy in range(n)]
		s[-1] = s[0]

		l = [random.uniform(0, 1) for dummy in range(n-1)]
		factor = sum(l)
		l = [x / factor for x in l]

		if chain_delay(s, l) < mini:
			mini = chain_delay(s, l)
			ms, ml = s, l

	print mini
	print s
	print l
