package ksequences

import "bytes"

// import "gilk.net/graph"

type Sequence struct {
  head *Sequence
  tail byte  // Maybe should be a rune?
}

func (self *Sequence) callForElements(f func(byte)) {
  if self.head != nil {
    self.head.callForElements(f)
  }
  if self.tail != 0 {
    f(self.tail)
  }
}

func (self *Sequence) String() string {
  var buf bytes.Buffer
  writeByte := func(b byte) {
    buf.WriteByte(b)
  }
  self.callForElements(writeByte)
  return buf.String()
}

func (self *Sequence) Append(b byte) *Sequence {
  head := self
  if self.tail == 0 {
    head = nil
  }
  return &Sequence{head, b}
}

func (self *Sequence) Head() *Sequence {
  return self.head
}
