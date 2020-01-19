from . import lexer
from . import parsetree

# take tokens and return an abstract syntax tree
# simple recursive decent parser
class parser():
    class ParsingError(Exception):
        pass

    def __init__(self, string):
        self.lexer = lexer.lexer(string)

    def evaluate(self):
        roll = self.__Roll()
        self.__expect(self.lexer.next(), "EOF")
        return roll.roll()

    def __match(self, actual, expect):
        return actual.tokentype == expect

    def __expect(self, obj, expect = None):
        if expect:
            if obj.tokentype == expect:
                return obj
            else:
                errormsg = "Expected token " + expect + " not found"
                raise self.ParsingError(errormsg)
        else:
            if obj:
                return obj
            else:
                errormsg = "Expected object not found" # probably should make a helpful error
                raise self.ParsingError(errormsg)

    def __RollTerminal(self):
        """ return a Roll object that has no children Rolls and be evaluated to get a random roll, or None if not matched """
        roll = None
        token = self.lexer.peek()
        # d rollnum
        if self.__match(token, "DiceSpecifier"):
            self.__expect(self.lexer.next(), "DiceSpecifier")
            dice  = parsetree.Integer("1")
            faces = self.__expect(self.__Rollnum())
        else:
            dice = self.__Rollnum()
            if dice:
                # rollnum d rollnum
                if self.__match(self.lexer.peek(), "DiceSpecifier"):
                    self.__expect(self.lexer.next(), "DiceSpecifier")
                    faces = self.__expect(self.__Rollnum())
                # rollnum
                else:
                    return dice # lol
            else:
                return None

        # action-seq ?
        actionseq = None
        if self.__match(self.lexer.peek(), "Action"):
            actionseq = self.__expect(self.__ActionSequence())

        roll  = parsetree.RollTerminal(dice, faces, actionseq)
        return roll

    def __Roll(self):
        """ return a Roll object with children Rolls that can be evaluated to get a random roll, or None if not matched """
        roll = self.__RollTerminal()
        if not roll:
            return None

        # { oper roll }
        while self.__match(self.lexer.peek(), "Operator"):
            operator = self.__expect(self.lexer.next(), "Operator")
            right    = self.__expect(self.__RollTerminal())

            roll = parsetree.Roll(roll, operator.value, right)

        return roll
    
    def __Rollnum(self):
        """ return an object that can be evaulated, or None if not matched """
        retobj = None
        token = self.lexer.peek()
        # "(" roll ")"
        if self.__match(token, "OpenParen"):
            self.__expect(self.lexer.next(), "OpenParen")
            retobj = self.__expect(self.__Roll())
            self.__expect(self.lexer.next(), "CloseParen")
        # integer
        else:
            retobj = self.__Integer()
            if not retobj:
                return None
        return retobj

    def __Operator(self):
        """ return an Operator object with dependency injection for Roll to evaluate, or None """
        # "+" || "-"
        if self.__match(self.lexer.peek(), "Operator"):
            operator = self.__expect(self.lexer.next(), "Operator")
            return parsetree.Operator(operator.value)
        else:
            return None

    def __Integer(self):
        """ return a Integer object that can be evaluated, or None if not matched """
        operator = None
        # oper ?
        if self.__match(self.lexer.peek(), "Operator"):
            operator = self.__expect(self.lexer.next(), "Operator")

        # natnum
        if self.__match(self.lexer.peek(), "NaturalNumber"):
            number = self.__expect(self.lexer.next(), "NaturalNumber")
            if operator:
                return parsetree.Integer(number.value, operator.value)
            else:
                return parsetree.Integer(number.value)
        else:
            if operator:
                self.lexer.unread(operator)
            return None

    def __ActionSequence(self):
        """ return an ActionSequency object with dependency injection for Roll, or None """
        actionseq = None
        while self.__match(self.lexer.peek(), "Action"):
            action = self.__expect(self.lexer.next(), "Action")
            args = {}
            # "drop" drop-args ?
            if action.value == "drop":
                # droparg ? rollnum ?
                if self.__match(self.lexer.peek(), "DropArg"):
                    args["droparg"] = self.__expect(self.lexer.next(), "DropArg").value
                rollnum = self.__Rollnum()
                if rollnum:
                    args["rollnum"] = rollnum
            actionseq = parsetree.ActionSequence(action.value, args, actionseq)

        return actionseq

