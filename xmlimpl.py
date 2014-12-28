from grammar import Node
class Bnf(Node):
  def dump(self, depth=0):
    print(" "*depth, "<bnf>")
    for rule in self.match:
      rule.dump(depth+1)
    print(" "*depth, "</bnf>")

class NonterminalRule(Node):
  def dump(self, depth=0):
    print(" "*depth, "<ntrule>")
    print(" "*(depth+1), "<name>{}</name>".format(
      self.match[0].string))
    for matcher in self.match[4]:
      matcher.dump(depth+1)
    print(" "*depth, "</ntrule>")

class Rule(Node):
  def dump(self, depth=0):
    print(" "*depth, "<rules>")
    for instr in self.match[0]:
      instr.dump(depth+1)
    print(" "*depth, "</rules>")

class Matcher(Node):
  def dump(self, depth=0):
    print(" "*depth, "<rule>")

    if self.match[1]:
      print(" "*depth, "<option>")

    self.match[0].dump(depth+1)

    for tail in self.match[1]:
      print(" "*(depth), "</option><option>")
      tail[1].dump(depth+1)
    if self.match[1]:
      print(" "*(depth), "</option>")
    print(" "*depth, "</rule>")

class Items(Node):
  def dump(self, depth=0):
    for item in self.match:
      if type(item) == Group:
        item.dump(depth+1)
      elif item.type == 3:
        print(" "*depth, "<string>{}</string>".format(
          item.string))
      elif item.type == 1:
        print(" "*depth, "<name>{}</name>".format(
          item.string))
      else:
        print(item)

class Group(Node):
  def dump(self, depth=0):
    mod = self.match[3]
    if mod:
      modstr = " mod=" + mod.string
    else:
      modstr = ""
    print(" "*depth, "<group{}>".format(modstr))
    self.match[1].dump(depth+1)
    print(" "*depth, "</group>")
