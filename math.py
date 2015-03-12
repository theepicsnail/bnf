from lang import Rule, Matcher
from token import NUMBER

@Rule("<Term> (('+' | '-') <Term>)*")
class Equation:
  def __init__(self, term, tail):
    self.term = term
    self.tail = tail

  def evaluate(self, scope):
    val = self.term.evaluate(scope)
    for op, term in self.tail:
      op = op[0].string
      if op == '+':
        val += term.evaluate(scope)
      elif op == '-':
        val -= term.evaluate(scope)
    return val

@Rule("<Factor> (('*' | '/') <Factor>)*")
class Term:
  def __init__(self, factor, tail):
    self.factor = factor
    self.tail = tail

  def evaluate(self, scope):
    val = self.factor.evaluate(scope)
    for op, term in self.tail:
      op = op[0].string
      if op == '*':
        val *= term.evaluate(scope)
      elif op == '/':
        val /= term.evaluate(scope)
    return val

@Rule("{NUMBER} | {NAME}")
class Factor:
  def __init__(self, val):
    self.val = val

  def evaluate(self, scope):
    if self.val.type == NUMBER:
      return float(self.val.string)
    else:
      return scope.get(self.val.string, 0)


equationMatcher = Matcher("Equation")
examples = ["0", "1+1", "2+3*4", "2*3+4", "1+", "1*", "", "x", "x+1", "y*7+x", "z"]
scope = {"x": 3, "y":10}
for equ in examples:
  print("")
  print(">>",equ)
  try:
    equ_object = equationMatcher.matchString(equ)
    result = equ_object.evaluate(scope)
    print("<<", result)
  except:
    print("<<", "Failed to parse")
