from parser import Parser, ParseFail
from token import *
def FAIL(parser):
  raise ParseFail()

class Node(object):
  @staticmethod
  def matcher():
    raise Exception("No matched defined in subclass.")

  def __init__(self, match):
    self.match = match

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, self.match)

def dprint(*a):
#  import traceback
#  print("  " * len(traceback.extract_stack()), *a)
  pass

def EXACTLY(matcher):
  def match(parser):
    dprint("EXACTLY", matcher)

    if type(matcher) == str:
      tok = parser.get()
      dprint("tok", tok.string)
      if tok.string != matcher:
        raise ParseFail("Expected {} but got {}".format(matcher, tok.string))
      return tok

    if type(matcher) == int:
      tok = parser.get()
      dprint("tok", tok.type, tok.string.replace("\n","\\n"))
      if tok.type != matcher:
        raise ParseFail("Expected type {}({}) but got {}({})".format(
            tok_name[matcher],matcher,
            tok_name[tok.type], tok.type))
      return tok

    if type(matcher) == tuple:
      out = []
      for submatcher in matcher:
        match = EXACTLY(submatcher)(parser)
        out.append(match)
      out = tuple(out)
      return out

    if callable(matcher):
      if type(matcher) == type and issubclass(matcher, Node):
        res = EXACTLY(matcher.matcher())(parser)
        return matcher.IMPL(res) # return an instance of the Node class.
      else:
        ret = matcher(parser)
        return ret

    raise ParseFail("Invalid match type specified {}".format(matcher))
  return match

def OPTIONAL(subtree):
  """ returns the contents of the subtree or None """
  def match(parser):
    dprint("OPTIONAL", subtree)
    pos = parser.tokens.pos
    try:
      out = EXACTLY(subtree)(parser)
      return out
    except ParseFail:
      parser.tokens.pos = pos
    return None
  return match

def ANY(*subtrees):
  """ returns the contents of the first subtree that matches"""
  def match(parser):
    dprint("ANY", subtrees)
    for subtree in subtrees:
      res = OPTIONAL(subtree)(parser)
      if res:
        return res
    raise ParseFail("Didn't match any of: {}".format(subtrees))
  return match

def MANY(matcher):
  """ Returns a list of matches (at least 1) of the subtree """
  def match(parser):
    dprint("MANY", matcher)
    results = [EXACTLY(matcher)(parser)]
    while True:
      val = OPTIONAL(matcher)(parser)

      if val is None:
        return results

      results.append(val)
  return match

def ZERO_OR_MORE(matcher):
  def match(parser):
    dprint("ZERO_OR_MORE", matcher)
    results = []
    while True:
      val =  OPTIONAL(matcher)(parser)

      if val is None:
        return results

      results.append(val)
  return match





