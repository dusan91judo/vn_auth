from django.urls import path
from main.views.test import TestViewSet

urlpatterns = [
    path('test/', TestViewSet.as_view({'get': 'test'}), name='test')
]
