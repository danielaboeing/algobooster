import ast
import astor
import shutil
import subprocess
from threading import Thread
import virtualenv

from ab_ui.models import AlgorithmData


TIMEOUT_TIME = 5 # seconds
TEMP_DIR = "" # default: current directory

class RunCodeEnv(Thread):
    """ Class for creating a virtual environment to run the submitted algorithm in. """

    def __init__(self, py_code):
        """ Initializes the RunCodeEnv instance.

        Keyword arguments:
        self -- the RunCodeEnv instance
        py_code -- the Python code to execute in the virtual environment
        """
        
        Thread.__init__(self)
        self.__timeout = TIMEOUT_TIME
        self.__subdir = TEMP_DIR
        self.__venv_path = self.__subdir + "virtualenvs/" # virtual environment path
        self.__python_path = self.venv_path + "bin/python" # path to the Python resources
        self.__script_file = self.__subdir + "sandbox_code.py" # file for the Python code
        self.__cmd = [self.python_path, self.script_file]
        self.__errfile = None
        self.__pathErrFile = self.venv_path + "/errors.log"

        # Write the Python code to the script file
        try:
            code_file = open(self.script_file, "w")
            code_file.write(py_code)
            code_file.close()
        except IOError as ioe:
            print("Error while writing code to file:", ioe)
            return None

        # Create 'safe' environment without wheel, pip, setuptools or site packages
        virtualenv.create_environment(self.venv_path,site_packages=False, no_wheel=True, no_pip=True, no_setuptools=True, clear=True)

        # Open stream to error file
        try:
            self.__errfile = open(self.pathErrFile, "w")
        except IOError as ioe:
            print("Error while opening errorfile:", ioe)
            return None


    def run(self):
        """ Inherited from 'Thread'. This method is called on RunCodeEnv.start().

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        self.__prg = subprocess.Popen(self.cmd, stderr=self.errfile) # Starts the execution of the python script in a subprocess
        self.prg.communicate() # Waits for child process to terminate

    def Run(self, check_type):
        """ Actually called run method from outside. Starts its own thread and checks if the
        program terminates. Additionally, checks if an error was output (like Maximum
        Recursion Depth). Returns 0 if the program exited normally, 0 otherwise.

        Keyword arguments:
        self -- the RunCodeEnv instance
        check_type -- the Class instance of which the attribute should be checked
        """

        # Start the Thread, run() is called
        self.start()
        # Wait for the thread termination for the length of the given timeout
        self.join(self.timeout)

        # If the time of timeout is over and the thread is still alive, kill it
        if self.is_alive():
            self.prg.terminate()
            self.prg.kill() # Ensures the termination of the program; most of the time, self.prg.terminate() should be enough
            if isinstance(check_type, ProgTerminate):
                return 1 # Program was killed because it takes very long or can not terminate
            #self.join()
        else:
            if isinstance(check_type, ProgTerminate):
                err_result = ""
                try:
                    readErr = open(self.pathErrFile, "r")
                    err_result = readErr.read()
                    readErr.close()
                except IOError as ioe:
                    print("Could not read error file:", ioe)
                    print("Possibly not existing.")
                    return 0
                if err_result != "":
                    return 1 # Problems were detected, like RecursionErrors
        
        return 0 # Program exited normally

    def cleanUp(self):
        """ Removes the virtual environment path.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        shutil.rmtree(self.venv_path, ignore_errors=True)

    # Class helper methods

    def getPrg(self):
        """ Gets the program that runs in the subprocess.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__prg

    def getCmd(self):
        """ Gets the command executed in the virtual environment.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__cmd

    def getTimeout(self):
        """ Gets the timeout time in seconds.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__timeout

    def getVenvPath(self):
        """ Gets the path to the virtual environment.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__venv_path

    def getPythonPath(self):
        """ Gets the path to the Python resources.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__python_path

    def getScriptFile(self):
        """ Gets the script file name and path.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__script_file

    def getErrFile(self):
        """ Gets the stream to the error file.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__errfile

    def getPathErrFile(self):
        """ Gets the error file name and path.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        return self.__pathErrFile


    def __del__(self):
        """ Destructor of RunCodeEnv. Closes the stream to the
        error file.

        Keyword arguments:
        self -- the RunCodeEnv instance
        """
        try:
            self.errfile.close()
        except IOError as ioe:
            print("Error file could not be closed:", ioe)

    prg = property(getPrg)
    cmd = property(getCmd)
    timeout = property(getTimeout)
    venv_path = property(getVenvPath)
    python_path = property(getPythonPath)
    script_file = property(getScriptFile)
    errfile = property(getErrFile)
    pathErrFile = property(getPathErrFile)



