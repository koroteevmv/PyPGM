'''
    Random variable is the basic building block fo Bayesian and Markov nets.
    Variable can be assigned to one of given set of values. This class
    represents discrete variable.
'''

class Variable(object):
    '''
    Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake']);
            >>> B = Variable("Burglary",  [0, 1]);
            >>> A = Variable("Alarm", 3);
            >>> R = Variable("Radio", 2)

    Fields:
        name
            string representing the name of the variable. Assuming
            this is readble full name. This name is used for representing.
        value
            list of all possible values. Elements can be any type with defined
            equality operation
        card
            cardinality of the variable - number of all possible values

    '''

    def __init__(self, name, a):
        '''
        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> print E.name
            Eartquake
            >>> E.card
            2
            >>> E.value
            ['still', 'shake']
            >>> E = Variable("Eartquake", 3)
            >>> E.value
            [0, 1, 2]
            >>> E.card
            3

        Arguments:
            name
                string representing the name of the variable. Assuming
                this is readble full name. This name is used for representing.
            a
                if list, represent full set of possible variable's values
                if int,  represent number of value (cardinality). Values in this
                case are integers from 0 to a-1.
        '''
        self.name = name                # имя переменной
        self.value = []                 # значения переменной
        self.card = 0                   # мощность переменной

        if  type(a) == int:             # cardinality passed
            self.card = a
            for i in range(a):
                self.value.append(i)
        elif type(a) == list:            # values list passed
            self.value = a
            self.card = len(a)

    def find_value(self, val):
        '''
        Given value finds its number among variable's values.
        If val is not in list of values, returns None

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> E.find_value('still')
            0
            >>> E.find_value('shake')
            1
            >>> E = Variable("Eartquake", 3)
            >>> E.find_value(1)
            1
            >>> E.find_value(2)
            2

        Arguments:
            val
                one of the values of this variable
        '''
        for j in range(len(self.value)):
            if self.value[j] == val:
                return j

    def __abs__(self):
        '''
        Returns cardinality of the variable

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> abs(E)
            2
            >>> E = Variable("Eartquake", 3)
            >>> abs(E)
            3
        '''
        return self.card

    def __repr__(self):
        '''
        Represent variable as a string (only name)

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> E
            Eartquake
            >>> E = Variable("Eartquake", 3)
            >>> E
            Eartquake
        '''
        return self.name

    def equal(self, term, value):
        '''
        Computes indicative equality function.
        Returns 0 if term!=value
        Returns 1 if term==value
        Returns None if term is not among self.value
        Syntax:
            >>> V = BinaryVariable("Sample")
            >>> V.equal(0, 0)
            1.0
            >>> V.equal(1, 0)
            0.0
            >>> V.equal(2, 0)
            >>> print V.equal(2, 0)
            None

        Arguments:
            term
                one of the values of this variable
            value
                value to be tested for equality with term
        '''
        if term in self.value:
            return float(term == value)
        return None

class BinaryVariable(Variable):
    '''
    Particular case of the variable with only two possible values: 0 and 1
    '''
    def __init__(self, name):
        '''
        Syntax:
            >>> E = BinaryVariable('coin flip')
            >>> E
            coin flip
            >>> abs(E)
            2
            >>> E.value
            [0, 1]
            >>> E.find_value(1)
            1

        Arguments:
            name
                string representing the name of the variable. Assuming
                this is readble full name. This name is used for representing.
        '''
        Variable.__init__(self, name, [0, 1])
        self.name = name
        self.value = [0, 1]
        self.card = 2


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
##    doctest.testmod(verbose=True)
