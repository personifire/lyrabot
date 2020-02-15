import random

from . import lexer # thing under test

def randomchoice(rules):
    productions = []
    weights     = []

    for production, weight in rules:
        productions.append(production)
        weights.append(weight)

    return random.choices(productions, weights)[0]

def roll():
    rules = [
                (["d", rollnum],              10),
                ([rollnum, "d", rollnum],     50),
                ([roll, oper, roll],          20),
                ([natnum],                    20),
                ([roll, actionseq],           10),
                (["(", roll, ")"],            5),
              ]
    return randomchoice(rules)

def rollnum():
    rules = [
                (["(", roll, ")"],            10),
                ([natnum],                    90),
            ]
    return randomchoice(rules)
    
def oper():
    rules = [
                (["+"],                       50),
                (["-"],                       50),
            ]
    return randomchoice(rules)

def natnum():
    randint = str(random.randrange(0, 10))
    rules = [
                ([randint],                   80),
                ([randint, natnum],           20),
            ]
    return randomchoice(rules)

def actionseq():
    rules = [
                (["drop", dropargs],          45),
                (["explode"],                 45),
                ([actionseq, actionseq],      10),
            ]
    return randomchoice(rules)

def dropargs():
    rules = [
                ([""],                        10),
                (["lowest"],                  40),
                (["highest"],                 30),
                (["lowest", natnum],          10),
                (["highest", natnum],         10),
            ]
    return randomchoice(rules)

def expand(expression):
    index = 0
    # ll expand
    while index < len(expression):
        symbol = expression[index]
        if not isinstance(symbol, str):
            expression = expression[:index] + symbol() + expression[index + 1:]
        else:
            index += 1
    return expression

def main():
    # 100 valid expressions
    for i in range(100):
        expression = [roll]
        print("Building expression: ")
        expression = expand(expression)
        print("Lexing expression: " + str(expression))
        lex = lexer.lexer("".join(expression))
        tokens = []
        token = lex.next()
        while token:
            tokens.append(str(token))
            token = lex.next()
        print("Lexed expression: " + str(tokens) + "\n")

    # just one bad one
    expression = [roll]
    print("Making almost-valid expression")
    print("Building expression: ")
    expression = expand(expression)
    expression = "".join(expression)
    print("Built expression: " + expression)
    rand = random.randrange(0, len(expression))
    expression = expression[:rand] + "i" + expression[rand:]
    print("Lexing bad expression: " + expression)
    lex = lexer.lexer(expression)
    tokens = []
    token = lex.next()
    while token:
        tokens.append(token.value)
        token = lex.next()
    print("Lexed expression: " + str(tokens))

if __name__ == "__main__":
    main()
