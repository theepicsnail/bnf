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


# List of math expressions to input into our evaluator.
# ( expression (str), result (float or None))
# result is None if the expression shouldn't parse.
scope = {
    "x": 3,
    "y":10}
tests = [
    ("0", 0),
    ("1+1", 2),
    ("2+3*4", 14),
    ("2*3+4", 10),
    ("1+", None),
    ("1*", None),
    ("", None),
    ("x", 3),
    ("x+1", 4),
    ("y*7+x", 73),
    ("z", 0),
    ("z+x", 3)
]

equationMatcher = Matcher("Equation")

for (equation, answer) in tests:
  try:
    ans = equationMatcher.matchString(equation).evaluate(scope)
    assert ans == answer, "Equation {} evaluated to {}. But {} was expected".format(equation, ans, answer)
  except:
    assert answer is None, "Equation {} didn't parse. It should have evaluated to {}".format(equation, answer)

print("All tests passed.")
