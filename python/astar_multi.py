#!/usr/bin/env python2.6

"""Find a sequence of n elements that has the k-radius property."""

import heapq
import logging
import multiprocessing
import Queue
import sys
import threading

import astar



if True:
  Process = multiprocessing.Process
  JoinableQueue = multiprocessing.JoinableQueue
  GENERATORS = multiprocessing.cpu_count()
else:
  Process = threading.Thread
  JoinableQueue = Queue.Queue
  GENERATORS = 1


class _PriorityQueueCloseMarker(object):
  pass


class HeapPriorityQueue(object):

  def __init__(self, *args, **kwargs):
    self._input_queue = kwargs.pop('input_queue')
    self._output_queue = kwargs.pop('output_queue')
    self._heap = []
    self._condition = threading.Condition()
    self._closed = threading.Event()
    self._process = Process(target=self.run)
    self._consumer = None
    self._producer = None

  def put(self, item, block=True, timeout=None):
    logging.debug('Putting an item in the queue.')
    self._input_queue.put(item, block, timeout)
    logging.debug('Put an item in the queue.')

  def get(self, block=True, timeout=None):
    logging.debug('Getting an item from the queue.')
    item = self._output_queue.get(block, timeout)
    logging.debug('Got an item from the queue.')
    return item

  def _Producer(self):
    logging.debug('_Producer started.')
    while not self._closed.is_set():
      with self._condition:
        if not self._heap:
          self._condition.wait()
          continue
        item = heapq.heappop(self._heap)
      self._output_queue.put(item)
      self._output_queue.join()
    logging.debug('_Producer quit.')

  def _Consumer(self):
    logging.debug('_Consumer started.')
    while not self._closed.is_set():
      try:
        item = self._input_queue.get(timeout=1)
      except Queue.Empty:
        continue
      try:
        if isinstance(item, _PriorityQueueCloseMarker):
          self._closed.set()
          with self._condition:
            self._condition.notify_all()
        else:
          with self._condition:
            heapq.heappush(self._heap, item)
            self._condition.notify()
      finally:
        self._input_queue.task_done()
    logging.debug('_Consumer quit.')

  def close(self):
    self._input_queue.put(_PriorityQueueCloseMarker())
    self.join_input()
    if not self.empty():
      self.get()
      self.task_done()

  def join(self):
    self._process.join()

  def join_input(self):
    self._input_queue.join()

  def start(self):
    self._process.start()

  def task_done(self):
    self._output_queue.task_done()

  def run(self):
    self._consumer = threading.Thread(target=self._Consumer)
    self._producer = threading.Thread(target=self._Producer)
    self._consumer.start()
    self._producer.start()
    self._consumer.join()
    self._producer.join()

  def empty(self):
    if self._output_queue.empty() and self._input_queue.empty():
      with self._condition:
        return not self._heap
    return False


