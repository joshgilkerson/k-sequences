package graph

import "testing"

func TestNew(t *testing.T) {
	g := NewWeightedUndirectedGraph(2)
	if len(g.Rows) != 2 {
		t.Errorf("Rows should have length 2, has %d",
			len(g.Rows))
		t.Fail()
	}
	if len(g.Rows[len(g.Rows)-1]) != 2 {
		t.Errorf("Rows last element  should have length 2, has %d",
			len(g.Rows))
		t.Fail()
	}
}

func TestSimple(t *testing.T) {
	g := NewWeightedUndirectedGraph(10)
	for i := 0; i < 10; i++ {
		for j := 0; j < 10; j++ {
			w := int(g.Get(NodePair{Node(i), Node(j)}))
			if w != 0 {
				t.Errorf("Wrong weight at (%d, %d). Expected 0, Found %d.",
					i, j, w)
				t.Fail()
			}
		}
	}
}
