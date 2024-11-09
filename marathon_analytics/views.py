from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Result
from django.db.models.query import QuerySet
import plotly
import plotly.graph_objs as go


# Create your views here.

class ResultsListView(ListView):
    '''view to display list of marathon results'''
    template_name = 'marathon_analytics/results.html'
    model = Result
    context_object_name = "results" #name to be used in html file
    paginate_by = 50 #limits number to show on page

    def get_queryset(self):
        qs = super().get_queryset()

        if 'city' in self.request.GET:
            city = self.request.GET['city']
            if city: #if blank
                qs = Result.objects.filter(city__icontains=city) 

        return qs

class ResultDetailView(DetailView):

    template_name = 'marathon_analytics/result_detail.html'
    model = Result
    context_object_name = 'r'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        r = context['r']
        x = [f'runners passed {r.first_name}',
             f'runners who passed {r.first_name}']
        
        y = [r.get_runner_passed(), r.get_runner_passed_by()]

        fig = go.Bar(x=x, y=y)
        graph_div = plotly.offline.plot({"data":[fig]}, auto_open=False, output_type = 'div'
                    )
        context['graph_div'] = graph_div

        #pie char for first half and second half
        x=['first half time', 'second half time']

        first_half_sec = r.time_half1.hour * 3600 + r.time_half1.minute * 60 + r.time_half1.second
        second_half_sec = r.time_half2.hour * 3600 + r.time_half2.minute * 60 + r.time_half2.second

        y=[first_half_sec, second_half_sec]

        fig = go.Pie(labels=x, values=y)
        pie_div = plotly.offline.plot({"data":[fig]}, auto_open=False, output_type = 'div'
                    )
        context['pie_div'] = pie_div

        return context




