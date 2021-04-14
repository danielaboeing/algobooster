
from pylint import epylint as lint

class CodeChecker():
    """ Class for the static code analysis. """

    def __init__(self, base_dir):
        """ Initializes the code checker.

        Keyword arguments:
        self -- the CodeChecker instance
        base_dir -- the basic temporary directory to work on
        """
        self.__base_dir = base_dir

        self.__pylint_options = ' -s n' # show no score
        self.__pylint_options += ' -f text' # set output format to text
        self.__pylint_options += ' -r n' # no full report, only messages
        self.__pylint_options += " --msg-template='[{msg_id}]{line:3d}: {msg}'" # set message template
        self.__relevant_msgs = {
            'error_msgs': [
                'E0001', # syntax error
                'E0102', # function redefined
                'E0108', # duplicate argument name
                'E0301', # non-iterator-returned, object not iterable (e.g. 'for i in set' loop)
                'E0601', # local variable used before assigned
                'E0602', # undefined variable
                'E0603', # undefined all variable
                'E0604', # undefined all object
                'E0611', # no name in module, sth was not found
                'E1120', # no value for parameter, too few arguments
                'E1121', # too many arguments
                'E1126', # invalid sequence index, possible wrong type (non-array instead of array)
                'E1133', # not iterable
                'F0001', # fatal error (e.g. module not found)
                'F0010', # parse error
                'R0123', # compared literal to object
                'W0631', # loop variable used outside scope
            ],
            'tip_msgs': [
                'E1111', # assignment from function that does not return
                'E1128', # assignment from function that returns None
                'R1705', # unnecessary 'else' after 'return'
                'W0101', # unreachable code
                'W0125', # using constant for if test
                'W0612', # unused variable

            ],
            'change_msgs': [
                'W0122', # use of exec
            ]
        }
        self.__keywords = ["import", "eval", "compile", "input", "open", "close"]

    def executeCheck(self, py_code, code_file, error_file):
        """ Executes the static code analysis. Returns a result containing
        the corrected code, possible errors and tips from the analysis.

        Keyword arguments:
        self -- the CodeChecker instance
        py_code -- the submitted and parsed Python code to check
        code_file -- name of the file where the code should be written to
        error-file -- name of the file where the errors should be written to
        """

        # Initialize response and file paths
        result = {'corrected_code': py_code, 'errors': "", 'tips' : ""}
        filename = self.base_dir + code_file
        errorfile =  self.base_dir + error_file

        # Delete lines with certain keywords
        for kw in self.keywords:
            kw_res = self.checkAndFixKeyword(result.get('corrected_code'), kw)
            if kw_res[1]:   # line with keyword was found
                result['tips'] += "Use of '" + kw + "' forbidden. Line was removed.\n"
                result['corrected_code'] = kw_res[0]

        # Try writing code to file
        if self.writeToFile(result['corrected_code'], filename) != 0:
            return result

        # Get result of the pylint analysis
        (pylint_stdout, pylint_stderr) = lint.py_run(filename + self.pylint_options, return_std=True)
        output = pylint_stdout.read()

        # Try writing errors to file
        if self.writeToFile(pylint_stderr.read(), errorfile) != 0:
            print("Error log could not be written!")

        # Get error messages: code won't be checked further if at least one of them appears
        for msg in self.relevant_msgs.get('error_msgs'):
            result['errors'] += self.checkAndReportMsg(msg, self.getFittingLine(msg,output))

        # Get tip messages: these will be returned for further human optimization
        for msg in self.relevant_msgs.get('tip_msgs'):
            result['tips'] += self.checkAndReportMsg(msg, self.getFittingLine(msg, output))

        # Get change messages: these will be changed immediately by program
        for msg in self.relevant_msgs.get('change_msgs'):
            result['corrected_code'] = self.checkAndFixMsg(result.get('corrected_code'), msg, self.getFittingLine(msg,output))

        return result

    def getFittingLine(self, msg, stdout):
        """ Gets the line of the pylint result containing the searched message.

        Keyword arguments:
        self -- the CodeChecker instance
        msg -- the message to search the output for
        stdout -- the pylint output to search in
        """
        for line in stdout.splitlines():
            if msg in line:
                return line
        return None

    def writeToFile(self, content, filename):
        """ Writes a given content to the given file.

        Keyword arguments:
        self -- the CodeChecker instance
        content -- the content to write to the file
        filename -- the name and path of the file to write the content to
        """
        try:
            code_file = open(filename, "w")
            code_file.write(content)
            code_file.close()
        except IOError as ioe:
            print("Error while writing to file:", ioe)
            return -1
        return 0

    def checkAndReportMsg(self, msg_code, line):
        """ Checks for and extracts messages used for optimization hints.

        Keyword arguments:
        self -- the CodeChecker instance
        msg_code -- the code of the searched message
        line -- the complete line which contains the message
        """

        if line is None:
            return ""
        
        lineno = int(line[(len(msg_code) + 3):line.index(':')]) # start: after message code and two brackets, starting at 0
        lineno = lineno-1 # substracts 1 because of the added main function which does not belong to the initial program
        line = line.replace("[" + msg_code + "]", "line ") + "\n"
        line = "line " + str(lineno) + line[line.index(':'):]
        return line

    def checkAndFixMsg(self, py_code, msg_code, line):
        """ Checks for and corrects messages that can be changed immediately.

        Keyword aruments:
        self -- the CodeChecker instance
        py_code -- the code to correct
        msg_code -- the code of the searched message
        line -- the complete line which contains the message
        """

        if line is None:
            return py_code

        lineno = int(line[(len(msg_code) + 3):line.index(':')]) # start: after message code and two brackets, starting at 0
        
        # remove line (either with or without newline)
        linecontent = py_code.splitlines()[lineno-1] # substracts 1 because of the added main function which does not belong to the initial program
        py_code = py_code.replace(linecontent + "\n", "")
        py_code = py_code.replace(linecontent, "")
        return py_code            

    def checkAndFixKeyword(self, py_code, keyword):
        """ Checks for and removes line containing the given keyword.

        Keyword arguments:
        self -- the CodeChecker instance
        py_code -- the code to correct
        keyword -- the Python keyword to search for
        """
        
        result = ""
        found = False
        for line in py_code.splitlines():
            if keyword not in line:
                result += line + "\n"
            else:
                found = True
        return (result, found)

    # Class helper methods

    def getPylintOptions(self):
        """ Returns the Pylint options.

        Keyword arguments:
        self -- the CodeChecker instance
        """
        return self.__pylint_options

    def getRelevantMsgs(self):
        """ Returns the relevant messages.

        Keyword arguments:
        self -- the CodeChecker instance
        """
        return self.__relevant_msgs

    def getKeywords(self):
        """ Returns the keywords

        Keyword arguments:
        self -- the CodeChecker instance
        """
        return self.__keywords

    def getBaseDir(self):
        """ Returns the base directory.

        Keyword arguments:
        self -- the CodeChecker instance
        """
        return self.__base_dir

    pylint_options = property(getPylintOptions)
    relevant_msgs = property(getRelevantMsgs)
    keywords = property(getKeywords)
    base_dir = property(getBaseDir)

# Testing
if __name__ == '__main__':
    checker = CodeChecker("temp/")
    checker.executeCheck("a = 3\n", "output.py", "error.py")