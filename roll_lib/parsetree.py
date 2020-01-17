import random

class Roll():
    def __init__(self, left, oper, right):
        self.left  = left
        self.oper  = oper
        self.right = right

    def roll():
        lval = self.left.roll()
        rval = self.right.roll()
        return self.oper(lval, rval)

    def evaluate():
        return self.roll()

class RollTerminal(Roll):
    def __init__(self, dice, faces, actionseq = None):
        self.dice      = dice
        self.faces     = faces
        self.actionseq = actionseq

    def roll():
        dice  = self.dice.roll()
        if dice < 0:
            rolls = [-self.faces.roll() for roll in range(-dice)]
        elif dice == 0:
            rolls = [0]
        else:
            rolls = [self.faces.roll() for roll in range(dice)]
        rolls.sort()

        if actionseq:
            roll = self.actionseq(roll)
        return roll

    def evaluate():
        return self.roll()

class Operator():
    def __init__(self, operator):
        if operator.value == "+":
            self.call = lambda a, b: sort(a + b)
        elif operator.value == "-":
            self.call = lambda a, b: sort(a - b)

    def __call__(self, lval, rval):
        return self.call(lval, rval)

class Integer():
    def __init__(self, number, operator = None):
        try:
            value = int(number, 0)
        except Exception as e:
            value = 0

        if operator == "-":
            value = -value

        self.value = value

    def roll():
        if self.value < 0:
            return random.randint(self.value, -1)
        elif self.value == 0:
            return 0
        else:
            return random.randint(1, self.value)

    def evaluate():
        return self.value

class ActionSequence():
    def __init__(self, action, args, prev = None):
        if action.value == "drop":
            self.action = Drop(*args)
        elif action.value == "explode":
            self.action = Explode(*args)

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
            return rollseq[drops:]
        elif self.droparg:
            return rollseq[:-drops]

class Explode():
    def __init__(self, exploderange = Integer("1")):
        self.exploderange = exploderange

    def __call__(self, rollseq):
        pass
