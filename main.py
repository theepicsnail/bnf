from  api import *

tokens = Parser.FILE("test")
matcher = EXACTLY(Bnf)
#matcher = Bnf.matcher()
matcher(tokens).dump()



