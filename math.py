from lang import Rule, Matcher
from token import NUMBER

Grammer = """
assignment: [NAME '='] equation
equation: term (('+'|'-') term)*
term: factor (('*'|'/'|'%'|'//') factor)*
factor: atom ['^' factor]
atom: '(' equation ')' | NAME | NUMBER | '-' <atom>
"""


@Rule("({NAME} '=')? <Equation>")
class Assignment:
  def __init__(self, name, equation):
    self.equation = equation
    if name is not None:
      self.name = name[0].string
    else:
      self.name = None

  def evaluate(self, scope):
    val = self.equation.evaluate(scope)
    if self.name is not None:
      scope[self.name] = val
    return val

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


@Rule("<Atom> ( '^' <Factor> )?")
class Factor:
  def __init__(self, atom, tail):
    self.atom = atom
    self.tail = tail
  def evaluate(self, scope):
    val = self.atom.evaluate(scope) 
    if self.tail is not None:
      val **= self.tail[1].evaluate(scope)

    return val

@Rule(" '(' <Equation> ')' | {NAME} | {NUMBER} | '-' <Atom>")
class Atom:
  def __init__(self, a, b=None, c=None):
    #This is too complicated, it beeds broken apart.
    if a.string == '(': # ( Equation )
      self.evaluate = b.evaluate
    elif a.string == '-':
      self.evaluate = lambda *args: -1 * b.evaluate(*args)
    else:
      self.val = a

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
    ("z+x", 3),
    ("x=10", 10),
    ("x", 10),
    ("x = 3^(2+4)", 729),
]

matcher = Matcher("Assignment")

for (equation, answer) in tests:
  try:
    ans = matcher.matchString(equation).evaluate(scope)
    assert ans == answer, "Equation {} evaluated to {}. But {} was expected".format(equation, ans, answer)
  except:
    if answer is not None:
      raise
    assert answer is None, "Equation {} didn't parse. It should have evaluated to {}".format(equation, answer)
print("All tests passed.")

print("type 'quit' to exit")
while True:
  line = input(">")
  if line in ['quit', 'exit', '']:
    break
  if line == "scope":
    print(scope)
  try:
    print("<", matcher.matchString(line).evaluate(scope))
  except:
    print("Failed to parse")


