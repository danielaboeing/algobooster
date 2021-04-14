import pandas
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import pickle
from ab_ui.models import TrainData

class Agent():
	""" Class for the machine learning agent. """
    
	def __init__(self, base_dir):
		""" Initializes the machine learning agent.

		Keyword arguments:
		self -- the Agent instance
		base_dir -- the base directory to put the machine learning directory in
		"""
		self.__prefix = base_dir + "ml/"
		self.__trainFile = self.prefix + "train.data" # containing default training data

		# resources for the model
		self.__modelFile = self.prefix + "model.obj"
		self.__model = None

		# resources for the standard scaler
		self.__stdscFile = self.prefix + "stdsc.obj"
		self.__stdsc = None

		# load model and standard scaler if possible; if not, do initializing training
		try:
			opModFile = open(self.modelFile, "rb")
			readModel = pickle.load(opModFile)
			opStdscFile = open(self.stdscFile, "rb")
			readStdsc = pickle.load(opStdscFile)
		except IOError as ioe:
			print("Model or scaler could not be loaded:", ioe)
			self.init_train()
		else:
			if not(readModel is None):
				self.model = readModel
			if not(readStdsc is None):
				self.stdsc = readStdsc
			try:
				opModFile.close()
				opStdscFile.close()
			except IOError as ioe:
				print("Model or scaler file could not be closed:", ioe)
	

	def init_train(self):
		""" Do first initializing training.
	
		Keyword arguments:
		self -- the Agent instance
		"""

		# Clean database and objects from old training data
		TrainData.objects.all().delete()
		for obj in TrainData.objects.all():
			del obj
		
		# Read (new) training data from file
		dataset = pandas.read_csv(self.trainFile, names=None, encoding='utf-8', engine='c')

		train_data = dataset.values

		attr_list = {} 
		for row in train_data:
			attr_list['RecCount'] = row[0]
			attr_list['LoopNDepend'] = row[1]
			attr_list['LoopNested'] = row[2]
			attr_list['LoopType'] = row[3]
			attr_list['ProgTerminate'] = row[4]
			attr_list['UsingNonScalar'] = row[5]
			attr_list['RepeatValues'] = row[6]
			attr_list['ReuseValues'] = row[7]
			attr_list['Complexity'] = row[8]

			# Save new train data			
			newObj = TrainData()
			newObj.initAttr(attr_list, row[9])
			newObj.save()
		
		# Do training
		self.train()


	def train(self, attr_list=None, classification=None, show_outputs=False):
		""" Trains the machine learning agent. If applicable, 
		adds new training set to existing, chooses the best
		(new) ml classifier and trains this one.

		Keyword arguments:
		self -- the Agent instance
		attr_list -- list of extracted attributes of the training data (default None)
		classification -- given classification of the data to train with (default None)
		show_outputs -- if set to True, the training will show the output of different steps in the ml training process (default False)
		"""
			
		# Add newest training data if existent
		if classification != None and attr_list != None:
			newObj = TrainData()
			newObj.initAttr(attr_list, classification)
			newObj.save()

		# Get all training data
		allObjVals = []
		for obj in TrainData.objects.all():
			allObjVals.append(obj.getValues().values())

		dataset = pandas.DataFrame(allObjVals)

		# Split into validation and test set
		vals = dataset.values
		X = vals[:,0:9] # takes data
		y = vals[:,9] # takes classification

		X_train_pre, X_test_pre, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3)

		# Train StandardScaler
		stdsc = StandardScaler()
		X_train = stdsc.fit_transform(X_train_pre)
		self.stdsc = stdsc

		# Use StandardScaler for validation data
		X_test = stdsc.transform(X_test_pre)

	
		# List possible models to choose best from
		models = []
		#models.append(('KSVM', SVC(kernel="rbf", random_state=0, gamma=0.10, probability=True))) # probability=True needed to get probability in output 
		models.append(('CART', DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0)))
		#models.append(('KNN', KNeighborsClassifier(n_neighbors=4, p=2, metric='minkowski'))) # p=2 is Euclidian distance
		#models.append(('NB', GaussianNB()))

		# Not fitting models
		# models.append(('LR', LogisticRegression()))
		# models.append(('SVM', SVC(kernel="linear", probability=True))) # probability=True needed to get probability in output 

		# Evaluate each of the possible models
		results = []
		names = []
		max_acc = 0
		for name, model in models:
			# Stratified cross validation
			kfold = model_selection.StratifiedKFold(n_splits=3)#, random_state=1)
			cv_results = model_selection.cross_val_score(estimator=model, X=X_train, y=y_train, cv=kfold, scoring='accuracy', n_jobs=1)
			results.append(cv_results)
			names.append(name)
			if show_outputs:
				msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
				print(msg)

			# choose best model
			if cv_results.mean() > max_acc: 
				max_acc = cv_results.mean()
				self.model = model


		# Train best model
		self.model.fit(X_train, y_train)
		
		# Show validation results
		if show_outputs:
			print(X_test)
			prediction = self.model.predict(X_test)
			self.showTest(y_test, prediction)

		# Save model; Note: protocol 4 is latest and most efficient pickle protocol, python>=3.4
		try:
			opFile = open(self.modelFile, "wb")
			pickle.dump(self.model, opFile, protocol=4)
			opFile.close()
		except IOError as ioe:
			error_msg = "Model could not be saved"
			print(error_msg, ":", ioe)
			return error_msg

		# Save standard scaler; also using pickle protocol 4
		try:
			opFile = open(self.stdscFile, "wb")
			pickle.dump(self.stdsc, opFile, protocol=4)
			opFile.close()
		except IOError as ioe:
			error_msg = "Scaler could not be saved"
			print(error_msg, ":", ioe)
			return error_msg

		# Show visualization
		if show_outputs:
			self.visualizeData(dataset, results, names)

		return "Training was successful."
		
	def showTest(self, y, prediction):
		""" Method to output validation information.

		Keyword arguments:
		self -- the Agent instance
		y -- the actual class
		prediction -- the predicted class
		"""		
		print(accuracy_score(y, prediction))
		print(confusion_matrix(y, prediction))
		print(classification_report(y, prediction))

	def visualizeData(self, dataset, pred_results, model_names):
		""" Visualize the input and prediction data of the machine learning system.

		Keyword arguments:
		self -- the Agent instance
		dataset -- the pandas DataFrame containing the attribute data
		pred_results -- the prediction results of the different models
		model_names -- the name of the used models in same order as the pred_results
		"""

		# Histogram of the input dataset
		dataset.hist()

		# Model comparision
		fig = plt.figure()
		fig.suptitle('Models with their Precision')
		ax = fig.add_subplot(111)
		plt.boxplot(pred_results)
		ax.set_xticklabels(model_names)

		# Show visualization
		plt.show()

	def predict(self, predObj):
		""" Prediction method for a new object.

		Keyword arguments:
		self -- the Agent instance
		predObj -- the AlgorithmData object instance to predict the class for
		"""

		# Get the extracted attributes of the object
		vals = list(predObj.getValues().values())
		X_pre = [vals[0:9]]
		
		# Use trained StandardScaler to standardize data
		X = self.stdsc.transform(X_pre)

		# Get class prediction and probability
		prediction = self.model.predict(X)[0]
		probability = self.model.predict_proba(X)[0][int(prediction)] * 100

		# Delete prediction object from database
		predObj.delete()
		
		return {'classification': prediction, 'probability': probability }

	# Class helper methods

	def getPrefix(self):
		""" Returns the path prefix.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__prefix

	def getModelFile(self):
		""" Returns the model file name and path.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__modelFile
	
	def getModel(self):
		""" Returns the model object.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__model

	def getTrainFile(self):
		""" Returns the train file name and path.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__trainFile

	def getStdscFile(self):
		""" Returns the standard scaler file name and path.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__stdscFile

	def getStdsc(self):
		""" Returns the standard scaler object.

		Keyword arguments:
		self -- the Agent instance
		"""
		return self.__stdsc

	def setModel(self, other):
		""" Sets the model.

		Keyword arguments:
		self -- the Agent instance
		other -- the new value for the model object
		"""
		self.__model = other

	def setStdsc(self, other):
		""" Sets the standard scaler.

		Keyword arguments:
		self -- the Agent instance
		other -- the new value for the standard scaler object
		"""
		self.__stdsc = other

	prefix = property(getPrefix)
	trainFile = property(getTrainFile)
	modelFile = property(getModelFile)
	model = property(getModel, setModel)
	stdscFile = property(getStdscFile)
	stdsc = property(getStdsc, setStdsc)