class PQPriorityQueue(object):

  def __init__(self, *args, **kwargs):
    self._input_queue = kwargs.pop('input_queue')
    self._output_queue = kwargs.pop('output_queue')
    self._pq = Queue.PriorityQueue()
    self._condition = threading.Condition()
    self._closed = threading.Event()
    self._process = Process(target=self.run)
    self._consumer = None
    self._producer = None

  def put(self, item, block=True, timeout=None):
    logging.debug('Putting an item in the queue.')
    self._input_queue.put(item, block, timeout)
    logging.debug('Put an item in the queue.')

  def get(self, block=True, timeout=None):
    logging.debug('Getting an item from the queue.')
    item = self._output_queue.get(block, timeout)
    logging.debug('Got an item from the queue.')
    return item

  def _Producer(self):
    logging.debug('_Producer started.')
    while not self._closed.is_set():
      with self._condition:
        try:
          item = self._pq.get(block=False)
        except Queue.Empty:
          self._condition.wait()
          continue
      self._output_queue.put(item)
      self._output_queue.join()
    logging.debug('_Producer quit.')

  def _Consumer(self):
    logging.debug('_Consumer started.')
    while not self._closed.is_set():
      try:
        item = self._input_queue.get(timeout=1)
      except Queue.Empty:
        continue
      try:
        if isinstance(item, _PriorityQueueCloseMarker):
          self._closed.set()
          with self._condition:
            self._condition.notify_all()
        else:
          with self._condition:
            self._pq.put(item)
            self._condition.notify()
      finally:
        self._input_queue.task_done()
    logging.debug('_Consumer quit.')

  def close(self):
    logging.debug('Closing the PriorityQueue.')
    self._input_queue.put(_PriorityQueueCloseMarker())
    self.join_input()
    if not self.empty():
      self.get()
      self.task_done()

  def join(self):
    self._process.join()

  def join_input(self):
    self._input_queue.join()

  def start(self):
    self._process.start()

  def task_done(self):
    self._output_queue.task_done()

  def run(self):
    self._consumer = threading.Thread(target=self._Consumer)
    self._producer = threading.Thread(target=self._Producer)
    self._consumer.start()
    self._producer.start()
    self._consumer.join()
    self._producer.join()

  #TODO(jwg): This doesn't actually work, since _pq.empty is only valid in the PriorityQueue process.
  def empty(self):
    if self._output_queue.empty() and self._input_queue.empty():
      with self._condition:
        return self._pq.empty()
    return False


class _DoneMarker(object):
  pass


PriorityQueue = PQPriorityQueue


def AstarHelperNextNodeGenerator(input_queue, output_queue,
                                 next_nodes, score, done):
  while True:
    node = input_queue.get()
    try:
      if isinstance(node, _DoneMarker):
        return
      for i in next_nodes(node):
        not_done = 0 if done(i) else 1
        output_queue.put((score(i), not_done, i))
    finally:
      input_queue.task_done()


def Astar(initial_node, next_nodes, score, done):
  priority_queue = PriorityQueue(
      input_queue=JoinableQueue(GENERATORS * 2),
      output_queue=JoinableQueue(1),
  )
  generators_queue = JoinableQueue(GENERATORS * 2)
  generators = []
  for i in xrange(GENERATORS):
    generators.append(Process(
        target=AstarHelperNextNodeGenerator,
        name='Next Node Generator %d' % i,
        args=(generators_queue, priority_queue, next_nodes, score, done),
    ))
  for i in generators:
    i.start()
  priority_queue.start()

  def Barrier():
    generators_queue.join()
    priority_queue.join_input()
    if not priority_queue.empty():
      priority_queue.put(priority_queue.get())
      priority_queue.join_input()
      priority_queue.task_done()

  best = None
  best_score = None
  generators_queue.put(initial_node)

  barrier_called = False
  while True:
    score, not_done, node = priority_queue.get()
    priority_queue.task_done()
    if barrier_called and score >= best_score:
      break
    barrier_called = False
    if not_done:
      generators_queue.put(node)
    else:
      if not best or score < best_score:
        best = node
        best_score = score
        Barrier()
        barrier_called = True
  logging.debug('Loop exited. Shutting down.')
  for _ in generators:
    generators_queue.put(_DoneMarker())
  priority_queue.close()
  for gen in generators:
    gen.join()
  priority_queue.join()
  return best


def main(argv):
  #logging.basicConfig(filename='/dev/stderr', level=logging.DEBUG)
  assert len(argv) == 3
  radius = int(argv[1])
  alphabet_size = int(argv[2])
  initial_node = astar.ScoredSequence(k=radius, n=alphabet_size)
  next_nodes = lambda node: astar.GenerateNextNodes(node, alphabet_size)
  score = lambda node: astar.ScoreNode(node, radius, alphabet_size)
  result = Astar(initial_node, next_nodes, score, astar.Done)
  print 'radius: %d' % radius
  print 'alphabet size: %d' % alphabet_size
  print 'length: %d' % len(result)
  print 'result:'
  print result


if __name__ == '__main__':
  main(sys.argv)
