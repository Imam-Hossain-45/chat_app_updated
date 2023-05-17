from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('api-token-auth/', views.token_obtain_pair, name='login_token'),
]
