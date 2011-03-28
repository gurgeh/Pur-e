"""
TODO Add uniqueness typing

Design:
 Modify recursive algorithm with
   class stuff
     a constructor is a function that returns a context (also called an object)
     a context can do symbol lookups
     you can possibly evaluate an expression in a context (see branching)
     many/most of the methods in a context returns a new context
     contexts can only be queried (and constructed) with static strings, not dynamically in runtime
     a context can be inherited with some bindings overridden
     
   conditions and constraints flowing back and forth
     Poss should merge possibilities in more general possibilities (but this is only an optimization, so maybe defer)
     when looping over possibilities, the conditions and constraints should be sent "down". Always down, except when explicitly returned together with possibilities. Either as a separate argument to the analyze functions or remembered by the external analyzer trampoline.
     impossible possibilities should be weeded to stop false errors and warnings (and optimize)
     The conds and constrs (do I need to have separate names?) should not really be stored with the data object, but communicated on a side channel in Poss.

   containers
     lists
       can be implemented as objects with standard iteration methods
       optimized later
       reminds me that I need generalizer for functions and contexts
     vectors
       a special data type. static, of course, but with obvious optimizations when unique
       does a vector store pointers and/or unboxed values? If it consists entirely of one
       unboxable data types, they are unboxed. If it consists of just one type of object
       or context it too will be unboxed and stored inline.
     maps (sets later)
       if contexts are accessible from code, they could be used as maps
       alternatively could be implemented on top of vectors and trees (lists),
       entirely in code. Yes! this is the right solution for now.

   lazy arguments? (other branches)
     could be implemented with macros + if
     otherwise, send context and raw expression to function (still needs if to branch)

   continuations?
     context and expressions are enough

   generators?
     not as such. for-interface of course.
     lazy thunks? Not now.

   exceptions? (non-local unwinding. More generally, co-routines)
     non-local unwinding seems powerful. The target of the unwind command may have to be determined
     statically. This can probably be added later, without much thought now.

   macros and other ways to communicate with analyzer are added later

   modules later

   syntax later

To implement this complex beast, I will use an analytical loop that calls functions that yields subexpressions, when it wants to analyze them and gets the result sent back. The generator functions can also yield other commands, such as the backwards analysis mentioned below.
This is also the easiest idea for an interpreter and a good way to get tail call optimization.


Recursion analytics algorithm:
  precalculate symbols used in each subtree
  in each branch (if), mark path taken with values for relevant context
  when reaching a marked branch that "contains" (i.e - is a generalization of) context:
    send other branch (if no other, signal error) back, mark stem with return value
    when reaching a marked stem, check if marking "contains" return value, if not:
      generalize marking and (this is the hard part, implementation wise)            
      send back generalized marking from origin where the ORIGINAL marking took place.
      repeat until stem is passed
  else:
    generalize context

Algorithm for context generalization: TOTHINK!
  bool
    exact -> unknown
  int
    exact -> bounds -> single bound -> unknown
  function
    
  context
    

"""


class Generalizer:
    def __init__(self):
        self.argmap = {}

    def has(self, args):
        if tuple(args) in self.argmap:
            return self.argmap[tuple(args)]
        self.argmap[tuple(args)] = None

    def get(self, args):
        return self.argmap[tuple(args)]

    def set(self, args, val):
        self.argmap[tuple(args)] = val
