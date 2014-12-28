from grammar import Node

class Bnf(Node):
  def dump(self, depth=0):
    print("from grammar import Node, Parser")
    print("from grammar import MANY, ANY, EXACTLY, OPTIONAL, ZERO_OR_MORE")
    print("from token import NUMBER, NAME, NEWLINE, INDENT, DEDENT, STRING")
    print("import impl")

    for rule in self.match:
      rule.dump(depth+1)

class NonterminalRule(Node):
  def dump(self, depth=0):
    name = self.match[0].string
    rules = self.match[4]

    if len(rules) == 1:
      matcher = rules[0].dump()
    else:
      matchers = [rule.dump() for rule in rules]
      matcher = "ANY(" + ",".join(matchers) + ")"

    print("""
class {NAME}(node):
  IMPL = impl.{NAME}
  @staticmethod
  def matcher():
    return {MATCHER}""".format(NAME=name, MATCHER=matcher))

class Rule(Node):
  def dump(self, depth=0):
    return "{}".format(
      ",".join(
        [instr.dump() for instr in self.match[0]]
      ))

class Matcher(Node):
  def dump(self, depth=0):

    head = self.match[0].dump()

    tail = [items[1].dump() for items in self.match[1]]

    if tail:
      return "ANY({},{})".format(head, ",".join(tail))
    else:
      return head

class Items(Node):
  def dump(self, depth=0):
    out = []
    for item in self.match:
      if type(item) == Group:
        out.append(item.dump())
      else:
        out.append(item.string)
    if len(out) > 1:
      return "(" + ", ".join(out) + ")"
    return out[0]

class Group(Node):
  def dump(self, depth=0):
    out = "{}"
    mod = self.match[3]
    if mod:
      out = {
        "+":"MANY({})",
        "?":"OPTIONAL({})",
        "*":"ZERO_OR_MORE({})"
      }[mod.string]

    return out.format(self.match[1].dump())
