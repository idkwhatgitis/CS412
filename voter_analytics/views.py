# File: views.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/10/2024
# Description: showing details of voter, showing a list of voter, and graph view 


from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from django.db.models.query import QuerySet
from django.db.models import Count
import plotly
import plotly.graph_objs as go
from datetime import datetime


# Create your views here.

class VotersListView(ListView):
    '''view to display list of Voter results'''
    template_name = 'voter_analytics/voters.html'
    model = Voter
    context_object_name = "voters" #name to be used in html file
    paginate_by = 100 #limits number to show on page


    def get_queryset(self):
        '''filtering what the user asked for'''
        queryset = super().get_queryset()
        
        # Get query parameters from the request
        party = self.request.GET.get('party', '')
        min_birth_year = self.request.GET.get('min_birth_year', '')
        max_birth_year = self.request.GET.get('max_birth_year', '')
        score = self.request.GET.get('score', '')
        vote_2020s = self.request.GET.get('2020s', None)
        vote_2021t = self.request.GET.get('2021t', None)
        vote_2021p = self.request.GET.get('2021p', None)
        vote_2022g = self.request.GET.get('2022g', None)
        vote_2023t = self.request.GET.get('2023t', None)

        # Build filters based on the input values
        if party:
            queryset = queryset.filter(party=party)

        if min_birth_year:
            queryset = queryset.filter(dob__gte=f'{min_birth_year}-01-01')

        if max_birth_year:
            queryset = queryset.filter(dob__lte=f'{max_birth_year}-12-31')


        if score:
            queryset = queryset.filter(voter_score=score)

        # Filtering based on voting history
        if vote_2020s:
            queryset = queryset.filter(v20s=True)
        if vote_2021t:
            queryset = queryset.filter(v21t=True)
        if vote_2021p:
            queryset = queryset.filter(v21p=True)
        if vote_2022g:
            queryset = queryset.filter(v22g=True)
        if vote_2023t:
            queryset = queryset.filter(v23t=True)

        return queryset

class VoterDetailView(DetailView):
    '''detail page of the voter, inherting model Voter'''
    template_name = 'voter_analytics/voter_detail.html'
    model = Voter
    context_object_name = 'r'

    





class GraphDetailView(ListView):
    '''creating graphs based on our needs'''
    template_name = 'voter_analytics/graphs.html'
    model = Voter
    context_object_name = 'voters'

    
    def get_context_data(self, **kwargs):
        '''function to obtain data, and creating graph based on the data'''
        context = super().get_context_data(**kwargs)

        # Optional filtering by party affiliation and year of birth, and voter score, and voted in which vote
        min_birth_year = self.request.GET.get('min_birth_year', None)
        max_birth_year = self.request.GET.get('max_birth_year', None)
        score = self.request.GET.get('score', '')
        vote_2020s = self.request.GET.get('2020s', None)
        vote_2021t = self.request.GET.get('2021t', None)
        vote_2021p = self.request.GET.get('2021p', None)
        vote_2022g = self.request.GET.get('2022g', None)
        vote_2023t = self.request.GET.get('2023t', None)
        party = self.request.GET.get('party', None)

        # obtain everything and filter from this point
        #reuse code from previous class
        queryset = Voter.objects.all()

        if min_birth_year:
            queryset = queryset.filter(dob__gte=f'{min_birth_year}-01-01')
        if max_birth_year:
            queryset = queryset.filter(dob__lte=f'{max_birth_year}-12-31')
        if party:
            queryset = queryset.filter(party=party)
    
        if vote_2020s is not None:
            queryset = queryset.filter(v20s=vote_2020s)
        if vote_2021t is not None:
            queryset = queryset.filter(v21t=vote_2021t)
        if vote_2021p is not None:
            queryset = queryset.filter(v21p=vote_2021p)
        if vote_2022g is not None:
            queryset = queryset.filter(v22g=vote_2022g)
        if vote_2023t is not None:
            queryset = queryset.filter(v23t=vote_2023t)
        if score:
            queryset = queryset.filter(voter_score=score)

        # Histogram for Distribution by Year of Birth
        birth_years = queryset.values_list('dob', flat=True)
        birth_years = [datetime.strptime(dob, '%Y-%m-%d').year if dob else None for dob in birth_years]

        birth_year_counts = {}
        for year in birth_years:
            if year:
                birth_year_counts[year] = birth_year_counts.get(year, 0) + 1

        birth_year_labels = list(birth_year_counts.keys())
        birth_year_values = list(birth_year_counts.values())

        birth_year_histogram = go.Bar(x=birth_year_labels, y=birth_year_values, name="Voter Distribution by Year of Birth")
        birth_year_histogram_div = plotly.offline.plot({"data": [birth_year_histogram]}, auto_open=False, output_type='div')
        context['birth_year_histogram'] = birth_year_histogram_div

        # 2. Pie chart for Distribution by Party Affiliation
        party_distribution = queryset.values('party').annotate(count=Count('party'))
        labels = [entry['party'] for entry in party_distribution]
        values = [entry['count'] for entry in party_distribution]

        party_pie_chart = go.Pie(labels=labels, values=values, title="Voters by Party Affiliation")
        party_pie_chart_div = plotly.offline.plot({"data": [party_pie_chart]}, auto_open=False, output_type='div')
        context['party_pie_chart'] = party_pie_chart_div

        # 3. Histogram for Voter Participation in Elections
        election_fields = ['v20s', 'v21t', 'v21p', 'v22g', 'v23t']
        election_counts = []
        for field in election_fields:
            election_counts.append(queryset.filter(**{field: True}).count())

        election_histogram = go.Bar(x=['v20s', 'v21t', 'v21p', 'v22g', 'v23t'], y=election_counts, name="Voter Participation")
        election_histogram_div = plotly.offline.plot({"data": [election_histogram]}, auto_open=False, output_type='div')
        context['election_histogram'] = election_histogram_div

        # Pass filtered queryset to template as 'voters' context object
        context['voters'] = queryset
        return context
