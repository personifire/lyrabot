import random

# explain only top level results

def total(lst):
    total = 0
    for val in lst:
        total += val
    return total

class Roll():
    def __init__(self, left, oper, right):
        self.left  = left
        self.oper  = Operator(oper)
        self.right = right

    def roll(self):
        lval = self.left.roll()
        rval = self.right.roll()
        return self.oper(lval, rval)

    def evaluate(self):
        return total(self.roll())

class RollTerminal(Roll):
    def __init__(self, dice, faces, actionseq = None):
        self.dice      = dice
        self.faces     = faces
        self.actionseq = actionseq

    def rand_dice(self, faces):
        if faces < 0:
            return random.randint(faces, -1)
        elif faces == 0:
            return 0
        else:
            return random.randint(1, faces)

    def roll(self):
        dicenum = self.dice.evaluate()
        facenum = self.faces.evaluate()

        if abs(dicenum) > 100000:
            raise Exception("Too many dice to roll")

        if dicenum < 0:
            rolls = [-self.rand_dice(facenum) for roll in range(-dicenum)]
        elif dicenum == 0:
            rolls = [0]
        else:
            rolls = [ self.rand_dice(facenum) for roll in range(dicenum)]
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
            value = int(number)
        except Exception as e:
            value = 0
            raise e

        if operator == "-":
            value = -value

        self.value = value

    def roll(self):
        return [self.value]

    def evaluate(self):
        return self.value

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
        drops = self.rollnum.evaluate()

        if drops < 0:
            drops = -drops
            self.droparg = not self.droparg
        elif drops == 0:
            return rollseq

        if drops > len(rollseq):
            return [0]

        if self.droparg:
            for drop in range(drops):
                rollseq.remove(min(rollseq))
        else:
            for drop in range(drops):
                rollseq.remove(max(rollseq))

        return rollseq

class Explode():
    def __init__(self, exploderange = Integer("1")):
        self.exploderange = exploderange

    def __call__(self, rollseq):
        pass
