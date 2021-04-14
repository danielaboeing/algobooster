from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, RequestContext
from django import forms
from ab_ui.ab_main import ab_controller as main

def index(request):
	""" View function for the index page. """
	return render(request, 'ab_ui/index.html')

def about(request):
	""" View function for the about page. """
	return render(request, 'ab_ui/about.html')

def imprint(request):
	""" View function for the imprint page. """
	return render(request, 'ab_ui/imprint.html')

def disclaimer(request):
	""" View function for the disclaimer page. """
	return render(request, 'ab_ui/disclaimer.html')

def algobooster(request):
	""" View function for the 'Use Algobooster' page. (GET) """
	return render(request, 'ab_ui/algobooster.html')

def training(request):
	""" View function for the 'Train Algobooster' page. (GET) """
	return render(request, "ab_ui/training.html")
 
def train(request):
	""" View function for submitting code and classification to the 'Train Algobooster' page. (POST) """
	# Read the input pseudocode
	code = request.POST.get('code')

	# Read the classification
	try:
		classification = str(request.POST.get("classification"))
	except TypeError:
		context = {
			'result': "Error while reading classification."
		}
		return render(request, "ab_ui/training.html", context)
		

	# Train machine learning system with the code and classification
	result = main.trainAB(code, classification)

	context = {
		'result': result,
		'input': code,
		'classification': classification
	}
	return render(request, "ab_ui/training.html", context)

def submit(request):
	""" View function for submitting code to the 'Use Algobooster' page. (POST) """
	# Read the input pseudocode
	code = request.POST.get('code')


	# Method to prepare Python for html
	def prepare_html(pre_string):
		pre_string = pre_string.replace('\n', "<br />")
		pre_string = pre_string.replace('\t', "&nbsp;&nbsp;&nbsp;&nbsp;")
		return pre_string

	# Check submit type
	subType = request.POST.get('submitType')

	# forward the code to Algobooster
	if subType == "parse_and_class":
		ab_result = main.startAB(code) 
	else:
		ab_result = main.startAB(code, True)

	context = {
		'code': prepare_html(ab_result.get('code')),
		'complexity': prepare_html(ab_result.get('complexity')),
		'classification': prepare_html(ab_result.get('classification')),
		'probability': prepare_html(ab_result.get('probability')),
		'tips': prepare_html(ab_result.get('tips')),
		'input': code
	}
	
	return render(request, 'ab_ui/algobooster.html', context)
