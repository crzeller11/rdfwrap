from networkx import DiGraph
from networkx.drawing.nx_agraph import to_agraph
from rdflib import Graph as RDFGraph, BNode, Literal, Namespace

class NXRDF:
    NAMESPACE = Namespace('http://justinnhli.com/attr#')
    def __init__(self):
        self.nx = DiGraph()
        self.rdf = RDFGraph()
        self.rdf.bind('nxrdf', NXRDF.NAMESPACE)
        self.node_id = 0
    def add_edge(self, parent, label, child, **kwargs):
        assert isinstance(parent, BNode)
        assert isinstance(label, str)
        if not (isinstance(child, BNode) or isinstance(child, Literal)):
            child = self.add_literal(child)
        self.rdf.add((parent, NXRDF.NAMESPACE[label], child))
        self.nx.add_edge(parent, child, label=label, **kwargs)
    def add_node(self, **kwargs):
        node = BNode('N{}'.format(self.node_id))
        self.node_id += 1
        self.nx.add_node(node, **kwargs)
        return node
    def add_literal(self, value, **kwargs):
        node = Literal(value)
        self.nx.add_node(node, **kwargs)
        return node
    def query(self, sqarql):
        return self.rdf.query(sqarql)
    def to_dot(self):
        return to_agraph(self.nx)

def main():
    # create example graph
    g = NXRDF()
    mammal = g.add_node()
    g.add_edge(mammal, 'name', 'mammal')
    cat = g.add_node()
    g.add_edge(cat, 'name', 'cat')
    bear = g.add_node()
    g.add_edge(bear, 'name', 'bear')
    fur = g.add_node()
    g.add_edge(fur, 'name', 'fur')
    g.add_edge(cat, 'has', fur)
    g.add_edge(bear, 'has', fur)
    g.add_edge(cat, 'isa', mammal)
    g.add_edge(bear, 'isa', mammal)
    # print graph in graphviz format
    print(g.to_dot())
    # do a query ("name all animals that have fur")
    qres = g.query('''
        SELECT DISTINCT ?animal_name
        WHERE {
            ?animal nxrdf:has ?fur ;
                    nxrdf:name ?animal_name .
            ?fur nxrdf:name "fur" .
        }
    ''')
    for row in qres:
        print(row)

if __name__ == '__main__':
    main()
