package ksequences

import "testing"

func TestBasics(t *testing.T) {
  var s *Sequence = &Sequence{}
  if s.String() != "" {
    t.Errorf("\"\" != %s", s.String())
  }
  s = s.Append('a').Append('b').Append('c').Append('d').Append('e').Append('f')
  if s.String() != "abcdef" {
    t.Errorf("\"abcdef\" != %s", s.String())
  }
  s = s.Append('g').Append('h').Append('i').Append('j').Append('k').Append('l')
  if s.String() != "abcdefghijkl" {
    t.Errorf("\"abcdefghijkl\" != %s", s.String())
  }
  s = s.Head().Head().Head().Head().Head().Head().Head().Head().Head().Head()
  if s.String() != "ab" {
    t.Errorf("\"ab\" != %s", s.String())
  }
}
