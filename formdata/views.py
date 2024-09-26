from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


# Create your views here.

def show_form(request):
    '''Show the web page with the form.'''
    template_name = "formdata/show_form.html"

    return render(request, template_name)


def submit(request):
    template_name = 'formdata/confirmation.html'
    print(request)

    if request.POST:
        name = request.POST['name']
        favorite_color = request.POST['favorite_color']

        context = {
            'name': name,
            'favorite_color': favorite_color,
         }
        return render(request, template_name, context)
    ##return HttpResponse("NOPE") ok solution:shows a page that says NOPE


    # template_name = "formdata/show_form.html"
    # return render(request, template_name) ##goes back to the form, if mistakenly goes to that page(after submission)
    
    return redirect("show_form") #redirect to another url

