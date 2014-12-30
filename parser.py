import tokenize
import token
import functools

class TokenList:
  """ Manage the list of tokens and moving forward/backward through them"""

  @staticmethod
  def FILE(filename):
    return TokenList(open(filename).readline)

  @staticmethod
  def STRING(string):
    return TokenList([b"", string].pop)

  def __init__(self, readline):
    self.tokens = list(tokenize.generate_tokens(readline))
#    for tok in self.tokens:
#      print("[{} {}]".format(
#        tok.type,
#        tok.string.replace("\n","")), end="\t")
#    print()
    self.pos = 0
    self.max_pos = len(self.tokens)

  def get(self):
    assert(self.pos < self.max_pos)
    ret = self.tokens[self.pos]
    self.pos += 1
    return ret

  def unget(self):
    self.pos -= 1
    assert(self.pos >= 0)

class ParseFail(BaseException):
  def __init__(self, *a):
    super().__init__(*a)

class Parser:
  """ Provide convenient matching logic, and exception handling for parsing"""
  NUMBER = token.NUMBER
  NAME = token.NAME

  @staticmethod
  def FILE(filename):
    return Parser(TokenList.FILE(filename))

  @staticmethod
  def STRING(string):
    return Parser(TokenList.STRING(string))

  def __init__(self, tokens):
    self.tokens = tokens

  def get(self):
    return self.tokens.get()

  def zeroOrMore(self, tree):
    results = []
    while True:
      val = self.optional(tree)

      if val is None:
        return results

      results.append(val)

  def anyof(self, *trees):
    """ Try each of the passed in trees, return the first that matched."""
    for tree in trees:
      val = self.optional(tree)
      if val:
        return val
    raise ParseFail()

  def optional(self, tree):
    """ Try to match a tree, if it fails, return None.
    This method doesn't raise a ParseFail if it fails.
    """
    pos = self.tokens.pos
    ret = None
    try:
      ret = tree.parse(self)
    except ParseFail:
      self.tokens.pos = pos

    return ret

  def expect(self, tree):
    return tree.parse(self)


