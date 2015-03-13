import io
import tokenize, token


import traceback
DEBUG = False# True
def Debug(func):
  if not DEBUG:
    return func
  def debugger(*a, **b):
    depth = len(traceback.extract_stack()) // 2
    indent = "| " * depth
    try:
      print(indent, ">>", func )
      for i,n in enumerate(a):
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
    return t.type not in [
      tokenize.ENCODING,
      token.INDENT,
      token.DEDENT
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
    return self.cls(*self.matcher.match(lang, tokens))

  def __repr__(self):
    return "RuleMatcher({})".format(self.rule)

class MatcherBase:
  def __init__(self, expected):
    self.expected = expected
  @Debug
  def match(self, lang, tokenStream):
    assert False, "Unimplemented"
  def __repr__(self):
    return str(self.__class__.__name__) + "(" + repr(self.expected) + ")"

class MatchReference(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    ruleMatcher = lang[self.expected]
    return ruleMatcher.match(lang, tokenStream)

class MatchString(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    tok = tokenStream.expectString(self.expected)
    if tok == None:
      tokenStream.unget()
      raise MatchFail("Expected '{}' but got {}".format(self.expected, tok))
    return tok

class MatchType(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
      tok = tokenStream.get()
      if token.tok_name[tok.type] != self.expected:
        tokenStream.unget()
        raise MatchFail("Expected '{}' but got {}".format(self.expected, tok))
      return tok

class MatchOptional(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    state = tokenStream.getState()
    try:
      return self.expected.match(lang, tokenStream)
    except MatchFail:
      tokenStream.setState(state)
      return None

class MatchMany(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    first = self.expected.match(lang, tokenStream)
    rest = MatchList(self.expected).match(lang, tokenStream)
    return [first] + rest

class MatchList(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    out = []
    matcher = MatchOptional(self.expected)
    while True:
      val = matcher.match(lang, tokenStream)
      if val is None:
        break
      else:
        out.append(val)
    return out

class MatchAll(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    out = []
    for matcher in self.expected:
      out.append(matcher.match(lang, tokenStream))
    return out

class MatchFirst(MatcherBase):
  @Debug
  def match(self, lang, tokenStream):
    state = tokenStream.getState()
    try:
      for option in self.expected:
        res = option.match(lang,tokenStream)
        if res is not None:
          return res
        tokenStream.setState(state)
    except:
      raise MatchFail("Couldn't match any of:" + ", ".join(map(str,self.expected)))

class Matcher:
  def __init__(self, reference, lang=DEFAULT_LANGUAGE):
    self.matcher = MatchAll([
      MatchReference(reference),
      MatchType("ENDMARKER")])
    self.lang = lang
  def matchString(self, line):
    lineFactory = io.StringIO(line).readline
    tokens = TokenStream(lineFactory)
    return self.matcher.match(self.lang, tokens)[0]

  def matchFile(self, filename):
    lineFactory = open(filename).readline
    tokens = TokenStream(lineFactory)
    return self.matcher.match(self.lang, tokens)[0]
