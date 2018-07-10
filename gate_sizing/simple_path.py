import gpkit as gp

# s1 = gp.Variable("s1")
# s2 = gp.Variable("s2")

# l1 = gp.Variable("l1")
# l2 = gp.Variable("l2")

# d1 = (s2 + l1) / s1
# d2 = (s1 + l2) / s2
# d3 = l1 * s2 + l1 * l1
# d4 = l2 * s1 + l2 * l2

# c1 = (s1 >= 1)
# c2 = (s2 >= 1)
# c3 = (s1 <= 3)
# c4 = (s2 <= 3)
# c5 = l1 <= 1
# c6 = l2 <= 1

# with gp.SignomialsEnabled():
#     c0 = (l1 + l2 >= 1)


# M = gp.Model(d1 + d2 + d3 + d4, [c1, c2, c3, c4, c5, c6, c0])
# sol = M.localsolve(verbosity=0)
# print sol.table()

class Path:
    def __init__(self, n):
        self.length = 1
        
        self.smin = 1
        self.smax = 4
        self.lmin = 0
        self.lmax = self.length
        
        self.n = n
        
    def build_path_ggp(self,  prim_in=0, prim_out=0):
        s = gp.VectorVariable(self.n, "s")
        l = gp.VectorVariable(self.n - 1, "l")
    
        delay = self.__get_delay_function(s, l)

        constraints = []
        self.__set_bounds(s, l, constraints)
        self.__set_l_sum(l, constraints)
        self.__set_primary_in_out(s, prim_in, prim_out, constraints)
      
        return gp.Model(delay, constraints)
    
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
        
#        constraints.append((l_sum <= self.length * (1 + tol)))
        
        with gp.SignomialsEnabled():
            constraints.append((l_sum >= self.length))
    
    def __set_bounds(self, s, l, constraints):
        s_min = gp.VectorVariable(self.n, "smin", [self.smin for dummy in xrange(self.n)])
        s_max = gp.VectorVariable(self.n, "smax", [self.smax for dummy in xrange(self.n)])
        l_min = gp.VectorVariable(self.n - 1, "lmin", [self.lmin for dummy in xrange(self.n - 1)])
        l_max = gp.VectorVariable(self.n - 1, "lmax", [self.lmax for dummy in xrange(self.n - 1)])
        
        for i in range(self.n):
            constraints.append(s[i] <= s_max[i])
            constraints.append(s[i] >= s_min[i])
        for i in range(self.n - 1):
            constraints.append(l[i] <= l_max[i])
            constraints.append(l[i] >= l_min[i])

    def __delay(self, i, s, l):
        d = 0
        d += (s[i+1] + l[i]) / s[i]
        d += s[i] * l[i-1] + l[i-1]*l[i-1]        
        return d
        


n = 3
p = Path(n)
for i in range(1):
    p.smax = i + 1
    M = p.build_path_ggp(i + 1, i + 1)
    sol = M.localsolve(verbosity=0)
    print sol.table(tables=("cost", "freevariables"))

