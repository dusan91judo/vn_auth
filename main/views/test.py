from rest_framework.response import Response
from rest_framework import viewsets, status


class TestViewSet(viewsets.ViewSet):
    def test(self, request):
        return Response({'dusan': 'pusan'})
