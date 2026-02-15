from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstallmentPlanViewSet, InstallmentPaymentViewSet

router = DefaultRouter()
router.register(r'plans', InstallmentPlanViewSet, basename='installment-plan')
router.register(r'payments', InstallmentPaymentViewSet, basename='installment-payment')

urlpatterns = router.urls
