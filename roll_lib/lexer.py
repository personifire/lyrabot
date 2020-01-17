# read characters from a string and give out tokens
class lexer():
    def __init__(self, string):
        self.tokens = self.__tokenize(string.lower())
        self.EOF = self.Token("EOF", None)

    class Token():
        def __init__(self, tokentype, value):
            self.tokentype = tokentype
            self.value = value


        def __str__(self):
            return "('" + self.tokentype + "', '" + self.value + "')"

    def __T_OpenParen(self, string):
        return self.Token("OpenParen", string[0]) if string[0] == "(" else False

    def __T_CloseParen(self, string):
        return self.Token("CloseParen", string[0]) if string[0] == ")" else False

    def __T_Operator(self, string):
        return self.Token("Operator", string[0]) if string[0] in "+-" else False

    def __T_DiceSpecifier(self, string):
        isdicespecifier = string[0] == "d" and len(string) > 1 and string[1] in "(0123456789"
        return self.Token("DiceSpecifier", string[0]) if isdicespecifier else False

    def __T_NaturalNumber(self, string):
        digit = "01234567689"
        index = 0
        while index < len(string) and string[index] in digit:
            index += 1
        return self.Token("NaturalNumber", string[:index]) if index > 0 else False

    def __T_Action(self, string):
        #actions = ["drop", "explode"]
        actions = ["drop"]
        for action in actions:
            if len(string) >= len(action) and string[:len(action)] == action:
                return self.Token("Action", action)
        return False

    def __T_DropArg(self, string):
        args = ["lowest", "highest"]
        for arg in args:
            if len(string) >= len(arg) and string[:len(arg)] == arg:
                return self.Token("DropArg", arg)
        return False
    

    # if I were to do this properly, I'd use a FSM to classify tokens without backtracking
    # and if I were doing this properly, I'd do it lazily, i.e. one token at a time
    # but I'm not doing this properly :^)
    def __tokenize(self, string):
        tokens = []
        matchfuncs = [ 
                self.__T_NaturalNumber, self.__T_DiceSpecifier, self.__T_Operator,
                self.__T_Action,        self.__T_DropArg,
                self.__T_OpenParen,     self.__T_CloseParen,
        ]

        toparse = string[:]
        while toparse:
            toparse = toparse.lstrip() # skip whitespace
            for func in matchfuncs:
                match = func(toparse)
                if match:
                    tokens.append(match)
                    toparse = toparse[len(match.value):]
                    break
            if not match:
                errormsg  = "\nSorry, I couldn't understand the word starting here:\n" + string + "\n"
                errormsg += " " * (len(string) - len(toparse)) + "^\n"
                class LexingError(Exception):
                    pass
                raise LexingError(errormsg)

        tokens.reverse()
        return tokens

    def peek(self):
        return self.tokens[-1] if len(self.tokens) >= 1 else self.EOF

    def next(self):
        return self.tokens.pop() if len(self.tokens) >= 1 else self.EOF
    
    def unread(self, token):
        self.tokens.append(token)

