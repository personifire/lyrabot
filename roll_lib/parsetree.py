import random

def total(lst):
    total = 0
    for val in lst:
        total += val
    return total

def int_or_eval(die):
    if isinstance(die, Integer):
        return die.value
    else:
        return die.roll()

class Roll():
    def __init__(self, left, oper, right):
        self.left  = left
        self.oper  = Operator(oper)
        self.right = right

    def roll(self):
        lval = int_or_eval(self.left)
        rval = int_or_eval(self.right)
        return self.oper(lval, rval)

    def evaluate(self):
        return total(self.roll())

class RollTerminal(Roll):
    def __init__(self, dice, faces, actionseq = None):
        self.dice      = dice
        self.faces     = faces
        self.actionseq = actionseq

    def roll(self):
        dice = int_or_eval(self.dice)

        if dice < 0:
            rolls = [-self.faces.evaluate() for roll in range(-dice)]
        elif dice == 0:
            rolls = [0]
        else:
            rolls = [self.faces.evaluate() for roll in range(dice)]
        rolls.sort()

        if self.actionseq:
            rolls = self.actionseq(rolls)
        return rolls

    def evaluate(self):
        return total(self.roll())

class Operator():
    def __init__(self, operator):
        if operator == "+":
            self.call = lambda a, b: sorted(a + b)
        else: # operator == "-":
            self.call = lambda a, b: sorted(a + list(map(lambda x: -x, b)))

    def __call__(self, lval, rval):
        value = self.call(lval, rval)
        return self.call(lval, rval)

class Integer():
    def __init__(self, number, operator = None):
        try:
            value = int(number, 0)
        except Exception as e:
            value = 0
            raise e

        if operator == "-":
            value = -value

        self.value = value

    def roll(self):
        if self.value < 0:
            return [random.randint(self.value, -1)]
        elif self.value == 0:
            return [0]
        else:
            return [random.randint(1, self.value)]

    def evaluate(self):
        return self.roll()[0]

class ActionSequence():
    def __init__(self, action, args, prev = None):
        if action == "drop":
            self.action = Drop(**args)
        elif action == "explode":
            self.action = Explode(**args)

        self.prev = prev

    def __call__(self, rollseq):
        if self.prev:
            return self.action(self.prev(rollseq))
        else:
            return self.action(rollseq)

class Drop():
    def __init__(self, droparg = "lowest", rollnum = Integer("1")):
        if droparg == "lowest":
            self.droparg = True
        else:
            self.droparg = False
        self.rollnum = rollnum

    # weird case: "(2d20 + 5) drop lowest" will sometimes drop the "+ 5"
    def __call__(self, rollseq):
        drops = int_or_eval(self.rollnum)

        if drops < 0:
            drops = -drops
            self.droparg = not self.droparg
        elif drops == 0:
            return rollseq

        if drops > len(rollseq):
            return [0]

        if self.droparg:
            return rollseq[drops:]
        else:
            return rollseq[:-drops]

class Explode():
    def __init__(self, exploderange = Integer("1")):
        self.exploderange = exploderange

    def __call__(self, rollseq):
        pass
