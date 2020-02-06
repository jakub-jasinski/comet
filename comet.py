import numpy as np
import itertools as it



class Comet:
    def __init__(self, alternatives, num_cv, mej=None):
        self.alternatives = np.array(alternatives)
        self.inputs_range = []
        for i in range(alternatives.shape[1]):
            self.inputs_range.append((min(self.alternatives[:, i]), max(self.alternatives[:, i])))
        self.num_cv = num_cv
        self.CVs = []
        for inp in self.inputs_range:
            self.CVs.append(np.linspace(inp[0], inp[1], num=num_cv))
        self.CVs = np.array(self.CVs)
        if mej is None:
            self.mej = self.generate_mej()
        else:
            self.mej = mej
        self.fit()

    @staticmethod
    def cartesian(arrays, out=None):
        arrays = [np.asarray(x) for x in arrays]
        dtype = arrays[0].dtype

        n = np.prod([x.size for x in arrays])
        if out is None:
            out = np.zeros([n, len(arrays)], dtype=dtype)

        m = n / arrays[0].size
        out[:, 0] = np.repeat(arrays[0], m)
        if arrays[1:]:
            Comet.cartesian(arrays[1:], out=out[0:m, 1:])
            for j in range(1, arrays[0].size):
                out[j * m:(j + 1) * m, 1:] = out[0:m, 1:]
        return out

    @staticmethod
    def mi(a, m, b, x):
        if x < a:
            return 0
        elif a <= x < m:
            return (x - a) / (m - a)
        elif x == m:
            return 1
        elif a < x <= b:
            return (b - x) / (b - m)
        elif x > b:
            return 0

    def fit(self):
        self.sj = self.calc_sj()
        self.p = self.calc_p()
        self.COs = list(it.product(*self.CVs))
        self.rules = list(zip(self.COs, self.p))
        #self.print_rules()

    def generate_mej(self):
        size = 1
        for cvs in self.CVs:
            size *= len(cvs)
        mej = np.random.choice((0, 0.5, 1), (size, size))
        np.fill_diagonal(mej, 0.5)
        for i in range(size):
            for j in range(i,size):
                mej[i, j] = 1 - mej[j, i]
        return mej

    def calc_sj(self):
        sj = []
        for i in range(self.mej.shape[0]):
            sj.append(sum(self.mej[i, :]))
        #print(sj)
        return sj

    def calc_p(self):
        k = len(np.unique(self.sj))
        P = np.zeros(len(self.mej))
        mySJ = np.copy(self.sj)
        for i in range(1, k):
            ind = np.where(mySJ == max(mySJ))
            P[ind] = (k-i)/(k-1)
            mySJ[ind] = 0
        #print(P)
        return P

    def print_rules(self):
        for rule in self.rules:
            print("IF", end=" ")
            for i, co in enumerate(rule[0]):
                if i is not len(rule[0])-1:
                    print(("C{}".format(i))+" = {}".format(co)+" AND ", end="")
                else:
                    print(("C{}".format(i)) + " = {}".format(co), end=" ")
            print("THEN P = {}".format(rule[1]))

    def _eval(self, inp):
        P = []
        activs = []
        for rule in self.rules:
            rule_activation = 1
            for i, c in enumerate(rule[0]):
                if c == min(self.CVs[i]):
                    activation = Comet.mi(c, c, self.CVs[i][1], inp[i])
                elif c == max(self.CVs[i]):
                    activation = Comet.mi(self.CVs[i][len(self.CVs[i])-2], c, c, inp[i])
                else:
                    activation = Comet.mi(self.CVs[i][(np.where(self.CVs[i] == c))[0][0]-1], c, self.CVs[i][(np.where(self.CVs[i] == c))[0][0] + 1], inp[i])
                rule_activation *= activation
            activs.append(rule_activation)
            p = rule_activation * rule[1]
            P.append(p)
        return sum(P)

    def evaluate(self):
        out = []
        for sample in self.alternatives:
            out.append(self._eval(sample))
        return out
