from django.urls import path
from .views import ConvertTxtAPIView

urlpatterns = [
    path('tolaz/<str:bahia>/', ConvertTxtAPIView.as_view(), name='convert-txt-laz'),
]