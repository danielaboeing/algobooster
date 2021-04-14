from ab_ui.ab_main.ps2py_parser import ps2py_yacc as parser
from ab_ui.ab_main import pylint_check as statcheck
from ab_ui.ab_main import ast_extraction as extract
from ab_ui.ab_main import ab_ml as mlagent
from ab_ui.ab_main import tip_chooser as tch

import os
import random
import shutil


# Top level directory
DATA_DIR = "ab_ui/ab_main/"
# Temporary directory to delete content from
TEMP_DIR = DATA_DIR + "temp/" 

def trainAB(code, classification):
    """ Trains the Algobooster machine learning system and
    returns a status message whether training was successful 
    or not, including tips from the static analysis if present.

    Keyword arguments:
    code -- the input pseudo code to train
    classification -- the class of the code 
    """

    # Create temporary directory
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Default response
    result = "Training was not successful."

    if code is None or code == "":
        return result

    # Parse the input
    parse_result = parser.parse_ps2py(code)

    # Set errors as response if there are any
    if parse_result.get('result') is None:
        result = parse_result.get('errors')
        return result


    # Static code analysis with a few corrections
    checker = statcheck.CodeChecker(TEMP_DIR)
    pylint_results = checker.executeCheck(addMain(parse_result.get('result')), "output_codebefore.py", "error_codebefore.log")
    pylint_results['corrected_code'] = removeMain(pylint_results['corrected_code'])

    # Set errors as response if there are any
    if pylint_results.get('errors') != "":
        result = "ERROR: " + pylint_results.get('errors') + "\n" + pylint_results.get('tips')
        return result

    # Get code changed by static analysis        
    res_code = pylint_results.get('corrected_code')

    # Extract attributes for machine learning
    extraction = extract.AttributeFinder(TEMP_DIR, True) 
    root = extraction.parseCodeToAST(res_code)
    attr_list = extraction.extractAttributes(root) 
    
    # Delete temporary directory
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # Check if attributes were extracted
    if attr_list == "":
        result = "Error while extracting attributes."
        return result
    
    # Start machine learning agent in training mode
    agent = mlagent.Agent(DATA_DIR)
    result = agent.train(attr_list, classification)  

    result += "\n" + pylint_results.get('tips')

    return result



def startAB(code, parse_only=False):
    """ Starts the Algobooster. Returns the parsed code, complexity,
    predicted classification with probability and further tips if all steps
    were successful.

    Keyword arguments:
    code -- the input pseudo code from the user
    parse_only -- checks if the code should only be parsed to Python (default False)
    """

    # Create temporary directory
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Default response
    result = {'code': 'Could not be parsed.','complexity': "Not calculated yet.",  'classification': 'Not classified yet.', 'probability': '0 %', 'tips' : ""}

    if code is None or code == "":
        return result

    # Parse the input and return errors if present
    parse_result = parser.parse_ps2py(code)
    if parse_result.get('result') is None:
        result['code'] = parse_result.get('errors')
        return result

    if parse_only:
        result['code'] = parse_result.get('result')
        return result

    # Static code analysis with a few corrections and creation of first tips
    checker = statcheck.CodeChecker(TEMP_DIR)
    pylint_results = checker.executeCheck(addMain(parse_result.get('result')), "output_codebefore.py", "error_codebefore.log")
    pylint_results['corrected_code'] = removeMain(pylint_results['corrected_code'])

    # Set errors as response if there are any
    if pylint_results.get('errors') != "":
        result['code'] = "ERROR: " + pylint_results.get('errors') + "\n" + pylint_results.get('tips')
        return result
    
    result['code'] = pylint_results.get('corrected_code')
    result['tips'] += pylint_results.get('tips')

    # Extract attributes for machine learning
    extraction = extract.AttributeFinder(TEMP_DIR) 
    root = extraction.parseCodeToAST(result['code'])
    complex_classes = {
        "4": "O(c^n)", # exponential / faculty
        "3": "O(n^c)", # polynomial
        "2": "O(n)", # linear
        "1": "O(log(n))", # logarithmic
        "0": "O(c)", # constant
    }

    predObj = extraction.extractAttributes(root)

    # Delete temporary directory
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # Check if attribute extraction was successful
    if predObj is None:
        result['code'] + "\nError while extracting attributes."
        return result

    result['complexity'] = complex_classes.get(extraction.getComplexity(root))

    # Start machine learning agent in prediction mode
    agent = mlagent.Agent(DATA_DIR)
    classificProb = agent.predict(predObj) 

    if classificProb is not None:
        # Get right tip for the given class prediction
        tipChooser = tch.TipChooser(classificProb.get('classification'))
        result['classification'] = tipChooser.getClassification()
        result['probability'] = str(classificProb.get('probability')) + " %"
        result['tips'] += tipChooser.getTip()

    return result

def addMain(py_code):
    """ Adds a main function with a random number
    around the input code so that the static code analysis 
    can do more checks.

    Keyword arguments:
    py_code -- the parsed Python code to add a main function to
    """

    result = "def main_" + randomMainNumber() + "():\n"
    for line in py_code.splitlines():
        # adds tabs for valid Python code
        result += "\t" + line + "\n"
    return result

def removeMain(py_code):
    """ Deletes the main function that was generated before.

    Keyword arguments:
    py_code -- the Python code containing a main function
    """

    result = ""
    first_line = py_code.splitlines()[0]
    py_code = py_code.replace(first_line + "\n", "")
    for line in py_code.splitlines():
        # removes the tabs inserted before
        result += line.replace("\t", "", 1) + "\n"
    return result

def randomMainNumber():
    """ Generates a random number combination with a 
    variable length between 1 and 10 numbers, each between
    0 and 100. This number combination is needed for the main
    function so that this function does not override
    a user written function.
    """

    result = ""
    end = random.randint(1, 10)
    for _ in range(1, end):
        result += str(random.randint(0, 100))
    return result