import traceback
DEBUG = True
def Debug(func):
  if not DEBUG:
    return func
  def debugger(*a, **b):
    depth = len(traceback.extract_stack()) // 2
    indent = "| " * depth
    try:
      print(indent, ">>", func )
      for i,n in enumerate(a):
        print(indent, "arg", i, "=", n)
      for k,n in b.items():
        print(indent, "arg", k, "=", n)
      val = func(*a, **b)
      print(indent, "<<", val)
      return val
    except BaseException as e:
      print(indent, "XX", e)
      raise
  return debugger


@Debug
def fib(n):
    if n < 2:
        return n
    return fib(n -1) + fib(n-2)

print(fib(4))


Output = """
|  >> <function fib at 0x7fab7a07b378>
|  arg 0 = 4
| |  >> <function fib at 0x7fab7a07b378>
| |  arg 0 = 3
| | |  >> <function fib at 0x7fab7a07b378>
| | |  arg 0 = 2
| | | |  >> <function fib at 0x7fab7a07b378>
| | | |  arg 0 = 1
| | | |  << 1
| | | |  >> <function fib at 0x7fab7a07b378>
| | | |  arg 0 = 0
| | | |  << 0
| | |  << 1
| | |  >> <function fib at 0x7fab7a07b378>
| | |  arg 0 = 1
| | |  << 1
| |  << 2
| |  >> <function fib at 0x7fab7a07b378>
| |  arg 0 = 2
| | |  >> <function fib at 0x7fab7a07b378>
| | |  arg 0 = 1
| | |  << 1
| | |  >> <function fib at 0x7fab7a07b378>
| | |  arg 0 = 0
| | |  << 0
| |  << 1
|  << 3
3
"""
