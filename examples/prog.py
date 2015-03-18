from lang import Rule, Matcher
from token import NUMBER
from collections import defaultdict
from lang import Debug
import lang
# Default constructor for simple nodes.
class MatchBase:
    def __init__(self, *match):
        self.match = match

@Rule("<Function>+")
class File:
    def __init__(self, funcs):
        self.funcs = funcs
    @Debug
    def compile(self):
        nonMains = []
        main = None
        for func in self.funcs:
            if func.name == "main":
                main = func
            else:
                nonMains.append(func)
        assert main is not None, "No 'main' function defined"
        partialCompiles = []
        linkMap = {}

        obj, links = main.compile()
        partialCompiles.append((obj,links))
        linkMap["main"] = 0

        offset = len(obj)
        for func in nonMains:
            obj, links = func.compile()
            partialCompiles.append((obj, links))
            linkMap[func.name] = offset
            offset += len(obj)
        # Now do the linking and the building
        out = []
        for obj, links in partialCompiles:
            #print("Linking:")
            #print(obj)
            #print(links)
            #print("With", linkMap)
            for name, spots in links.items():
                offset = linkMap[name]
                for s in spots:
                    obj[s] = offset
            out.extend(obj)
        return out

#      0      1      2   3          4  5
@Rule("'func' {NAME} '(' <Arglist> ')' <BlockStatement>")
class Function(MatchBase):
    def __init__(self, _, name, _2, args, _3, statement):
        self.name = name.string
        self.args = args
        self.body = statement
    @Debug
    def compile(self):
        # Return an array of bytes and a map of name to spots in the array to
        # write function offsets.
        # [ 1, 2, 0, 4, 0], {"foo", [2,4]}  would replace the 0's with wherever 'foo' ends up
        #print("Compiling", self.name)
        out = []
        offset = 0
        for name in self.args.names:
            out.extend(["pop", name]) # fill in our args.
            offset += 2

        obj, links = self.body.compile(offset)
        out.extend(obj)
        ##print(out, links)
        return out, links



# Matches a list of names. obj.names contains the names as a list!
@Rule("({NAME} (',' {NAME})*)?")
class Arglist:
    def __init__(self, args):
        self.names = []
        if args is None:
            return
        self.names.append(args[0].string)
        for _, name in args[1]:
            self.names.append(name.string)

# Multiplexer of sorts. Whichever node matches this, is the node that
# is returned when a 'Statement' is constructed.
@Rule("<ReturnStatement> | <IfStatement> | <LetStatement> | <BlockStatement>")
class Statement:
    def __new__(self, statement):
        return statement

@Rule("'return' <Expression>")
class ReturnStatement:
    def __init__(self, _, expr):
        self.expr = expr
    @Debug
    def compile(self, offset):
        obj, links = self.expr.compile(offset)
        obj.extend(["ret"])
        return obj, links

@Rule("'if' '(' <Expression> ')' <Statement>")
class IfStatement:
    def __init__(self, _, _2, expr, _3, stmt):
        self.expr = expr
        self.statement = stmt
    @Debug
    def compile(self, offset): #2
        exprObj, exprLinks = self.expr.compile(offset)
        exprObj.extend(["ifFalse", "jumpRel", 0])
        offset += len(exprObj)
        stmtObj, stmtLinks = self.statement.compile(offset)
        #Add statment links to exprLinks
        for k,v in stmtLinks.items():
            exprLinks[k].extend(v)
        exprObj[-1] =  len(stmtObj)
        exprObj += stmtObj
        return exprObj, exprLinks

@Rule(" '{' <Statement>* '}' ")
class BlockStatement:
    def __init__(self, _, statements, _2):
        self.statements = statements
    @Debug
    def compile(self, offset):
        out = []
        links = defaultdict(list)
        for stmt in self.statements:
            obj, l = stmt.compile(offset)
            offset += len(obj)
            out.extend(obj)
            for k,v in l.items():
                links[k].extend(v)
        return out, links

@Rule(" 'let' {NAME} '=' <Expression>")
class LetStatement:
    def __init__(self, _, name, _2, expr):
        self.name = name.string
        self.expr = expr

    @Debug
    def compile(self, offset):
        out,links = self.expr.compile(offset)
        out.extend(("pop", self.name))
        return out, links

#Hacky just for this example.
@Rule("'x' ('<' '2' | '-' ('1'|'2'))? |"
      "'y' '+' 'z' |"
      "'fib' '(' <Expression> ')' |"
      "'4'")
class Expression:
    def __init__(self, *args):
        def fix(x):
            if type(x) in [tuple, list]:
                return [fix(y) for y in x ]
            try:
                return x.string
            except:
                return x
        self.match = fix(args)
    @Debug
    def compile(self, offset):
        #print("Compiling expr:", self.match, offset)
        links = defaultdict(list)
        out = []
        if self.match[0] == 'x':
            op = self.match[1]
            out.extend(["push", "x"])
            if op is not None: # if there's an op after x, build that.
                if type(op[1]) == list: # ('1' | '2') get the value.
                    op[1] = op[1][0]
                out.extend(["push", op[1], op[0]])
        elif self.match[0] == 'y':
            out.extend(["push", "y", "push", "z", "+"])
        elif self.match[0] == '4':
            out.extend(["push", "4"])
        else: # fib ( expr )
            obj, links = self.match[2].compile(offset)
            out.extend(obj)
            out.extend(["push", "PC", "jumpAbs", "<link to fib>"])

            ref = len(out) + offset -1
            #print(ref, len(out), offset)
            links["fib"].append(ref)
        return out, links

matcher = Matcher("File")
res = matcher.matchString("""
func fib(x) {
    if(x < 2)
        return x
    let y = fib(x-1)
    let z = fib(x-2)
    return y+z
}

func main () {
    return fib(4)
}
""")
#print("Result:", res)
lang.DEBUG = False
binary = res.compile()

#for offset, val in enumerate(binary):
#    print(offset, val)


class Computer:
    def __init__(self, program):
        self.PC = 0
        self.Stack = []
        self.Map = {}
        self.program = program

    def next(self):
        assert self.PC >=0 and self.PC < len(self.program), "PC went out of bounds"
        op = self.program[self.PC]
        self.PC += 1
        return op

    def run(self):
        for steps in range(100):
            op = self.next()
            print(self.PC -1, op)

Computer(binary).run()


