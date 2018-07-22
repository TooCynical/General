import gpkit as gp
import random
import sys
from math import sqrt

DELAY_MIN = 0
POWER_MIN = 1
TRADEOFF  = 2

def uniform_l(n):
    return [1. / n for i in xrange(n)]


def random_l(n):
    l = [random.random() for i in range(n)]
    return [li / sum(l) for li in l]


def check_geometric_averages(s):
    for i in range(1, len(s) - 1):
        print float(s[i]), sqrt(s[i - 1] * s[i + 1])


def check_double_monotone(s):
    switches = 0

    epsilon = 0.00001
    for i in range(1, len(s) - 1):
        if s[i] > (1 + epsilon) * s[i-1] and s[i] > (1 + epsilon) * s[i+1]:
            switches += 1
        if (1 + epsilon) * s[i] < s[i-1] and (1 + epsilon) * s[i] < s[i+1]:
            switches += 1
    return (switches <= 1), switches




class Path:
    def __init__(self, n):
        self.length = 1
        
        self.smin = 1.
        self.smax = 10.
        self.lmin = 0.

        self.wire_cap = 1.
        self.wire_res = 1.

        self.gate_cap = 1.
        self.gate_res = 1.

        self.power_cost = 1.

        self.max_delay = 7.        
        self.n = n

        
    def build_path_ggp(self, prim_in=0, prim_out=0, mode=DELAY_MIN, fixed_l = []):
        s = gp.VectorVariable(self.n, "s")
        l = gp.VectorVariable(self.n - 1, "l")
    
        delay = self.__get_delay_function(s, l)
        power = self.__get_power(s)

        constraints = []
        self.__set_s_bounds(s, constraints)

        if not fixed_l:
            self.__set_l_bounds(l, constraints)
            self.__set_l_sum(l, constraints)
        else:
            self.__fix_l(fixed_l, l, constraints)

        self.__set_primary_in_out(s, prim_in, prim_out, constraints)

        if mode == DELAY_MIN:
            return gp.Model(delay, constraints), s, l
        elif mode == POWER_MIN:
            constraints.append(delay <= self.max_delay)
            return gp.Model(power, constraints), s, l
        else:
            return gp.Model(power + delay, constraints), s, l

        
    def __fix_l(self, fixed_l, l, constraints):
        for i in range(self.n - 1):
            constraints.append(l[i] == fixed_l[i])


    def __get_power(self, s):
        power = 0
        for i in xrange(self.n):
            power += self.power_cost * s[i]
        return power


    def __get_delay_function(self, s, l):
        delay = 0
        for i in xrange(self.n - 1):
            delay += self.__delay(i, s, l)
        return delay


    def __set_primary_in_out(self, s, prim_in, prim_out, constraints):
        if (prim_in > 0):
            constraints.append(s[0] == prim_in)
    
        if (prim_out > 0):
            constraints.append(s[-1] == prim_out)

    
    def __set_l_sum(self, l, constraints):
        tol = 0.001
        l_sum = 0
        for i in range(self.n - 1):
            l_sum += l[i]
                
        with gp.SignomialsEnabled():
            constraints.append((l_sum >= self.length))

        # constraints.append(l_sum <= self.length)


    def __set_s_bounds(self, s, constraints):
        s_min = gp.VectorVariable(self.n, "smin", [self.smin for dummy in xrange(self.n)])
        s_max = gp.VectorVariable(self.n, "smax", [self.smax for dummy in xrange(self.n)])
        
        for i in range(self.n):
            constraints.append(s[i] <= s_max[i])
            constraints.append(s[i] >= s_min[i])


    def __set_l_bounds(self, l, constraints):
        l_min = gp.VectorVariable(self.n - 1, "lmin", [self.lmin for dummy in xrange(self.n - 1)])
        l_max = gp.VectorVariable(self.n - 1, "lmax", [self.length for dummy in xrange(self.n - 1)])
        
        for i in range(self.n - 1):
            constraints.append(l[i] <= l_max[i])
            constraints.append(l[i] >= l_min[i])


    def __delay(self, i, s, l):
        d = 0
        d += (self.gate_cap * s[i+1] + self.wire_cap * l[i]) / (self.gate_res * s[i])
        d += self.wire_res * (self.gate_cap * s[i+1] * l[i] + 0.5 * self.wire_cap * l[i]*l[i])        
        return d
        

def make_run(n):
    p = Path(n)
    
    p.wire_res = random.random() * 2.
    p.wire_cap = random.random() * 5.
    
    p.wire_res = 1.
    p.wire_cap = 1.

    p_in = random.random() * 4 + 1
    p_out = round(random.random() * 4 + 1, 0)
    
    p_in = 000

    p.smax = 10
    p.lmin = 0.00

    f_l = uniform_l(n - 1)

    print p.wire_cap, p.wire_res, p_in, p_out

    # Compute minimum delay.
    M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out, fixed_l = f_l)

    # sol = M.localsolve(verbosity=0)
    sol = M.solve(verbosity=0)

    min_delay = float(sol["cost"])
    print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
    print "s:     ", sol(s)
    print "l:     ", sol(l)
    print "sum l: ", sum(sol(l))
    print "mono:  ", check_double_monotone(sol(s))
    # check_geometric_averages(sol(s))    
    print

    if not check_double_monotone(sol(s)):
        exit()


if __name__=="__main__":
    for i in range(int(sys.argv[1])):
        print "Run", i
        n=int(sys.argv[2])
        make_run(n)
    
    # # Compute minimum delay.
    # M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = 5., prim_out = 1.)

    # # sol = M.localsolve(verbosity=0)
    # sol = M.localsolve(verbosity=0)

    # min_delay = float(sol["cost"])
    # print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
    # print "s:", sol(s)
    # print "l:", sol(l)
    # print "sum l: ", sum(sol(l))
    # check_geometric_averages(sol(s))
    # print


# # Compute min power for max delay based on computed min_delay
# epsilon = 0.1
# p.max_delay = min_delay * (1 + epsilon)
# print "Computing min_power for max_delay", p.max_delay

# M, s, l = p.build_path_ggp(mode=POWER_MIN, prim_out = 2.)
# sol = M.localsolve(verbosity=0)

# power = float(sum(sol(s)))
# print "Power:", power
# print "s:", sol(s)
# print "l:", sol(l)

