"""
TODO:
 Modify recursive algorithm with
   class stuff
     a constructor is a function that returns a context (also called an object)
     a context can do symbol lookups
     you can possibly evaluate an expression in a context (see branching)
     many/most of the methods in a context returns a new context
     contexts can only be queried (and constructed) with static strings, not dynamically in runtime
     
     
   conditions and constraints flowing back and forth
     TOTHINK
     

   containers (TOTHINK)
     lists
     maps (sets later)
     vectors

   lazy arguments? (other branches)
     could be implemented with macros + if
     otherwise, send context and raw expression to function (still needs if to branch)

   continuations?
     context and expressions are enough

   generators?
     TOTHINK

   exceptions? (non-local unwinding. More generally, co-routines)
     non-local unwinding seems powerful. The target of the unwind command may have to be determined
     statically. This can probably be added later, without much thought now.
   


Recursion analytics algorithm:
  precalculate symbols used in each subtree
  in each branch (if), mark path taken with values for relevant context
  when reaching a marked branch that "contains" (i.e - is a generalization of) context:
    send other branch (if no other, signal error) back, mark stem with return value
    when reaching a marked stem, check if marking "contains" return value, if not:
      generalize marking and (this is the hard part, implementation wise)            
      send back generalized marking from origin where the ORIGINAL marking took place. <-- TODO!
      repeat until stem is passed
  else:
    generalize context

Algorithm for context generalization:
  TODO


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
