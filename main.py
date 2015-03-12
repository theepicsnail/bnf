from lang import Rule, Matcher

json = {}

@Rule("{STRING} ':' {STRING}", json)
class KeyValuePair:
    def __init__(self, key, _, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "({}, {})".format(self.key.string, self.value.string)

@Rule("'{' (<KeyValuePair> (',' <KeyValuePair>)* )? '}'", json)
class Object:
  def __init__(self, _, body, _2):
    self.body = body

  def __str__(self):
    out = ""
    if self.body is not None:
        head, tail = self.body
        out += str(head)
        for _, kv in tail:
            out += ", " + str(kv)
    return out

jsonObject = Matcher("Object", json)

print("1:",jsonObject.matchString("{}"))
print("2:",jsonObject.matchString("{'a': 'b'}"))
print("3:",jsonObject.matchString("{'a': 'b', 'c':'d'}"))

# Output:
# """
# 1:
# 2: ('a', 'b')
# 3: ('a', 'b'), ('c', 'd')
# """
