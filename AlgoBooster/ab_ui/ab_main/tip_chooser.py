

class TipChooser():
    """ Class used to match the classification to the fitting tip and class name.  """

    tip_none = ["None", """
            There are no further optimizations you can do using algorithmic design methods.
            Please consider the results of the static code analysis above.
        """]

    tip_divAndConq = ["Divide and Conquer", """
            To use the 'Divide and Conquer' pattern, you first have to split (divide) the problem in several subproblems until you get the smallest, possible problem.
            Then, you 'conquer' the problem by recursively applying the same operation you applied on the smallest problem on the bigger ones. 
            Additionally, after the smaller problems were solved, you have to merge the subsolutions to a bigger solution to use on the next recursive call. 
        """] 

    tip_dynProg = ["Dynamic Programming", """
            It seems like your algorithm repeatedly calculates the same values, for example in a loop or a recursive function call. 
            Try calculating these values before the loop or function to optimize your algorithm. 
            This could look like this:

            The code
            <code>for i in range(0, 10, 1):
                var = i * i + i
            </code>
            is optimized to
            <code>a[i] = i*i + i
            for i in range(0, 10, 1):
                var = a[i]
            </code>

            (In this particular case, you could also remove the loop then.)
        """]

    tip_greedy = ["Greedy Heuristic", """
            Stop looking for the best possible solution in your program - it seems like it takes too long. 

            If you are using a condition or calculation to evaluate if your current solution is a possible solution, stop your loop or recursion at that point if it is the case. 
            You might not have the optimal solution then, but a good solution in reasonable time.
        """]

    tip_bnb = ["Branch and Bound", """
            You have two take two steps for Branch and Bound. 
            While branching, you have to divide your problem into subproblems (if you have not already done it in your program like in Backtracking). 
            Then, you have to bound, so not follow ways that do not lead to a (better) solution. 

            To do this, you could for example check your if- or loop-condition before checking a subtree (so before doing further calculations) or branch your (break) condition into subproblems and subcalls.
        """]

    tip_randalg = ["Randomized Algorithm", """
            Presumably, your algorithm took much too long or will not even terminate. This is because you might only be able to approximate your desired solution.

            To approximate your solution, define the number of runs (through a loop, e.g.) and stop your approximation after the number of runs. To randomize it now, you could take a random value for your variable that limits your number of runs (loop, recursion, etc.). This will optimize your algorithm.
        """]

    def __init__(self, classification):
        """ Initializes the tip chooser.

        Keyword arguments:
        self -- the TipChooser instance
        classification -- the class the tip chooser should return the hints for
        """
        self.__classification = classification
        self.__classific_details = {
            '0': self.tip_none,
            '1': self.tip_divAndConq,
            '2': self.tip_dynProg,
            '3': self.tip_bnb,
            '4': self.tip_greedy,
            '5': self.tip_randalg,
        }


    # Class helper methods

    def getTip(self):
        """ Returns the fitting tip for the classification.

        Keyword arguments:
        self --- the TipChooser instance
        """
        return self.classific_details[str(self.__classification)][1]

    def getClassification(self):
        """ Returns the classification as text.

        Keyword arguments:
        self --- the TipChooser instance
        """
        return self.classific_details[str(self.__classification)][0]

    def getClassificDetails(self):
        """ Returns the classification details dictionary.

        Keyword arguments:
        self --- the TipChooser instance
        """
        return self.__classific_details

    classific_details = property(getClassificDetails)

    
