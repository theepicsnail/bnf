class Node:
  def __init__(self, match):
    self.match = match

class Bnf(Node):
  def dump(self, name):
    api = open(name + "_api.py", "w")
    impl = open(name + "_impl.py", "w")

    print("from grammar import ParseNode, Parser", file=api)
    print("from grammar import MANY, ANY, EXACTLY, OPTIONAL, ZERO_OR_MORE", file=api)
    print("from token import NUMBER, NAME, NEWLINE, INDENT, DEDENT, STRING", file=api)
    print("import {}_impl as impl".format(name), file=api)

    print("""
class Node:
  def __init__(self, match):
    self.match = match
""", file=impl)

    for rule in self.match:
      rule.dump(api, impl)

class NonterminalRule(Node):
  def dump(self, api, impl):
    name = self.match[0].string
    rules = self.match[4]

    if len(rules) == 1:
      matcher = rules[0].dump()
    else:
      matchers = [rule.dump() for rule in rules]
      matcher = "ANY(" + ",".join(matchers) + ")"

    print("""
class {NAME}(ParseNode):
  IMPL = impl.{NAME}
  @staticmethod
  def matcher():
    return {MATCHER}""".format(NAME=name, MATCHER=matcher), file=api)

    print("""
class {NAME}(Node):
  pass""".format(NAME=name), file=impl)

class Rule(Node):
  def dump(self):
    return "{}".format(
      ",".join(
        [instr.dump() for instr in self.match[0]]
      ))

class Matcher(Node):
  def dump(self):
    head = self.match[0].dump()

    tail = [items[1].dump() for items in self.match[1]]

    if tail:
      return "ANY({}, {})".format(head, ", ".join(tail))
    else:
      return head

class Items(Node):
  def dump(self):
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
  def dump(self):
    out = "{}"
    mod = self.match[3]
    if mod:
      out = {
        "+":"MANY({})",
        "?":"OPTIONAL({})",
        "*":"ZERO_OR_MORE({})"
      }[mod.string]

    return out.format(self.match[1].dump())
