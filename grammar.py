from parser import Parser, ParseFail
from token import tok_name
class ParseNode:
  pass

def EXACTLY(matcher):
  def match(parser):

    if type(matcher) == str:
      tok = parser.get()

      if tok.string != matcher:
        raise ParseFail("Expected {} but got {}"
            .format(matcher, tok.string))
      return tok.string

    if type(matcher) == int:
      tok = parser.get()

      if tok.type != matcher:
        raise ParseFail("Expected type {}({}) but got {}({})"
            .format(tok_name[matcher],matcher,
                tok_name[tok.type], tok.type))
      return tok.string

    if type(matcher) == tuple:
      out = []
      for submatcher in matcher:
        match = EXACTLY(submatcher)(parser)
        out.append(match)
      out = tuple(out)
      return out

    if callable(matcher):
      if hasattr(matcher, "Pattern"):
        res = EXACTLY(matcher.Pattern())(parser)
        return matcher(res)
      elif type(matcher) == type and issubclass(matcher, ParseNode):
        res = EXACTLY(matcher.matcher())(parser)
        # TODO Delete this code. Use the pattern method
        return matcher.IMPL(res)
      else:
        ret = matcher(parser)
        return ret

    raise ParseFail("Invalid match type specified {}"
        .format(matcher))
  return match

def OPTIONAL(subtree):
  """ returns the contents of the subtree or None """
  def match(parser):

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

    for subtree in subtrees:
      res = OPTIONAL(subtree)(parser)
      if res:
        return res
    raise ParseFail("Didn't match any of: {}".format(subtrees))
  return match

def MANY(matcher):
  """ Returns a list of matches (at least 1) of the subtree """
  def match(parser):

    results = [EXACTLY(matcher)(parser)]
    while True:
      val = OPTIONAL(matcher)(parser)

      if val is None:
        return results

      results.append(val)
  return match

def ZERO_OR_MORE(matcher):
  def match(parser):

    results = []
    while True:
      val =  OPTIONAL(matcher)(parser)

      if val is None:
        return results

      results.append(val)
  return match

# Aliases
ONE_PLUS = MANY
ZERO_PLUS = ZERO_OR_MORE
OPTIONAL = OPTIONAL
FIRST = ANY
