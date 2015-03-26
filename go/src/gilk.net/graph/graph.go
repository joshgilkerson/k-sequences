package graph

import "errors"
import "fmt"

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

func (g *WeightedUndirectedGraph) getEdge(nodes NodePair) (w *Weight, e error) {
  w = nil
  e = nil
  for _, node := range nodes {
    if int(node) > len(g.Rows) {
      e = errors.New(fmt.Sprintf(
        "Node out of bounds: %d",
        node))
      return
    }
  }
  if nodes[0] == nodes[1] {
    e = errors.New("Self-edges are not supported.")
    return
  }
  if nodes[0] < nodes[1] {
    w = &(g.Rows[nodes[1]][nodes[0]])
  } else {
    w = &(g.Rows[nodes[0]][nodes[0]])
  }
  return
}

func (g *WeightedUndirectedGraph) Set(nodes NodePair, weight Weight) error {
  if edge, error := g.getEdge(nodes); error == nil {
    *edge = weight
    return nil
  } else {
    return error
  }
}

func (g *WeightedUndirectedGraph) Get(nodes NodePair) (Weight, error) {
  if edge, error := g.getEdge(nodes); error == nil {
    return *edge, nil
  } else {
    return 0, error
  }
}
