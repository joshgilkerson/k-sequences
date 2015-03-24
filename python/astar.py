#!/usr/bin/env python2.6

"""Find a sequence of n elements that has the k-radius property."""


import array
import copy
import heapq
import itertools
import math
import pprint
import sys


class Graph(object):

  def __init__(self, *args, **kwargs):
    self._nodes = kwargs.pop('n')
    edges = kwargs.pop('_edges', None)
    self._set_edges = kwargs.pop('_set_edges', 0)
    self._set_edges_by_node = kwargs.pop('_set_edges_by_node', None)
    super(Graph, self).__init__(*args, **kwargs)
    if self._set_edges_by_node:
      self._set_edges_by_node = copy.copy(self._set_edges_by_node)
    else:
      self._set_edges_by_node = [0 for _ in xrange(self._nodes)]
    edge_count = self._nodes * (self._nodes - 1) / 2
    if not edges:
      self._edges = array.array('B', (0 for _ in xrange(edge_count)))
    else:
      self._edges = array.array('B', edges)
    assert edge_count == len(self._edges)

  def _Idx(self, node1, node2):
    assert node1 != node2
    assert node1 < self._nodes
    assert node2 < self._nodes
    big = max(node1, node2)
    small = min(node1, node2)
    return big * (big - 1) / 2 + small

  def SetEdge(self, node1, node2, set=True):
    index = self._Idx(node1, node2)
    if bool(self._edges[index]) != bool(set):
      self._edges[index] = 1 if set else 0
      self._set_edges += 1 if set else -1
      self._set_edges_by_node[node1] += 1 if set else -1
      self._set_edges_by_node[node2] += 1 if set else -1

  def HasEdge(self, node1, node2):
    return bool(self._edges[self._Idx(node1, node2)])

  def CountEdges(self):
    return self._set_edges

  def CountMissingEdges(self):
    all_edges = self._nodes * (self._nodes - 1) / 2
    return all_edges - self.CountEdges()

  def CountEdgesByNode(self, node):
    return self._set_edges_by_node[node]

  def CountMissingEdgesByNode(self, node):
    return self._nodes - 1 - self.CountEdgesByNode(node)

  def Copy(self):
    return Graph(n=self._nodes, _edges=self._edges, _set_edges=self._set_edges,
                 _set_edges_by_node=self._set_edges_by_node)


class Sequence(object):

  def __init__(self, *args, **kwargs):
    self._head = kwargs.pop('head', None)
    self._tail = kwargs.pop('tail')
    super(Sequence, self).__init__(*args, **kwargs)
    if self._head:
      self._len = len(self._head) + 1
    else:
      self._len = 1

  def __iter__(self):
    if self._head:
      for i in self._head:
        yield i
    yield self._tail

  def __repr__(self):
    return repr(list(self))

  def __str__(self):
    return pprint.pformat(list(self))

  def __len__(self):
    return self._len

  def GetTrailing(self, n):
    assert n >= 0
    if n == 0:
      return []
    elif n == 1:
      return [self._tail]
    elif not self._head:
      return [self._tail]
    else:
      return self._head.GetTrailing(n - 1) + [self._tail]


class ScoredSequence(object):

  @staticmethod
  def _UpdateScoreGraph(g, from_node, to_nodes):
    for i in to_nodes:
      if i == from_node: continue
      g.SetEdge(from_node, i)

  def __init__(self, *args, **kwargs):
    self._alphabet_size = kwargs.pop('n', None)
    self._radius = kwargs.pop('k', None)
    head = kwargs.pop('head', None)
    tail = kwargs.pop('tail', None)
    super(ScoredSequence, self).__init__(*args, **kwargs)
    if self._radius:
      assert self._alphabet_size
      assert not head
      assert not tail
      self._sequence = None
      self._score_graph = Graph(n=self._alphabet_size)
      self.largest_element = None
    else:
      assert not self._alphabet_size
      assert head is not None
      assert tail is not None
      self._alphabet_size = head._alphabet_size
      self._radius = head._radius
      self._score_graph = head._score_graph.Copy()
      head_trailing = []
      if head._sequence:
        ScoredSequence._UpdateScoreGraph(
            self._score_graph, tail, head._sequence.GetTrailing(self._radius))
      self._sequence = Sequence(head=head._sequence, tail=tail)
      self.largest_element = tail
      if head.largest_element:
        self.largest_element = max(tail, head.largest_element)

  def MissingEdges(self):
    return self._score_graph.CountMissingEdges()

  def MissingEdgesByNode(self, node):
    return self._score_graph.CountMissingEdgesByNode(node)

  def __len__(self):
    if self._sequence:
      return len(self._sequence)
    else:
      return 0

  def __repr__(self):
    if self._sequence:
      return repr(self._sequence)
    else:
      return '[]'

  def __str__(self):
    if self._sequence:
      return str(self._sequence)
    else:
      return '[]'

  @property
  def tail(self):
    return self._sequence.GetTrailing(1)[0]

  def GetTrailing(self, n):
    if self._sequence:
      return self._sequence.GetTrailing(n)
    else:
      return []


