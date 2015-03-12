from lang import Rule, Matcher

@Rule("<Term> (('+' | '-') <Term>)*")
class Equation:
  def __init__(self, term, tail):
    self.term = term
    self.tail = tail

  def evaluate(self):
    val = self.term.evaluate()
    for op, term in self.tail:
      op = op[0].string
      if op == '+':
        val += term.evaluate()
      elif op == '-':
        val -= term.evaluate()
    return val

@Rule("<Factor> (('*' | '/') <Factor>)*")
class Term:
  def __init__(self, factor, tail):
    self.factor = factor
    self.tail = tail

  def evaluate(self):
    val = self.factor.evaluate()
    for op, term in self.tail:
      op = op[0].string
      if op == '*':
        val *= term.evaluate()
      elif op == '/':
        val /= term.evaluate()
    return val

@Rule("{NUMBER}")
class Factor:
  def __init__(self, num):
    self.num = num

  def evaluate(self):
    return float(self.num.string)


equationMatcher = Matcher("Equation")
examples = ["0", "1+1", "2+3*4", "2*3+4", "1+", "1*", ""]
for equ in examples:
  print("")
  print(">>",equ)
  try:
    equ_object = equationMatcher.matchString(equ)
    result = equ_object.evaluate()
    print("<<", result)
  except:
    print("<<", "Failed to parse")
