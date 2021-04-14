import ply.yacc as yacc
from ab_ui.ab_main.ps2py_parser.ps2py_lex import tokens

# precedence of mathematical operations
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'LPARENROUND', 'RPARENROUND')
)

errors = ""

start = 'code'

# General expressions

def p_code(p):
    '''code : expr 
            | expr code'''
    try:
        p[0] = p[1] + p[2]
    except IndexError:
        p[0] = p[1]

def p_expr(p):
    ''' expr : calcexpr
            | condexpr
            | loopexpr
            | funcexpr
            | returnexpr '''
    p[0] = p[1]


# Calculations

def p_calcexpr(p):
    ' calcexpr : var ASSIGN calc'
    p[0] =  p[1] + " = " + p[3] + "\n"

def p_calc(p):
    ''' calc : LPARENROUND calc RPARENROUND
            | calc op calc
            | term '''
    try:
        p[0] = p[1] + p[2] + p[3]
    except IndexError:
        if str(p[1]) == '(':
            p[0] = '(' + p[2] + ')'
        else:
            p[0] = p[1]

def p_op(p):
    '''op : PLUS 
            | MINUS 
            | TIMES 
            | DIVIDE 
            | INTDIVIDE 
            | MOD 
            | POWER'''
    if p[1] == '^':
        p[0] = " ** "
    else:
        p[0] = " " + p[1] + " "


# Data Types

def p_var(p):
    ''' var : NAME
            | NAME LPARENANG NUMBER RPARENANG
            | NAME LPARENANG NAME RPARENANG '''
    p[0] = p[1]
    try:
        p[0] += "[" + p[3] + "]"
    except IndexError:
        pass # no more arguments to handle

def p_term(p):
    ''' term : scalar
            | set
            | seq '''
    p[0] = p[1]

def p_scalar(p):
    ''' scalar : NUMBER
                | funccall
                | var '''
    p[0] = p[1]

def p_funccall(p):
    ' funccall : NAME LPARENROUND callparams RPARENROUND '
    p[0] = p[1] + '(' + p[3] + ')'

def p_callparams(p):
    ''' callparams : calc
                    | calc COMMA callparams'''
    p[0] = p[1]
    try:
        p[0] += ", " + p[3]
    except IndexError:
        pass # no more arguments to handle

def p_set(p):
    ''' set : LBRACE value RBRACE'''
    p[0] = '{' + p[2] + '}'

def p_seq(p):
    ' seq : LPARENANG value RPARENANG'
    p[0] = '[' + p[2] + ']'

def p_value(p):
    ''' value : scalar COMMA value
                | scalar'''
    try:
        p[0] = p[1] + ',' + p[3]
    except IndexError:
        p[0] = p[1]

# Conditions

def p_condexpr(p):
    '''condexpr : IF cond THEN code ENDIF
                | IF cond THEN code ELSE code ENDIF'''
    
    p[0] = 'if ' +  p[2] + ":" + "\nINDENT\n" + p[4] + "UNINDENT\n"
    try:
        p[0] += 'else:\nINDENT\n' + p[6] + "UNINDENT\n"
    except IndexError:
        pass # no extended rule needed

def p_cond(p):
    '''cond : LPARENROUND cond RPARENROUND
            | NOT cond
            | term
            | cond log cond
            | term comp term'''
    if p[1] == '(':
        p[0] = '(' + p[2] + ')'
    elif p[1] == 'not':
        p[0] = ' not(' + p[2] + ')'
    else:
        try:
            p[0] = p[1] + p[2] + p[3]
        except IndexError:
            p[0] = p[1]

def p_log(p):
    ''' log : AND
            | OR '''
    p[0] = " " + p[1] + " "

def p_comp(p):
    ''' comp : EQ
            | NOTEQ
            | GT
            | GE
            | LT
            | LE
            | IN
            | NOT IN'''
    p[0] = " " + p[1] + " "


# Loops

def p_loopexpr(p):
    ''' loopexpr : REPEAT code UNTIL cond
                | FOR condfor DO code ENDFOR'''
    if p[1] == 'repeat': # do-while-loop
        p[0] = 'while True:\nINDENT\n' + p[2] + 'if ' + p[4] + ":\n\tbreak\nUNINDENT\n"
    else:
        p[0] = 'for ' + p[2] + ":" + "\nINDENT\n" + p[4] + "UNINDENT\n"
    
def p_condfor(p):
    ''' condfor : NAME IN set
                | NAME IN NAME
                | NAME IN scalar TO scalar BY scalar '''
    try:
        if p[4] == 'to':
            p[0] = p[1] + ' in range(' + p[3] + "," + p[5] + "," + p[7] +")"
    except IndexError:
        p[0] = p[1] + ' in ' + p[3]

# Functions

def p_funcexpr(p):
    ' funcexpr : PROCEDURE NAME LPARENROUND params RPARENROUND code ENDPROC'
    p[0] = 'def ' + p[2] + " (" + p[4] + "):\nINDENT\n" + p[6] + "UNINDENT\n"
    
def p_returnexpr(p):
    ''' returnexpr : RETURN
                    | RETURN calc '''
    try:
        p[0] = "return " + p[2] + "\n"
    except IndexError:
        p[0] = "return\n"

def p_params(p):
    ''' params : NAME COMMA params
                | NAME '''
    p[0] = p[1]
    try:
        p[0] += ',' + p[3]
    except IndexError:
        pass # no more arguments to handle


# Error rule for syntax errors
def p_error(p):
    global errors
    errors += "Syntax error in input at: " + str(p) + "\n"

# Build the parser
parser = yacc.yacc()

# Parse method
def parse_ps2py(parse_string): 
    global errors
    errors = ""
    
    # Start parsing process
    result_pre = parser.parse(parse_string)
    if result_pre is None:
        return {'result': result_pre, 'errors': errors}

    # Add tabs for valid Python code
    result_after = ""
    tab = 0
    for line in result_pre.splitlines():
        if line == "INDENT":
            tab = tab+1
        elif line == "UNINDENT":
            tab = tab-1
        else:
            result_after += "\t" * tab + line + "\n"
    result_after = result_after.replace("  ", " ")
    return {'result': result_after.strip(), 'errors': errors}

