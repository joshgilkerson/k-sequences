package graph

type Status int
type Weight int
type Node int
type NodePair [2]Node

type WeightedUndirectedGraph struct {
	Rows [][]Weight
}

func NewWeightedUndirectedGraph(nodeCount int) *WeightedUndirectedGraph {
	rows := make([][]Weight, 0, nodeCount)
	for i := 0; i < nodeCount; i++ {
		rows = append(rows, make([]Weight, i+1))
		// 0 -> Linearized[0:1]
		// 1 -> Linearized[1:3]
		// 2 -> Linearized[3:6]
	}
	return &WeightedUndirectedGraph{rows}
}

func sortedNodes(nodes NodePair) (Node, Node) {
	if nodes[0] < nodes[1] {
		return nodes[0], nodes[1]
	} else {
		return nodes[1], nodes[0]
	}
}

func (g *WeightedUndirectedGraph) getEdge(nodes NodePair) *Weight {
	if int(nodes[0]) > len(g.Rows) {
		return nil
	} else {
		n1, n2 := sortedNodes(nodes)
		return &(g.Rows[n2][n1])
	}
}

func (g *WeightedUndirectedGraph) Set(nodes NodePair, weight Weight) {
	(*g.getEdge(nodes)) = weight
}

func (g *WeightedUndirectedGraph) Get(nodes NodePair) Weight {
	edge := g.getEdge(nodes)
	if edge == nil {
		return 0
	} else {
		return *edge
	}
}
