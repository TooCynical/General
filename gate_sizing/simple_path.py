import gpkit as gp
import random
import sys
from math import sqrt

from timeit import default_timer as timer

import cvxopt as cvx
cvx.solvers.options['show_progress'] = False

import matplotlib.pyplot as plt

DELAY_MIN = 0
POWER_MIN = 1
TRADEOFF  = 2

def uniform_l(n, length=1.):
    return [length / n for i in xrange(n)]


def random_l(n, length=1.):
    l = [random.random() for i in range(n)]
    return [length * li / sum(l) for li in l]


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
        self.length = 1.
        
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


    def build_path_qp(self, s, mode=DELAY_MIN):
        q = [self.wire_cap / (self.gate_res * s[i]) + self.wire_res * self.gate_cap * s[i+1] \
             for i in xrange(self.n - 1)]
        q = cvx.matrix(q)

        p = [0.5 * self.wire_res * self.wire_cap for i in xrange(self.n - 1)]
        P = cvx.spdiag(p)

        G = -cvx.spdiag([1. for i in xrange(self.n - 1)])
        h = cvx.matrix([0. for i in xrange(self.n - 1)])

        A = cvx.matrix([1. for i in xrange(self.n - 1)]).T
        b = cvx.matrix([self.length])

        return P, q, G, h, A, b

        
    def build_path_ggp(self, prim_in=0, prim_out=0, mode=DELAY_MIN, fixed_l=[], fixed_s=[]):
        s = gp.VectorVariable(self.n, "s")
        l = gp.VectorVariable(self.n - 1, "l")
    
        constraints = []

        if not fixed_s:
            self.__set_s_bounds(s, constraints)
        else:
            self.__fix_s(fixed_s, s, constraints)

        if not fixed_l:
            self.__set_l_bounds(l, constraints)
            self.__set_l_sum(l, constraints)
        else:
            self.__fix_l(fixed_l, l, constraints)

        self.__set_primary_in_out(s, prim_in, prim_out, constraints)

        delay = self.__get_delay_function(s, l)
        power = self.__get_power(s)

        if mode == DELAY_MIN:
            return gp.Model(delay, constraints), s, l
        elif mode == POWER_MIN:
            constraints.append(delay <= self.max_delay)
            return gp.Model(power, constraints), s, l
        else:
            return gp.Model(power + delay, constraints), s, l


    # public version of __get_delay_function (that takes fixed s, l).
    def get_delay(self, fixed_s, fixed_l):
        return self.__get_delay_function(fixed_s, fixed_l)


    def __fix_s(self, fixed_s, s, constraints):
        for i in range(self.n):
            constraints.append(s[i] == fixed_s[i])

        
    def __fix_l(self, fixed_l, l, constraints):
        for i in range(self.n - 1):
            constraints.append(l[i] == fixed_l[i])


    def __get_power(self, s):
        power = 0
        for i in xrange(self.n):
            power += self.power_cost * s[i]
        return power


    # Can take either fixed or variable s, l.
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

    # p.length = float(n) / 10

    p.smax = 50
    
    p.wire_res = random.random() * 2.
    p.wire_cap = random.random() * 5.
    
    p.wire_res = 1.
    p.wire_cap = 1.
    # p.wire_res = 0.
    # p.wire_cap = 0.

    p_in = random.random() * 4 + 1
    p_out = round(random.random() * 30 + 1, 0)
    
    # p_in = 000

    p.lmin = 0.00

    # f_l = uniform_l(n - 1, p.length)
    # f_l = random_l(n - 1)
    f_l = []

    print p.wire_cap, p.wire_res, p_in, p_out

    # Compute minimum delay.
    M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out, fixed_l = f_l)

    sol = M.localsolve(verbosity=0)
    # sol = M.solve(verbosity=0)

    min_delay = float(sol["cost"])
    print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
    print "s:     ", sol(s)
    print "l:     ", sol(l)
    print "sum l: ", sum(sol(l))
    print "mono:  ", check_double_monotone(sol(l))
    # check_geometric_averages(sol(s))    
    print

    if not check_double_monotone(sol(s)):
        exit()


