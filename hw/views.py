from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random

# Create your views here.

# def home(request):
#     '''function to respons /hw url'''
#     response_text  = "hello" 
#     #response text can be anything u want



#     return HttpResponse(response_text)

def home(request):
    template_name = "hw/home.html"
    quotes = ["A rose by any other name would smell as sweet.(shakespear)", 
               " Genius is one percent inspiration and ninety-nine percent perspiration.(thomas edison)",
               "If you are going through hell, keep going.(winston churchill)"]
    images = []
    #create a dictionary
    context = {
        'current_time': time.ctime(),
        'letter1' : "HI"
    }

    return render(request, template_name, context)
    

def about(request):
    template_name = "hw/about.html"

    #create a dictionary
    context = {
        'current_time': time.ctime(),
        'letter1' : chr(random.randint(65,90)), #random letter from a to z
    }

    return render(request, template_name, context)
