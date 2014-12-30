from grammar import ParseNode, Parser
from grammar import MANY, ANY, EXACTLY, OPTIONAL, ZERO_OR_MORE
from token import NUMBER, NAME, NEWLINE, INDENT, DEDENT, STRING
import impl

class Bnf(ParseNode):
  IMPL = impl.Bnf
  @staticmethod
  def matcher():
    return MANY(NonterminalRule)

class NonterminalRule(ParseNode):
  IMPL = impl.NonterminalRule
  @staticmethod
  def matcher():
    return (NAME, ":", NEWLINE, INDENT, MANY(Rule), DEDENT)

class Rule(ParseNode):
  IMPL = impl.Rule
  @staticmethod
  def matcher():
    return (MANY(Matcher), NEWLINE)

class Matcher(ParseNode):
  IMPL = impl.Matcher
  @staticmethod
  def matcher():
    return (Items, ZERO_OR_MORE(("|", Items)))

class Items(ParseNode):
  IMPL = impl.Items
  @staticmethod
  def matcher():
    return MANY(ANY(NAME, STRING, Group))

class Group(ParseNode):
  IMPL = impl.Group
  @staticmethod
  def matcher():
    return ("(", Matcher, ")", OPTIONAL(ANY("?", "+", "*")))
