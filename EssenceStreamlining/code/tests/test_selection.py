import Search.Lattice as Lattice
import Search.Selection as Selection

# Test that UCT Selection performs as expected
def test_uct_selection(mocker):
    lattice =  Lattice.Lattice()
    lattice.add_node('')
    lattice.get_graph().nodes['']['last_visited'] = 0
    lattice.get_graph().nodes['']['visited_count'] = 2
    lattice.get_graph().nodes['']['score'] = 1
    lattice.add_node('1')
    lattice.add_edge('', '1')
    lattice.get_graph().nodes['1']['last_visited'] = 0
    lattice.get_graph().nodes['1']['visited_count'] = 1
    lattice.get_graph().nodes['1']['score'] = 1
    lattice.add_node('2')
    lattice.add_edge('', '2')
    lattice.get_graph().nodes['2']['last_visited'] = 1
    lattice.get_graph().nodes['2']['visited_count'] = 1
    lattice.get_graph().nodes['2']['score'] = 0

    current_combination = set()
    result = Selection.UCTSelection().uct_values(lattice, current_combination, ['1','2'])

    assert(round(result['1'], 2), 1.08)
    assert(round(result['2'], 2), 0.08)
