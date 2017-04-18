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
        if not isinstance(child, (BNode, Literal)):
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
    def write_png(self, filename):
        to_agraph(self.nx).draw(filename, format='png', prog='dot')

def main():
    # create example graph
    g = NXRDF()

    bismarck = g.add_node()
    g.add_edge(bismarck, 'name', 'Bismarck')

    one_ca_nd = g.add_node()
    g.add_edge(one_ca_nd, 'type', 'predicate')
    ca = g.add_node()
    g.add_edge(one_ca_nd, 'source', ca)
    g.add_edge(ca, 'name', 'California')
    nd = g.add_node()
    g.add_edge(bismarck, 'city_state', nd)
    g.add_edge(nd, 'name', 'North Dakota')
    g.add_edge(one_ca_nd, 'destination', nd)
    unknown_dist_1 = g.add_node()
    g.add_edge(one_ca_nd, 'distance', unknown_dist_1)

    two_nd_wi = g.add_node()
    g.add_edge(two_nd_wi, 'type', 'predicate')
    wisco = g.add_node()
    g.add_edge(wisco, 'name', 'Wisconsin')
    g.add_edge(two_nd_wi, 'source', wisco)
    g.add_edge(two_nd_wi, 'destination', nd)
    unknown_dist_2 = g.add_node()
    g.add_edge(two_nd_wi, 'distance', unknown_dist_2)
    g.add_edge(unknown_dist_1, 'greater_than', unknown_dist_2)

    three_city_nd = g.add_node()
    g.add_edge(three_city_nd, 'type', 'predicate')
    arb_wi_city = g.add_node()
    g.add_edge(arb_wi_city, 'name', 'Arbitrary Wisconsin City')
    g.add_edge(three_city_nd, 'source', arb_wi_city)
    unknown_dist_3 = g.add_node()
    g.add_edge(three_city_nd, 'destination', bismarck)
    g.add_edge(three_city_nd, 'distance', unknown_dist_3)
    g.add_edge(arb_wi_city, 'city_state', wisco)

    four_city_nd = g.add_node()
    g.add_edge(four_city_nd, 'type', 'predicate')
    arb_ca_city = g.add_node()
    g.add_edge(arb_ca_city, 'name', 'Arbitrary California City')
    g.add_edge(four_city_nd, 'source', arb_ca_city)
    g.add_edge(four_city_nd, 'destination', bismarck)
    unknown_dist_4 = g.add_node()
    g.add_edge(four_city_nd, 'distance', unknown_dist_4)
    g.add_edge(arb_ca_city, 'city_state', ca)
    g.add_edge(unknown_dist_4, 'greater_than', unknown_dist_3)

    san_fran = g.add_node()
    g.add_edge(san_fran, 'name', 'San Francisco')
    g.add_edge(san_fran, 'city_state', ca)
    la = g.add_node()
    g.add_edge(la, 'name', 'Los Angeles')
    g.add_edge(la, 'city_state', ca)
    geneva = g.add_node()
    g.add_edge(geneva, 'name', 'Lake Geneva')
    g.add_edge(geneva, 'city_state', wisco)
    greenbay = g.add_node()
    g.add_edge(greenbay, 'name', 'Greenbay')
    g.add_edge(greenbay, 'city_state', wisco)
    madison = g.add_node()
    g.add_edge(madison, 'name', 'Madison')
    g.add_edge(madison, 'city_state', wisco)

    g.add_edge(bismarck, 'isa', 'city')
    g.add_edge(san_fran, 'isa', 'city')
    g.add_edge(la, 'isa', 'city')
    g.add_edge(geneva, 'isa', 'city')
    g.add_edge(greenbay, 'isa', 'city')
    g.add_edge(madison, 'isa', 'city')

    g.add_edge(wisco, 'isa', 'state')
    g.add_edge(nd, 'isa', 'state')
    g.add_edge(ca, 'isa', 'state')


    # print graph in graphviz format
    print(g.to_dot())
    g.write_png('temp.png')
    # do a query ("name all animals that have fur")
    # find all cities in California

    qres = g.query(

        '''
        SELECT DISTINCT ?city_name1 ?city_name
        WHERE {
            ?city nxrdf:isa "city" ;
                  nxrdf:city_state ?state ;
                  nxrdf:name ?city_name .
            ?state nxrdf:isa "state" ;
                  nxrdf:name "California" .
            ?state1 nxrdf:isa "state" ;
                  nxrdf:name "Wisconsin" .
            ?city1 nxrdf:isa "city" ;
                  nxrdf:city_state ?state1 ;
                  nxrdf:name ?city_name1 .

        }
    '''
    )

    print("Results of the Query:")
    for row in qres:
        print(row)

if __name__ == '__main__':
    main()
