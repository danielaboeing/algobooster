import ply.lex as lex

# List of tokens

keywords = { 
    'procedure' : 'PROCEDURE', 
    'return' : 'RETURN', 
    'if' : 'IF',
    'then' : 'THEN',
    'do' : 'DO',
    'endfor' : 'ENDFOR',
    'endproc' : 'ENDPROC',
    'else' : 'ELSE',
    'endif' : 'ENDIF',
    'for' : 'FOR', 
    'repeat' : 'REPEAT',
    'until' : 'UNTIL',
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',
    'in' : 'IN',
    'to' : 'TO',
    'by' : 'BY'
}

comparison = [
    'EQ', 'NOTEQ', 'GT', 'GE', 'LT', 'LE'
]

mathematical = [
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'INTDIVIDE', 'MOD', 'POWER'
]

tokens = list(keywords.values()) + comparison + mathematical + [
    'LPARENROUND', 'RPARENROUND', 'LPARENANG', 'RPARENANG', 
    'LBRACE', 'RBRACE', 'ASSIGN', 'COMMA', 'NUMBER', 'NAME'
]

# Regex rules for simple tokens

t_EQ = r'=='
t_NOTEQ = r'!='
t_GT = r'>'
t_GE = r'>='
t_LT = r'<'
t_LE = r'<='
t_PLUS = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_INTDIVIDE = r'//'
t_MOD = r'%'
t_POWER = r'\^'
t_LPARENROUND  = r'\('
t_RPARENROUND  = r'\)'
t_LPARENANG = r'\['
t_RPARENANG = r'\]'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_ASSIGN = r'<-'
t_COMMA = r','

# Ignore the following characters
t_ignore = ' \t\n\b\f\r\v'

# Regex rule for action code

def t_NUMBER(t):
    r'[+|-]?\d+'
    t.value = str(int(t.value)) 
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value.lower(), 'NAME') # check for keywords (avoids having a rule for every single keyword)
    return t


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Testing
if __name__ == '__main__':
    data = "a <- 3+7 PROCEDURE { bla RETURN 3, 2 and ^ [3*2]"
    lexer.input(data)
    tok = lexer.token()
    while tok:
        print(tok)
        tok = lexer.token()