class RecCount():
    """ Class for checking the number of recursive calls in a function. """

    def getAttribute(self, root):
        """ Gets the 'Reccount' attribute. Returns the highest number of recursive calls
        in a function, whereas 0 equals no recursions.

        Keyword arguments:
        self -- the RecCount instance
        root -- the root node of the abstract syntax tree
        """

        rec_count = 0
        comp_val = 0
        func_name = ""
        for node in ast.walk(root):
            # Check for a function and save the name
            if isinstance(node, ast.FunctionDef):
                if node.name != func_name or func_name == "":
                    func_name = node.name
                    # Check if the function is called recursively and count how many times
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and child.func.id == func_name:  
                            comp_val = comp_val + 1

            # Check if compare value is higher than old value
            if comp_val > rec_count:
                rec_count = comp_val
                comp_val = 0
            
        return rec_count


class LoopNDepend():
    """ Class for checking whether a loop depends on the length of a set or list. """

    def getAttribute(self, root):
        """ Gets the 'LoopNDepend' attribute. Returns 1 if there is at least one loop that
        depends on the length of a set or list, 0 otherwise.

        Keyword arguments:
        self -- the LoopNDepend instance
        root -- the root node of the abstract syntax tree
        """

        n_depend = 0
        non_scalars = []
        for node in ast.walk(root):
            # Search the complete tree for any assignment where a list or set is used (on the left side) and save the variable name
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Set) or isinstance(node.value, ast.List):
                    for target in node.targets:
                        non_scalars += [target.id]

            # For for-loops, only check that a name (no call of 'range') is used; it is n_depend then            
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Name): # set or list is used, no call of range
                    n_depend = 1
                    break
            
            if isinstance(node, ast.While):
                # Here, only do-while-loops can be parsed
                # So, search for the loop condition, i.e. the if-condition with a break in the if-body
                ifBreakNode = self.getIfNodeWithBreak(node)
                if ifBreakNode != None:
                    # Check if there is a comparison
                    if isinstance(ifBreakNode.test, ast.Compare):
                        # Check left side for a name, i.e. the complete variable name
                        if isinstance(ifBreakNode.test.left, ast.Name) and ifBreakNode.test.left.id in non_scalars:
                            n_depend = 1                            
                            break
                        # Check left side for a subscript, i.e. calling the variable name with a certain index
                        if isinstance(ifBreakNode.test.left, ast.Subscript):
                            if isinstance(ifBreakNode.test.left.value, ast.Name) and ifBreakNode.test.left.value.id in non_scalars:
                                n_depend = 1                            
                                break
                        # Check the right side for the non scalar
                        for comp in ifBreakNode.test.comparators:
                            # Check for a name, see above
                            if isinstance(comp, ast.Name) and comp.id in non_scalars:
                                n_depend = 1
                                break
                            # CHeck for a subscript, see above
                            if isinstance(comp, ast.Subscript):
                                if isinstance(comp.value, ast.Name) and comp.value.id in non_scalars:
                                    n_depend = 1
                                    break


        return n_depend

    def getIfNodeWithBreak(self, whileNode):
        """ Searches the subtree for an if-node that contains a 'break' statement
        in the body. This is the loop-condition for the do-while-loop.

        Keyword arguments:
        self -- the LoopNDepend instance
        whileNode -- the while node and subtree to search in
        """
        
        for node in ast.walk(whileNode):
            # First, search for an if node
            if isinstance(node, ast.If):
                # Then, check the subtree for a break statement
                for child in ast.walk(node):
                    if isinstance(child, ast.Break):
                        return node
        return None

