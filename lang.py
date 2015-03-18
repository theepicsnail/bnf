import io
import tokenize, token


import traceback
DEBUG = False
def Debug(func):
  def debugger(*a, **b):
    if not DEBUG:
      return func(*a, **b)
    depth = len(traceback.extract_stack()) // 2
    indent = "| " * depth
    try:
      print(indent, ">>", func )
      for i,n in enumerate(a):
        if type(n) == dict:
          n = n.keys()
        print(indent, "arg", i, "=", n)
      for k,n in b.items():
        print(indent, "arg", k, "=", n)
      val = func(*a, **b)
      print(indent, "<<", val, func)
      return val
    except BaseException as e:
      print(indent, "XX", e, func)
      raise
  return debugger

DEFAULT_LANGUAGE = {}
class MatchFail(BaseException):pass
class TokenStream:
  def __init__(self, readline):
    self.tokens = list(filter(self.acceptToken, tokenize.generate_tokens(readline)))
    self.pos = 0
  def acceptToken(self, t):
    if DEBUG:
      print("Accept token?", t)
    return t.type not in [
      tokenize.ENCODING,
      token.INDENT,
      token.DEDENT,
      tokenize.NL,
      tokenize.NEWLINE
    ]
  def get(self):
    self.pos += 1
    return self.tokens[self.pos-1]
  def unget(self):
    self.pos -= 1
  def peek(self):
    return self.tokens[self.pos]

  def getState(self):
    return self.pos
  def setState(self, state):
    self.pos = state

  def hasNext(self):
    return self.pos != len(self.tokens)

  def expectString(self, val):
    return self.expect(lambda t:t.string == val)
  def expectType(self, type):
    return self.expect(lambda t:t.type == type)
  def expect(self, validFunc):
    got = self.get()
    if validFunc(got):
      return got
    self.unget()
    return None

  def __repr__(self):
    return str(self.pos)+" "+ (", ".join(map(lambda t:repr(t.string), self.tokens)))


def Rule(rule, lang=DEFAULT_LANGUAGE):
  def Decorator(cls):
    assert(type(cls) == type) # catch using 'def' instead of 'class', also catches python2
    name = cls.__name__
    assert name not in lang, name + " already defined."
    #lang[name] = createMatcher(rule, cls)
    lang[name] = RuleMatcher(rule, cls)
    return cls
  return Decorator

#def createMatcher(rule, factory):
#  """ Given a rule, and a class, return a function
#  that takes in a token stream and outputs and instance
#  of that class if it matches
#
#  classes are instanciated with the match results"""
#  matcher = compileMatcher(rule)
#  def ruleMatcher(lang, tokenStream):
#    result = matcher.match(lang, tokenStream)
#    if result != None:
#      return factory(*result)
#    return None
#  return ruleMatcher
#
def compileMatcher(rule):
  """ Given a bnf spec, return a function that will match that
  the returned function should return a list of matched tokens """
  lineFactory = io.StringIO(rule).readline
  tokens = TokenStream(lineFactory)
  rule = compileRule(tokens)
  if tokens.expectType(token.ENDMARKER) is None:
    tokens.unget()
    print("Error unused tokens:")
    while tokens.hasNext():
      print(tokens.get())
    raise MatchFail("Failed to compile rule: " + str(rule))
  return rule

@Debug
def compileRule(tokens):
  """ Return a (rule, remaining tokens)"""
  options = []
  out = []
  while tokens.hasNext():
    t = tokens.get()
    if t.string == "<": # < NAME >    Reference another rule
      name = tokens.expectType(token.NAME)
      tokens.expectString(">")
      out.append(MatchReference(name.string))
    elif t.string == "{": # { NAME }    Match a token type
      group = tokens.expectType(token.NAME)
      tokens.expectString("}")
      out.append(MatchType(group.string))
    elif t.type == token.STRING:
      out.append(MatchString(eval(t.string)))
    elif t.string == "(":
      rule = compileRule(tokens)
      out.append(rule)
      tokens.expectString(")")
    elif t.string in ["+", "?", "*"]:
      assert len(out) >0, "Unexpected modifier"
      mod = {"?":MatchOptional, "+":MatchMany, "*":MatchList}
      out[-1]=mod[t.string](out[-1])
    elif t.string == '|':
      options.append(MatchOptional(MatchAll(out)))
      out = []
    else:
      tokens.unget()
      break

  options.append(MatchAll(out))
  return MatchFirst(options)




