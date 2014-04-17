import networkx as nx

class Bayesian(object):
    '''
    Syntax:

    Fields:

    '''

    def __init__(self, factors=None):
        '''
        Syntax:

        Arguments:

        '''
        if not factors:
            factors = []

        self.graph = nx.DiGraph()
        self.factors = factors

        for factor in self.factors:
            self.graph.add_node(factor.var[-1])
            for parent in factor.parents:
                self.graph.add_edge(parent.var[-1], factor.var[-1])

    def joint(self):
        '''
        Syntax:

        Arguments:

        '''
        res = None
        for fact in self.factors:
            res = fact*res
        return res

    def draw(self):
        '''
        Syntax:

        Arguments:

        '''
        pos = nx.pygraphviz_layout(self.graph, prog='dot')
        nx.draw(self.graph, pos, node_shape='D')


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
##    doctest.testmod(verbose=True)