class ProgTerminate():
    """ Class for checking whether the algorithm terminates normally or not. """

    def getAttribute(self, root):
        """ Gets the 'ProgTerminate' attribute. Returns 0 if the program terminates after
        TIMEOUT_TIME seconds normally, or 1 if it was necessary to kill it.

        Keyword arguments:
        self -- the ProgTerminate instance
        root -- the root node of the abstract syntax tree
        """

        code = astor.to_source(root)
        venv = RunCodeEnv(code)
        if isinstance(venv, RunCodeEnv):
            result = venv.Run(self)
            venv.cleanUp()
        return result

class LoopNested():
    """ Class for checking the number of nested loops. """

    def getAttribute(self, root):
        """ Gets the 'LoopNested' attribute. Returns the number of nested loops, whereas
        0 equals no loops in program, and 1 a not-nested loop. The highest number of nested loops is saved.

        Keyword arguments:
        self -- the LoopNested instance
        root -- the root node of the abstract syntax tree
        """

        nested_loop = 0
        comp_val = 0
        
        # Initialization: Get child nodes to search in and save parent node
        children = ast.iter_child_nodes(root)
        last_parents = [root]
        child = next(children)
        visited = [root]
        loop_found = False

        # Depth-first-search
        while True:
            # Only search child if it was not already visited
            if child not in visited: 
                visited += [child]

                # Check if child is a loop
                if isinstance(child, ast.For) or isinstance(child, ast.While):
                    # Increment the number of nested loops and set child to children of the loop to search the subtree for more loops
                    loop_found = True
                    comp_val = comp_val + 1
                    last_parents += [child]
                    children = ast.iter_child_nodes(child)

            # Continue iterating
            try:
                child = next(children)
            except StopIteration: # No more children to iterate
                # New value is higher than last value
                if comp_val > nested_loop:
                    nested_loop = comp_val
                # Go back to last visited parent and continue searching the subtree, if there is a parent left
                try:
                    child = last_parents.pop()
                    children = ast.iter_child_nodes(child)
                    # Do not completely reset the compare value, but decrement it when there was a loop previously
                    if comp_val > 0 and loop_found:
                        comp_val -= 1
                    loop_found = False
                except IndexError:
                    break
                    
        return nested_loop

class LoopType():
    """ Class for checking the type of the loop if present. """

    def getAttribute(self, root):
        """ Gets the 'LoopType' attribute. Returns 0 if no loop is present,
        1 for at least one for-loop but no while-loop, 2 for at least one while-loop.

        Keyword arguments:
        self -- the LoopType instance
        root -- the root node of the abstract syntax tree
        """

        loop_type = 0
        for node in ast.walk(root):
            if isinstance(node, ast.For) and loop_type < 2:
                loop_type = 1
            if isinstance(node, ast.While):
                loop_type = 2
        return loop_type

class UsingNonScalar():
    """ Class for checking on the use of non scalars. """

    def getAttribute(self, root):
        """ Gets the 'UsingNonScalar' attribute. Returns 1 if at least one non scalar like a list or
        set is used, 0 otherwise.

        Keyword arguments:
        self -- the UsingNonScalar instance
        root -- the root node of the abstract syntax tree
        """
        nonscalar_found = 0
        for node in ast.walk(root):
            # Check if a set or list was used
            if isinstance(node, ast.Set) or isinstance(node, ast.List):
                nonscalar_found = 1
        return nonscalar_found

