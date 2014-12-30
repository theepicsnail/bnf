from  api import *

name = "math2"

tokens = Parser.FILE("math")
matcher = EXACTLY(Bnf)
#matcher = Bnf.matcher()
matcher(tokens).dump(name)



