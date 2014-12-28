#rom tokenize import TokenInfo
#okenInfo.__repr__ = lambda x:"{}{}".format(x.string.replace("\n","\\n"), x.type)
from grammar import Node, Parser
from grammar import MANY, ANY, EXACTLY
from token import NUMBER, NAME, NEWLINE, INDENT, DEDENT, STRING

import impl
class Bnf(Node):
  IMPL = impl.Bnf
  @staticmethod
  def matcher():
    return MANY(NonterminalRule)

class NonterminalRule(Node):
  IMPL = impl.NonterminalRule
  @staticmethod
  def matcher():
    return (NAME, ":", NEWLINE, INDENT,
        MANY(Rule), DEDENT)

class Rule(Node):
  IMPL = impl.Rule
  @staticmethod
  def matcher():
    return MANY(Matcher), NEWLINE

class Matcher(Node):
  IMPL = impl.Matcher
  @staticmethod
  def matcher():
    return ANY(NAME, Group, STRING)

class Group(Node):
  IMPL = impl.Group
  @staticmethod
  def matcher():
    return ("(", Matcher, ")", Optional("+"))