class RepeatValues():
    """ Class for checking on repeating values. """

    def getAttribute(self, root):
        """ Gets the 'RepeatValues' attribute. Returns 1 if the same value is assigned
        more than once to the same variable, 0 otherwise.

        Keyword arguments:
        self -- the RepeatValues instance
        root -- the root node of the abstract syntax tree
        """

        # Add function call at every var assignment
        for node in ast.walk(root):
            assign_childs = self.checkForDirectAssignChild(node)
            # For all direct children with assignment, add a function call to 'addToSaveVarValues'
            for child in assign_childs:
                try:
                    for target in child.targets: # do it for all targets in the assignment, e.g. 'a, b = ...'
                        if isinstance(target, ast.Name):
                            curNode = ast.Expr(value=ast.Call(func=ast.Name(id='addToSaveVarValues', ctx=ast.Load()), 
                                                args=[ast.Name(id="'" + target.id + "'", ctx=ast.Load()), child.value],
                                                keywords=[]))
                            node.body.insert(0, curNode)
                            ast.fix_missing_locations(curNode) # automatically adds the attributes 'lineno' and 'col_offset' of the added node needed by AST
                           
                except AttributeError:
                    pass # node object has no body attribute - avoid inserting node more than once

        code = astor.to_source(root)

        # New code with added function
        code = """
saveVarValues = { }

def addToSaveVarValues(var, value):
    found = False
    try:
        for values in saveVarValues.get(str(var)):
            if value == values:
                found = True
    except TypeError:
        saveVarValues[str(var)] = []
    except KeyError:
        found = False

    if not(found):
        saveVarValues[str(var)] += [value]
    else:
        try:
            checkFile = open( "%s", "w")
            checkFile.write("1")
            checkFile.close()
        except IOError as ioe:
            print("Error while writing saved var values to file:", ioe)

""" % (TEMP_DIR + "virtualenvs/checkFile.txt") + code

        # Execute the extended code
        venv = RunCodeEnv(code)
        if isinstance(venv, RunCodeEnv):
            venv.Run(self)

        # Read the result
        result = 0
        try:
            checkFile = open(TEMP_DIR + "virtualenvs/checkFile.txt", "r")
            res_file = checkFile.read()
            if int(res_file) == 1:
                result = 1
            checkFile.close()
        except IOError as ioe:
            print("Could not open saved var values file:", ioe)
            print("Possibly none existing.")
        except ValueError:
            result = 0

        if isinstance(venv, RunCodeEnv):
            venv.cleanUp()

        return result

    def checkForDirectAssignChild(self, node):
        """ Checks the node's direct children for assignment nodes
        and returns them if present.

        Keyword arguments:
        self -- the RepeatValues instance
        node -- the subtree node root to search in
        """

        assign_childs = []
        # In contrast to ast.walk(node), only iterate over the direct children of node
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Assign):
                assign_childs += [child]
        return assign_childs



class ReuseValues():
    """ Class for checking on reused values. """

    def getAttribute(self, root):
        """ Gets the 'ReuseValues' attribute. Returns 1 if values are
        reused, for example in a loop or recursive function call, 0 otherwise.

        Keyword arguments:
        self -- the ReuseValues instance
        root -- the root node of the abstract syntax tree
        """
        reuse_values = 0
        func_name = ""
        indexVars = {}
        for node in ast.walk(root):
            # Check if a variable is used and assigned in a loop; this is then done repeatedly
            if isinstance(node, ast.While) or isinstance(node, ast.For):
                if self.checkSubTreeForVarName(node) is not None:
                    reuse_values = 1
                    break

            # Check if a variable is used and assigned in a recursive function and taken into function call; this is then done repeatedly
            if isinstance(node, ast.FunctionDef):
                # Get the function name
                if node.name != func_name or func_name == "":
                    func_name = node.name
                    # Get the variable name which could possibly be repeatedly called
                    var_name = self.checkSubTreeForVarName(node)
                    if var_name is not None:
                        indexVars[var_name] = node
                    # Check children of function for a recursive call
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and child.func.id == func_name: 
                            # Now it is a recursive function; check reuse
                            for arg in child.args:
                                if isinstance(arg, ast.Name) and arg.id in indexVars and indexVars[arg.id] == node:
                                    reuse_values = 1
                                    break

        return reuse_values

    def checkSubTreeForVarName(self, node):
        """ Checks a given sub tree for an assignment in which a
        variable is present on both sides of the assignment, e.g. i = 1 + i.
        Returns the variable name for which this is the case, None otherwise.

        Keyword arguments:
        self -- the ReuseValues instance
        node -- the subtree root node to search in
        """

        var_name = None
        for child in ast.walk(node):
            # Search for assignment node
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    # Check for a variable name
                    if isinstance(target, ast.Name):
                        # Checks if the same variable is assigned to it directly; it is then reused
                        if isinstance(child.value, ast.Name) and target.id == child.value.id:
                            return target.id
                        # Checks if the same variable is assigned using a calculation; it is then reused
                        elif isinstance(child.value, ast.BinOp):
                            for subchild in ast.walk(child):
                                if isinstance(subchild, ast.Name) and target.id == subchild.id:
                                    return target.id
                            
        return var_name

