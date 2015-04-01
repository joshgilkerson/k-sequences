package graph

import "errors"
import "fmt"

type Status int
type Weight int
type Node int
type NodePair [2]Node

type WeightedUndirectedGraph struct {
  rows [][]Weight
  nodeCount uint
}

func NewWeightedUndirectedGraph(nodeCount uint) *WeightedUndirectedGraph {
  rows := make([][]Weight, 0, nodeCount)
  for i := uint(0); i < nodeCount; i++ {
    rows = append(rows, make([]Weight, i+1))
    // 0 -> Linearized[0:1]
    // 1 -> Linearized[1:3]
    // 2 -> Linearized[3:6]
  }
  return &WeightedUndirectedGraph{rows, nodeCount}
}

func (g *WeightedUndirectedGraph) getEdge(nodes NodePair) (w *Weight, e error) {
  w = nil
  e = nil
  for _, node := range nodes {
    if uint(node) >= g.nodeCount {
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
    w = &(g.rows[nodes[1]][nodes[0]])
  } else {
    w = &(g.rows[nodes[0]][nodes[1]])
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

type Visitor func(nodes NodePair, weight Weight)

func (g *WeightedUndirectedGraph) Scan(v Visitor) error {
  for i := uint(0); i < g.nodeCount; i++ {
    for j := uint(0); j < i; j++ {
      nodes := NodePair{Node(i), Node(j)}
      if w, e := g.Get(nodes); e != nil {
        return e
      } else {
        v(nodes, w)
      }
    }
  }
  return nil
}
