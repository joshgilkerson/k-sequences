#!/usr/bin/env pytest

import itertools
import logging
import multiprocessing
import unittest

import astar
import astar_multi


logging.basicConfig(filename='/dev/stderr', level=logging.DEBUG)

class GraphTest(unittest.TestCase):

  def testTiny(self):
    g = astar.Graph(n=2)
    assert g.CountEdges() == 0
    assert g.CountMissingEdges() == 1
    assert not g.HasEdge(0, 1)
    assert 0 == g.CountEdgesByNode(0)
    assert 0 == g.CountEdgesByNode(1)
    assert 1 == g.CountMissingEdgesByNode(0)
    assert 1 == g.CountMissingEdgesByNode(1)

  def testSmallEmpty(self):
    g = astar.Graph(n=3)
    assert g.CountEdges() == 0
    assert g.CountMissingEdges() == 3
    for i in xrange(3):
      assert 0 == g.CountEdgesByNode(i)
      assert 2 == g.CountMissingEdgesByNode(i)
      for j in xrange(i):
        assert not g.HasEdge(i, j)
        assert not g.HasEdge(j, i)

  def testSmallFull(self):
    g = astar.Graph(n=3)
    assert g.CountEdges() == 0
    assert g.CountMissingEdges() == 3
    for i in xrange(3):
      for j in xrange(i):
        assert not g.SetEdge(i, j)
    for i in xrange(3):
      assert 2 == g.CountEdgesByNode(i)
      assert 0 == g.CountMissingEdgesByNode(i)
      for j in xrange(i):
        assert g.HasEdge(j, i)
        assert g.HasEdge(j, i)
    assert g.CountEdges() == 3
    assert g.CountMissingEdges() == 0

  def testSetUnset(self):
    g = astar.Graph(n=3)
    g.SetEdge(1, 2)
    assert g.HasEdge(1, 2)
    g.SetEdge(1, 2, set=False)
    assert not g.HasEdge(1, 2)

  def testSymmetry(self):
    g = astar.Graph(n=3)
    g.SetEdge(1, 2)
    assert g.HasEdge(2, 1)

  def testCopyIsDeep(self):
    g1 = astar.Graph(n=3)
    g1.SetEdge(1, 2)
    g2 = g1.Copy()
    assert g2.HasEdge(1, 2)
    g2.SetEdge(1, 2, set=False)

    assert not g2.HasEdge(1, 2)
    assert 0 == g2.CountEdges()
    assert 3 == g2.CountMissingEdges()
    assert 2 == g2.CountMissingEdgesByNode(0)
    assert 2 == g2.CountMissingEdgesByNode(1)
    assert 2 == g2.CountMissingEdgesByNode(2)

    assert g1.HasEdge(1, 2)
    assert 1 == g1.CountEdges()
    assert 2 == g1.CountMissingEdges()
    assert 2 == g1.CountMissingEdgesByNode(0)
    assert 1 == g1.CountMissingEdgesByNode(1)
    assert 1 == g1.CountMissingEdgesByNode(2)


class SequenceTest(unittest.TestCase):

  def testConstructionAndIteration(self):
    s1 = astar.Sequence(tail=1)
    s2 = astar.Sequence(head=s1, tail=2)
    s3 = astar.Sequence(head=s2, tail=3)
    assert [1, 2, 3] == list(s3)

  def testRepr(self):
    s = astar.Sequence(tail=1)
    s = astar.Sequence(head=s, tail=2)
    assert isinstance(repr(s), str)

  def testStr(self):
    s = astar.Sequence(tail=1)
    s = astar.Sequence(head=s, tail=2)
    assert isinstance(str(s), str)

  def testLen(self):
    s = astar.Sequence(tail=1)
    s = astar.Sequence(head=s, tail=2)
    assert 2 == len(s)

  def testGetTrailing(self):
    s = astar.Sequence(tail=0)
    assert [0] == s.GetTrailing(2)
    s = astar.Sequence(head=s, tail=1)
    s = astar.Sequence(head=s, tail=2)
    s = astar.Sequence(head=s, tail=3)
    s = astar.Sequence(head=s, tail=4)
    s = astar.Sequence(head=s, tail=5)
    s = astar.Sequence(head=s, tail=6)
    s = astar.Sequence(head=s, tail=7)
    assert [6, 7] == s.GetTrailing(2)
    assert [6, 7] == s.GetTrailing(2)


class TheoreticalLowerBoundTest(unittest.TestCase):

  def testKEquals1(self):
    for n, expected in [
        (2, 2),
        (3, 4),
        (4, 8),
        (5, 11),
        (6, 18),
        (7, 22),
        (8, 32),
        (9, 37),
        (10, 50),
        (11, 56),
        (12, 72),
    ]:
      assert expected == astar.TheoreticalLowerBoundKEquals1(n)

  def testKEquals2(self):
    for n, expected in [
        (2, 2),
        (8, 17),
        (9, 20),
        (10, 30),
        (11, 33),
    ]:
      assert expected == astar.TheoreticalLowerBoundKEquals2(n)

  def testWeak(self):
    for k, n, expected in [
        (2, 2, 2),
        (2, 8, 16),
        (2, 9, 20),
        (2, 10, 24),
        (2, 11, 29),
        (3, 3, 3),
        (3, 10, 17),
    ]:
      actual = astar.TheoreticalLowerBoundWeak(k, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)

  def testCombined(self):
    actual = astar.TheoreticalLowerBoundNoMemo(1, 0)
    assert 0 == actual, '%s != 0 (1, 0)' % actual
    for n in xrange(3, 20):
      expected = astar.TheoreticalLowerBoundKEquals1(n)
      actual = astar.TheoreticalLowerBoundNoMemo(1, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)
    for n in xrange(3, 20):
      expected = astar.TheoreticalLowerBoundKEquals2(n)
      actual = astar.TheoreticalLowerBoundNoMemo(2, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)
    for k, n in itertools.product(xrange(3, 20), repeat=2):
      expected = astar.TheoreticalLowerBoundWeak(k, n)
      actual = astar.TheoreticalLowerBoundNoMemo(k, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)

  def testMemoized(self):
    for k, n in itertools.product(xrange(1, 20), repeat=2):
      expected = astar.TheoreticalLowerBoundNoMemo(k, n)
      actual = astar.TheoreticalLowerBound(k, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)
    # Do the same thing twice to make sure it doesn't mess up the second time.
    for k, n in itertools.product(xrange(1, 20), repeat=2):
      expected = astar.TheoreticalLowerBoundNoMemo(k, n)
      actual = astar.TheoreticalLowerBound(k, n)
      assert expected == actual, '%s != %s (%s, %s)' % (actual, expected, k, n)


class PriorityQueueTest(unittest.TestCase):

  def testBasic(self):
    q_to = multiprocessing.Queue()
    q_from = multiprocessing.Queue(1)

    T1 = 'T1'
    T2 = 'T2'

    pq = astar_multi.PriorityQueue(input_queue=q_to, output_queue=q_from)
    pq.start()

    pq.put(T1)
    assert pq.get() == T1

    pq.put(T1)
    pq.put(T2)
    assert pq.get() == T1
    assert pq.get() == T2

    pq.close()
    pq.join()