def alternate(n, m):
    p = Path(n)

    p.length = float(n)

    fixed_l = random_l(n - 1, p.length)

    print fixed_l

    p_in = 0
    p_out = 1
    # p_out = round(random.random() * 30 + 1, 0)

    # p.wire_res = random.random() * 5.
    # p.wire_cap = random.random() * 10.

    M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out)
    sol = M.localsolve(verbosity=0)
    min_delay = float(sol["cost"])
    print "GGP solution"
    # print
    # print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
    print "s:     ", sol(s)
    print "l:     ", sol(l)
    # print "sum l: ", sum(sol(l))
    # print

    ggp_sol = min_delay
    ggp_s = [float(si) for si in sol(s)]
    ggp_l = [float(li) for li in sol(l)]
    
    sol_values = []

    epsilon = 0.000000000001

    for i in xrange(m):
        # print "Iteration", i

        print min_delay, "opt l", fixed_l
        M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out, fixed_l = fixed_l)
        sol = M.solve(verbosity=0)
        min_delay = float(sol["cost"])
        # print "Optimised s"
        # print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
        # print "s:     ", sol(s)
        # print "l:     ", sol(l)
        # print "sum l: ", sum(sol(l))

        sol_values.append(min_delay)
        fixed_s = [float(si) for si in sol(s)]

        print fixed_s

        P, q, G, h, A, b = p.build_path_qp(fixed_s)
        sol = cvx.solvers.qp(2 * P, q, G, h, A, b)
        l_gp = [max(epsilon, x) for x in sol['x']]
                
        # # print min_delay, "opt s", fixed_s
        M, s, l = p.build_path_ggp(mode=DELAY_MIN, fixed_s = fixed_s)
        sol = M.localsolve(verbosity=0)
        min_delay = float(sol["cost"])
        # # # print "Optimised l"
        # # print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
        l_qp = [float(x) for x in sol(l)]
        # print "sum l: ", sum(sol(l))
        
        print "QP / GP:"
        dif = [abs(l_qp[i] - l_gp[i]) for i in range(len(l_qp))]
        print l_gp, p.get_delay(fixed_s, l_gp)
        print l_qp, p.get_delay(fixed_s, l_qp)
        print dif
        print sum(dif)

    print ggp_sol, sol_values[-1]

    # print sol_values
    # print fixed_l
    # print fixed_s

def alternate_gp_qp(n, m):
    p = Path(n)

    p.length = n / 2.

    p_in = 5.
    p_out = round(random.random() * 10 + 1, 0)

    p.wire_res = 2 #random.random() * 2.
    p.wire_cap = 2 #random.random() * 2.

    print "Initializing constants:"
    print p_in, p_out, p.wire_cap, p.wire_res, p.gate_cap, p.wire_cap

    print "Finding GGP solution..."
    start = timer()
    M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out)
    sol = M.localsolve(verbosity=0)
    min_delay = float(sol["cost"])
    print "Found GGP solution in", timer() - start, "seconds."

    ggp_sol = min_delay
    ggp_s = [float(si) for si in sol(s)]
    ggp_l = [float(li) for li in sol(l)]
    
    sol_values = []

    epsilon = 0.000000000001

    print "Performing ACS (" + str(m) + " iterations )." 
    
    fixed_l = random_l(n - 1, p.length)
    fixed_l = uniform_l(n - 1, p.length)

    print "Initial l:"
    print fixed_l

    start = timer()
    for i in xrange(m):
        M, s, l = p.build_path_ggp(mode=DELAY_MIN, prim_in = p_in, prim_out = p_out, fixed_l = fixed_l)
        sol = M.solve(verbosity=0)
        min_delay = float(sol["cost"])
        # print "Optimised s"
        # print "Minimum delay is: " + str(min_delay) + " with power " + str(float(sum(sol(s))))
        # print "s:     ", sol(s)
        # print "l:     ", sol(l)
        # print "sum l: ", sum(sol(l))

        sol_values.append(min_delay)
        fixed_s = [float(si) for si in sol(s)]

        P, q, G, h, A, b = p.build_path_qp(fixed_s)
        sol = cvx.solvers.qp(2 * P, q, G, h, A, b)
        fixed_l = [max(epsilon, x) for x in sol['x']]
        sol_values.append(p.get_delay(fixed_s, fixed_l))

    print "Finished ACS in", timer() - start, "seconds."

    print "GGP solution:"
    print "d:     ", ggp_sol
    print "s:     ", ggp_s
    print "l:     ", ggp_l

    print "ACS solution:"
    print "d:     ", min_delay
    print "s:     ", fixed_s
    print "l:     ", fixed_l

    rel_sol_values = [v / ggp_sol for v in sol_values]

    plt.plot(rel_sol_values)

    # if ggp_sol * (1. + epsilon) < sol_values[-1] or ggp_sol > sol_values[-1] * (1. + epsilon):
    #     print p_in, p_out, p.wire_cap, p.wire_res


if __name__=="__main__":
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    k = int(sys.argv[3])
    
    for i in range(k):
        alternate(n, m)
        # make_run(n)
    # plt.show()

    # for i in range(int(sys.argv[1])):
    #     print "Run", i
    #     n=int(sys.argv[2])
    #     make_run(n)
    
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