def GenerateNextNodes(node, n):
  # Only add one element that is not already in node, since all new elements are
  # equivalent.
  for i in xrange(n):
    if len(node) and node.tail == i: continue
    yield ScoredSequence(head=node, tail=i)
    if (node.largest_element is None or node.largest_element < i):
      break


def TheoreticalLowerBoundKEquals1(n):
  # Ghosh 1975
  val = n * (n - 1) / 2
  if n % 2 == 0:
    val += n / 2
  else:
    val += 1
  return val


def TheoreticalLowerBoundKEquals2(n):
  # Corollary from paper.
  val = n * (n - 1) / 4.0
  mod4 = n % 4
  if mod4 == 0:
    val += n / 4.0 + 1
  elif mod4 == 1:
    val += 2
  elif mod4 == 2:
    val += 0.75 * n
  else:
    val += 0.5 * n
  return math.ceil(val)


def TheoreticalLowerBoundWeak(k, n):
  # JL04 Note, there is a slightly stronger version, but it is harder to
  # compute.
  return math.ceil(n * (n - 1) / 2.0 / k + (k + 1) / 2.0)


def TheoreticalLowerBoundNoMemo(k, n):
  assert k
  if n == 0:
    return 0
  if k == 1:
    return TheoreticalLowerBoundKEquals1(n)
  elif k == 2:
    return TheoreticalLowerBoundKEquals2(n)
  else:
    return TheoreticalLowerBoundWeak(k, n)


def TheoreticalLowerBound(k, n, __memo={}):
  val = __memo.get((k, n), None)
  if val is None:
    val = TheoreticalLowerBoundNoMemo(k, n)
  return val


# upper bound
def TheoreticalUpperBound(k, n):
  if n == 1: return 1
  if k == 1: return n * (n - 1) / 2 + n # This can likely be tighter.
  if n == 2: return 2
  val = TheoreticalUpperBound(k-1, n-1)
  val += math.ceil(val / k / 2.0)
  return val


def Index(l, v):
  try:
    return l.index(v)
  except ValueError:
    return len(l)


def ScoreNode(node, k, n):
  min_remaining = []
  min_remaining.append(math.ceil(float(node.MissingEdges()) / k))
  missing_edges = [node.MissingEdgesByNode(i) for i in xrange(n)]
  trailing = node.GetTrailing(k)
  trailing.reverse()
  idxs = (Index(trailing, i) for i in xrange(n))
  min_remaining.append(sum(max(0, math.ceil((i - k + idx) / 2.0 / k))
                           for i, idx in itertools.izip(missing_edges, idxs)))
  #min_remaining.append(sum(max(0, math.ceil((i - k) / 2.0 / k))
                           #for i in missing_edges))
  #This doesn't work. It should get the largest complete graph, not the highest
  #largest degree node in the inverted graph.
  #min_remaining.append(TheoreticalLowerBound(k, min(missing_edges)) - k)
  #min_remaining.append(TheoreticalLowerBound(k, min(missing_edges)))
  return len(node) + max(min_remaining)


def Done(node):
  return not node.MissingEdges()


def Astar(initial_node, next_nodes, score, done):
  current = initial_node
  heap = [(score(current), 0, current)]
  while not done(current):
    for i in next_nodes(current):
      score_i = score(i)
      secondary_i = 0 if done(i) else 1
      heapq.heappush(heap, (score_i, secondary_i, i))
    _, _, current = heapq.heappop(heap)
  assert done(current)
  return current


def main(argv):
  assert len(argv) == 3
  radius = int(argv[1])
  alphabet_size = int(argv[2])
  initial_node = ScoredSequence(k=radius, n=alphabet_size)
  next_nodes = lambda node: GenerateNextNodes(node, alphabet_size)
  score = lambda node: ScoreNode(node, radius, alphabet_size)
  result = Astar(initial_node, next_nodes, score, Done)
  print 'radius: %d' % radius
  print 'alphabet size: %d' % alphabet_size
  print 'length: %d' % len(result)
  print 'result:'
  print result


if __name__ == '__main__':
  main(sys.argv)
