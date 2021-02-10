from django.urls import path, include

urlpatterns = [
    path('/', include('main.routes.session')),
    path('api/v1/', include('main.routes.api'))
]
