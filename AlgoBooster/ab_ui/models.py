from django.db import models

class AlgorithmData(models.Model):
    """ General class for algorithm attributes (prediction case). """

    rec_count = models.IntegerField()
    loop_n_depend = models.IntegerField()
    loop_nested = models.IntegerField()
    loop_type = models.IntegerField()
    prog_terminate = models.IntegerField()
    using_non_scalar = models.IntegerField()
    repeat_values = models.IntegerField()
    reuse_values = models.IntegerField()
    complexity = models.IntegerField()
        
    def initAttr(self, attr_list):
        """ Initializes the algorithm attributes.

        Keyword arguments:
        self -- the AlgorithmData instance
        attr_list -- dictionary containing the names and values of the attributes for this instance
        """
        self.rec_count = attr_list.get('RecCount')
        self.loop_n_depend = attr_list.get('LoopNDepend')
        self.loop_nested = attr_list.get('LoopNested')
        self.loop_type = attr_list.get('LoopType')
        self.prog_terminate = attr_list.get('ProgTerminate')
        self.using_non_scalar = attr_list.get('UsingNonScalar')
        self.repeat_values = attr_list.get('RepeatValues')
        self.reuse_values = attr_list.get('ReuseValues')
        self.complexity = attr_list.get('Complexity')

    def getValues(self):
        """ Returns the attributes of the instance as dictionary.

        Keyword arguments:
        self -- the AlgorithmData instance
        """
        attr_list = {}
        attr_list['RecCount'] = self.rec_count
        attr_list['LoopNDepend'] = self.loop_n_depend
        attr_list['LoopNested'] = self.loop_nested
        attr_list['LoopType'] = self.loop_type
        attr_list['ProgTerminate'] = self.prog_terminate
        attr_list['UsingNonScalar'] = self.using_non_scalar
        attr_list['RepeatValues'] = self.repeat_values
        attr_list['ReuseValues'] = self.reuse_values
        attr_list['Complexity'] = self.complexity
        return attr_list


    def __str__(self):
        """ Returns a string representing the instance.

        Keyword arguments:
        self -- the AlgorithmData instance
        """
        return 'RecCount:' + str(self.rec_count) + ', ' + \
             'LoopNDepend:' + str(self.loop_n_depend) + ", " + \
             'LoopNested:' + str(self.loop_nested) + ", " + \
             'LoopType:' + str(self.loop_type) + ", " + \
             'ProgTerminate:' + str(self.prog_terminate) + ", " + \
             'UsingNonScalar:' + str(self.using_non_scalar) + ", " + \
             'RepeatValues:' + str(self.repeat_values) + ", " + \
             'ReuseValues:' + str(self.reuse_values) + ", " + \
             'Complexity:' + str(self.complexity)
                 

class TrainData(AlgorithmData):
    """ Extended class for algorithm attributes, also containing the classification (training case). """

    classification = models.IntegerField(default=0)

    def initAttr(self, attr_list, classification):
        """ Initializes the algorithm attributes.

        Keyword arguments:
        self -- the AlgorithmData instance
        attr_list -- dictionary containing the names and values of the attributes for this instance
        """

        super().initAttr(attr_list)
        self.classification = classification

    def getValues(self):
        """ Returns the attributes of the instance as dictionary.

        Keyword arguments:
        self -- the AlgorithmData instance
        """

        attr_list = super().getValues()
        attr_list['Classification'] = self.classification
        return attr_list

    def __str__(self):
        """ Returns a string representing the instance.

        Keyword arguments:
        self -- the AlgorithmData instance
        """

        return super().__str__() + ', Classification:' + str(self.classification)


