from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OnlinePaymentViewSet, stripe_webhook

router = DefaultRouter()
router.register(r'', OnlinePaymentViewSet, basename='online-payment')

urlpatterns = [
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
] + router.urls
