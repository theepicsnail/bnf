from grammar import ZERO_PLUS, ANY, EXACTLY
from parser import Parser

class Node:
  def __init__(self, match):
    self.match = match

class Input(Node):
  Pattern = lambda: (Expression, ZERO_PLUS((";", Expression)))

  def evaluate(self, scope):
    expr, expr_list = self.match

    ans = expr.evaluate(scope)
    for (_,expr) in expr_list:
      ans = expr.evaluate(scope)

    return ans

class Expression(Node):
  Pattern = lambda: (MultiExpr, ZERO_PLUS((ANY("+","-"), MultiExpr)))

  def evaluate(self, scope):
    multi, multi_list = self.match
    ans = multi.evaluate(scope)
    for (op, expr) in multi_list:
      tmp = expr.evaluate(scope)
      if op == "+":
        ans += tmp
      elif op == "-":
        ans -= tmp
      else:
        print(op)
    return ans

class MultiExpr(Node):
  Pattern = lambda: (Atom, ZERO_PLUS((ANY("*", "/"), Atom)))

  def evaluate(self, scope):
    atom, atom_list = self.match
    ans = atom.evaluate(scope)
    for (op, atom) in atom_list:
      tmp = atom.evaluate(scope)
      if op == "*":
        ans *= tmp
      elif op == "/":
        ans /= tmp
      else:
        print(op)
    return ans

class Atom(Node):
  Pattern = lambda: (ANY(
      Parser.NUMBER,
      ("(", Expression, ")")
  ))

  def evaluate(self, scope):
    if type(self.match) == str:
      return float(self.match)
    return self.match[1].evaluate(scope)

"""
Make this look like this:

# initial setup
parser = Parser(Input)
scope = {}

# main loop
input_string = "1+1"
tree = parser.parseString(input_string)
print(tree.evaluate(scope))
"""
input_string = "1+10*2;"
inputParser = Parser.STRING(input_string)
tree = EXACTLY(Input)(inputParser)

scope = {}
print("{}={}".format(input_string, tree.evaluate(scope)))