class RuleMatcher:
  def __init__(self, rule, cls):
    self.rule = rule
    self.matcher = compileMatcher(rule)
    self.cls = cls
  @Debug
  def match(self, lang, tokens):
    res = self.matcher.match(lang, tokens)
    if DEBUG:
      print("Rule matched:", self.cls, res)
    return self.cls(*res)

  def __repr__(self):
    return "RuleMatcher({})".format(self.rule)

  def compress(self, lang):
    self.matcher = self.matcher.compress(lang)
    return self

class MatcherBase:
  def __init__(self, expected):
    self.expected = expected
  @Debug
  def match(self, lang, tokenStream):
    assert False, "Unimplemented"
  def __repr__(self):
    return str(self.__class__.__name__) + "(" + repr(self.expected) + ")"

  @Debug
  def compress(self, lang):
    return self

class MatchReference(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    assert self.expected in lang, "{} was refereced but not defined.".format(self.expected)
    ruleMatcher = lang[self.expected]
    return ruleMatcher.match(lang, tokenStream)
  def __repr__(self):
    return "<{}>".format(self.expected)
  #Leaving as default so that stack traces keep references
  @Debug
  def compress(self, lang):
    lang[self.expected] = lang[self.expected].compress(lang)
    return self

class MatchString(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    tok = tokenStream.expectString(self.expected)
    if tok == None:
      raise MatchFail("Expected '{}' but got {}".format(self.expected, tokenStream.peek()))
    return tok
  def __repr__(self):
    return repr(self.expected)

class MatchType(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
      tok = tokenStream.get()
      if token.tok_name[tok.type] != self.expected:
        tokenStream.unget()
        raise MatchFail("Expected '{}' but got {}".format(self.expected, tok))
      return tok
  def __repr__(self):
      return "{{{}}}".format(self.expected)

class MatchOptional(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    state = tokenStream.getState()
    try:
      return self.expected.match(lang, tokenStream)
    except MatchFail:
      tokenStream.setState(state)
      return None
  @Debug
  def compress(self, lang):
    self.expected = self.expected.compress(lang)
    if type(self.expected) == MatchOptional:
        print("hm... optional(optional(...))")
    return self

class MatchMany(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    out = [self.expected.match(lang, tokenStream)]
    while True:
      state = tokenStream.getState()
      try:
        out.append(self.expected.match(lang, tokenStream))
      except MatchFail:
        tokenStream.setState(state)
        break
    return out

  @Debug
  def compress(self, lang):
    self.expected = self.expected.compress(lang)
    return self

class MatchList(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    out = []
    while True:
      state = tokenStream.getState()
      try:
        out.append(self.expected.match(lang, tokenStream))
      except MatchFail:
        tokenStream.setState(state)
        break
    return out

  @Debug
  def compress(self, lang):
    self.expected = self.expected.compress(lang)
    return self

class Lister:
  def __init__(self, matcher):
    self.matcher = matcher
  def match(self, lang, toks):
    return [self.matcher.match(lang,toks)]
  def compress(self, lang):
    return self

class MatchAll(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    out = []
    for matcher in self.expected:
      out.append(matcher.match(lang, tokenStream))
    return out

  @Debug
  def compress(self, lang):
    self.compress = lambda x:self
    if len(self.expected) == 1:
      return Lister(self.expected[0].compress(lang))
    self.expected = [
        matcher.compress(lang)
        for matcher in self.expected
        ]
    return self

class MatchFirst(MatcherBase):

  @Debug
  def compress(self, lang):
    if len(self.expected) == 1:
      return Lister(self.expected[0].compress(lang))
    self.expected = [
        matcher.compress(lang)
        for matcher in self.expected
        ]
    return self

  @Debug
  def match(self, lang, tokenStream):
    state = tokenStream.getState()
    try:
      for option in self.expected:
        res = option.match(lang,tokenStream)
        if res is not None:
          return res
        tokenStream.setState(state)
    except MatchFail:
      raise MatchFail("Couldn't match any of:" + ", ".join(map(str,self.expected)))

class Matcher:
  def __init__(self, reference, lang=DEFAULT_LANGUAGE):
    DEBUG = True
    self.matcher = MatchAll([
      MatchReference(reference),
      MatchType("ENDMARKER")])#.compress(lang)
    DEBUG = False
    self.lang = lang

  def matchString(self, line):
    lineFactory = io.StringIO(line).readline
    return self.matchReadline(lineFactory)

  def matchFile(self, filename):
    lineFactory = open(filename).readline
    return self.matchReadline(lineFactory)

  def matchReadline(self, readLine):
    tokens = TokenStream(readLine)
    try:
      return self.matcher.match(self.lang, tokens)[0]
    except MatchFail:
      print("Couldn't match:", tokens.peek())
      raise
