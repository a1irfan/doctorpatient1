from django.urls import path
from .views import *

urlpatterns = [
    # your existing URL patterns
    path('create-subscription-product/', CreateSubscriptionProductView),
    path('create-customer-subscription/', CreateCustomerSubscription , name="create-subscription"),
    path('checkout/', checkout_session, name='checkout'),
]