class AttributeFinder():
    """ Main class for extracting attributes """
    
    def __init__(self, base_dir, attrs_as_dict = False):
        """ Initializes the AttributeFinder instance.

        Keyword arguments:
        self -- the AttributeFinder instance
        base_dir -- the basic temporary directory to work on
        attrs_as_dict -- if set to True, the attributes are (later) returned as dictionary; else, they are returned as AlgorithmData object (default False)
        """

        global TEMP_DIR
        TEMP_DIR = base_dir
        self.__delimiter = ","
        self.__attr_classes = {
            "Number of recursive calls in a recursive function": RecCount(),
            "Loop condition depends on a length n": LoopNDepend(),
            "Number of nested loops": LoopNested(),
            "Type of loop": LoopType(),
            "Program terminates normally and independently": ProgTerminate(),
            "At least one non scalar is used": UsingNonScalar(),
            "Repeating values are assigned to variable": RepeatValues(),
            "Variable is used repeatedly": ReuseValues(),
        }
        self.__attr_pattern = []
        for key in self.attr_classes.keys():
            self.__attr_pattern += [key]
        self.__attr_pattern += ["Complexity"]
        self.__results = None
        self.__attrs_as_dict = attrs_as_dict

    
    def parseCodeToAST(self, py_code):
        """ Parses a given code to an abstract syntax tree (AST).

        Keyword arguments:
        self -- the AttributeFinder instance
        py_code -- the code to be parsed to AST
        """
        root = ast.parse(py_code, mode='exec')
        return root

    def parseASTToCode(self, root):
        """ Parses a given abstract snytax tree (AST) to Python code.

        Keyword arguments:
        self -- the AttributeFinder instance
        root -- the root node of the AST
        """
        py_code = astor.to_source(root)
        return py_code
 
    def extractAttributes(self, root):
        """ Method to extract the attributes. Depending on initializiation of the class,
        a dictionary or an instance of AlgorithmData is returned.

        Keyword arguments:
        self -- the AttributeFinder instance
        root -- the root node of the abstract syntax tree
        """
        
        # Checks if an extraction was already done (e.g. by getComplexity); if not, extracts the attributes
        if self.results is None:

            self.results = {}

            for attr in self.attr_classes:
                # Call the 'getAttribute' method of all attribute extracter classes
                res = self.attr_classes.get(attr).getAttribute(root)
                self.results[self.attr_classes.get(attr).__class__.__name__] = res
            
            # Calculate the complexity
            self.results['Complexity'] = self.getComplexity(root)

        # Return an object if attrs_as_dict is set to False
        if not(self.attrs_as_dict):
            predObj = AlgorithmData()
            predObj.initAttr(self.results)
            predObj.save()
            return predObj
        
        else:
            return self.results


    def getComplexity(self, root):
        """ Gets the complexity of the algorithm.

        Keyword arguments:
        self -- the AttributeFinder instance
        root -- the root node of the abstract syntax tree
        """

        func_name = ""
        divOp = False
        isRec = False

        mainComplex = 0 # constant if no other applies

        # Try getting the result of ProgTerminate
        progTerm = self.results.get('ProgTerminate')

        # If not existent, call the extractAttributes method
        if progTerm is None:
            self.extractAttributes(root)
            progTerm = self.results.get('ProgTerminate')
        
        # If program did not terminate normally, it is too complex
        if progTerm == 1:
            mainComplex = 4
            return str(mainComplex)

        # Check whether, if a recursion is present, the arguments in the recursive call are minimized by recursion
        for node in ast.walk(root):
            # Check if there is a function
            if isinstance(node, ast.FunctionDef):
                if node.name != func_name or func_name == "":
                    func_name = node.name
                    for child in ast.walk(node):
                        # Check if there is a recursive call in the function
                        if isinstance(child, ast.Call) and child.func.id == func_name: 
                            isRec = True
                            # Check if the recursive call contains a calculation respectively a division
                            for item in child.args:
                                if isinstance(item, ast.BinOp) and isinstance(item.op, ast.Div):
                                    divOp = True

        # first check on exponential: recursion
        if isRec:
            mainComplex = 3 # polynomial if tree is constructed through recursive call
            if not(divOp): # if the arguments are not divided in the recursive call
                mainComplex = 4
                return str(mainComplex)

        curComplex = 0

        indexVars = {}
        logWhiles = []

        # Check logarithmic which is present if the variable for a while loop is minimized by dividing in the loop body
        for node in ast.walk(root):
            # Check if there is a while loop
            if isinstance(node, ast.While):
                ifNode = LoopNDepend().getIfNodeWithBreak(node)
                # Check if a variable is used for the loop condition and save the name
                if ifNode is not None and isinstance(ifNode.test, ast.Compare):
                    if isinstance(ifNode.test.left, ast.Name):
                        indexVars[ifNode.test.left.id] = node
                    elif isinstance(ifNode.test.comparators, ast.Name):
                        indexVars[ifNode.test.comparators.id] = node
                
                for child in ast.walk(node):
                    # Check if there is an assignment in the while loop
                    if isinstance(child, ast.Assign):
                        # Check if the assignment contains a saved variable from the loop condition
                        for target in child.targets:
                            if isinstance(target, ast.Name) and target.id in indexVars:
                                if isinstance(child.value, ast.BinOp):
                                    if isinstance(child.value.left, ast.Name) and child.value.left.id == target.id:
                                        # Check if there is a division in the calculation
                                        if isinstance(child.value.op, ast.Div):
                                            curComplex = 1
                                            logWhiles += [indexVars.get(target.id)]

            # If the current complexity is higher than before, set it as new complexity
            if curComplex > mainComplex:
                mainComplex = curComplex
            curComplex = 0


        # Get number of nested loops; if not present, call the extractAttributes method
        numLoops = self.results.get('LoopNested')
        if numLoops is None:
            self.extractAttributes(root)
            numLoops = self.results.get('LoopNested')


        # if there is one not-nested loop which is not a log-while-loop, set complexity to linear
        # Note: complexity can not be exponential as this value was already returned at calculation        
        if numLoops > 0 and mainComplex != 1:
            mainComplex = 2
        # if there is an at least once-nested loop, set complexity to polynomial
        if numLoops > 1:
            mainComplex = 3

        # Check loop-exponential complexity
        for node in ast.walk(root):
            
            if isinstance(node, ast.For):
                # check for use of 'range'; if not, complexity is set to exponential
                if not(isinstance(node.iter, ast.Call) and node.iter.func.id == "range"):
                    curComplex = 4
           
                    
            if isinstance(node, ast.While) and not(node in logWhiles):
                # if while is no log-while and not n dependent: no defined end; complexity is exponential
                n_depend = self.results.get('LoopNDepend')
                if n_depend == 0:
                    curComplex = 4

            # If the current complexity is higher than before, set it as new complexity
            if curComplex > mainComplex:
                mainComplex = curComplex
            curComplex = 0
        
        return str(mainComplex)

    # Class helper methods

    def getAttrPattern(self):
        """  Returns the attribute pattern.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        return self.delimiter.join(self.__attr_pattern)

    def getAttrClasses(self):
        """  Returns the attribute classes.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        return self.__attr_classes

    def getDelimiter(self):
        """  Returns the delimiter.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        return self.__delimiter

    def getResults(self):
        """  Returns the extraction result.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        return self.__results

    def getAttrsAsDict(self):
        """  Returns the attributes as dictionary variable.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        return self.__attrs_as_dict

    def setResults(self, other):
        """  Sets the extraction result.

        Keyword arguments:
        self -- the AttributeFinder instance
        """
        self.__results = other


    attr_pattern = property(getAttrPattern)
    attr_classes = property(getAttrClasses)
    delimiter = property(getDelimiter)
    attrs_as_dict = property(getAttrsAsDict)
    results = property(getResults, setResults)

