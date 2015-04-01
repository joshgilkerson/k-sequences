package graph

import "testing"

func TestNewWeightedUndirectedGraph(t *testing.T) {
  g := NewWeightedUndirectedGraph(2)
  if len(g.rows) != 2 {
    t.Errorf("rows should have length 2, has %d", len(g.rows))
  }
  if g.nodeCount != 2 {
    t.Errorf("nodeCount should be 2, is %d", g.nodeCount)
  }
  if len(g.rows[g.nodeCount-1]) != 2 {
    t.Errorf("rows last element  should have length 2, has %d",
      len(g.rows[g.nodeCount-1]))
  }
}

func EnsureSymmetry(t *testing.T, g *WeightedUndirectedGraph) {
  for i := 0; i < int(g.nodeCount); i++ {
    for j := 0; j < i; j++ {
      var w1, w2 Weight
      var e error
      if w1, e = g.Get(NodePair{Node(i), Node(j)}); e != nil {
        t.Errorf("Get(%d, %d) failed. %s", i, j, e.Error())
        continue
      }
      if w2, e = g.Get(NodePair{Node(j), Node(i)}); e != nil {
        t.Errorf("Get(%d, %d) failed. %s", j, i, e.Error())
        continue
      }
      if w1 != w2 {
        t.Errorf("Assymetry at (%d, %d) %d vs %d.", i, j, w1, w2)
      }
    }
  }
}

func TestInitialState(t *testing.T) {
  g := NewWeightedUndirectedGraph(7)
  EnsureSymmetry(t, g)
  allZeroes := func(nodes NodePair, weight Weight) {
    if weight != 0 {
      t.Errorf("Found non-zero node (%d, %d) with weight %d",
        nodes[0], nodes[1], weight)
    }
  }
  if e := g.Scan(allZeroes); e != nil {
    t.Errorf("Error from g.Scan(allZeroes): %s", e.Error())
  }
}

func TestSetOneAtATime(t *testing.T) {
  const nodeCount uint = 7
  var i, j uint

  visitor := func(nodes NodePair, weight Weight) {
    n0 := uint(nodes[0])
    n1 := uint(nodes[1])
    if (n0 < i && n1 < i) || (n0 == i && n1 <= j) || (n1 == i && n0 <= j){
      if weight == Weight(n0 + n1) {
        return
      }
    } else {
      if weight == 0 {
        return
      }
    }
    t.Errorf("Unexpected weight %d at %d,%d with i,j at %d,%d.",
        weight, n0, n1, i, j)
  }

  g := NewWeightedUndirectedGraph(nodeCount)
  for i = 0; i < nodeCount; i++ {
    for j = 0; j < i; j++ {
      if e := g.Set(NodePair{Node(i), Node(j)}, Weight(i + j)); e != nil {
        t.Errorf("error from Set(%d, %d): %s", i, j, e)
        continue
      }
      EnsureSymmetry(t, g)
      if e := g.Scan(visitor); e != nil {
        t.Errorf("Error from g.Scan(visitor) i,j=%d,%d: %s", i, j, e.Error())
      }
    }
  }
}

func TestScanVisitsAllEdges(t *testing.T) {
  const nodeCount int = 7
  const expectedEdgeCount int = nodeCount * (nodeCount - 1) / 2
  edgesVisited := make([]NodePair, 0, expectedEdgeCount)

  visitor := func(nodes NodePair, _ Weight) {
    edgesVisited = append(edgesVisited, nodes)
  }
  g := NewWeightedUndirectedGraph(uint(nodeCount))
  if e := g.Scan(visitor); e != nil {
    t.Errorf("Error from g.Scan(visitor): %s", e.Error())
    return
  }
  if len(edgesVisited) < expectedEdgeCount {
    t.Errorf("Not all edges visited: %d vs %d expected.",
        len(edgesVisited), expectedEdgeCount)
  } else if len(edgesVisited) > expectedEdgeCount {
    t.Errorf("Extra edges visited: %d vs %d expected.",
        len(edgesVisited), expectedEdgeCount)
  }

  edgesVisitedSet := make(map[NodePair]bool)
  for _, nodes := range edgesVisited {
    if int(nodes[0]) >= nodeCount || int(nodes[1]) >= nodeCount {
      t.Errorf("Node out of bounds >%d in pair %d,%d.", nodeCount, nodes[0],
        nodes[1])
    }
    if edgesVisitedSet[nodes] {
      t.Errorf("Duplicate edge visited: %d,%d", nodes[0], nodes[1])
    }
    edgesVisitedSet[nodes] = true
  }
}
