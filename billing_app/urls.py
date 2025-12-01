from django.urls import path
from . import views


urlpatterns = [
path('', views.billing_page, name='billing_page'),
path('generate/', views.generate_bill, name='generate_bill'),
path('invoice/<int:bill_id>/', views.invoice_view, name='invoice_view'),
path('history/', views.customer_history, name='customer_history'),
]