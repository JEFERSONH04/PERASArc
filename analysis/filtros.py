# analysis/filters.py

import django_filters
from .models import AnalysisResult

class AnalysisResultFilter(django_filters.FilterSet):
    created_after  = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    status         = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    model          = django_filters.NumberFilter(field_name='model__id')
    dataset        = django_filters.NumberFilter(field_name='dataset__id')

    class Meta:
        model  = AnalysisResult
        fields = ['model','dataset','status','created_after','created_before']
