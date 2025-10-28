from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LowStockAlertView, ProductViewSet, SalesReportView , PromoCodeView, ApplyPromoView



router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
urlpatterns = [
    path('reports/', SalesReportView.as_view(), name='salesreport'),
     path('promocode/', PromoCodeView.as_view(), name='promo'),
    path('promocode/apply/', ApplyPromoView.as_view(), name='apply-promo'),
    path('low-stock-alert/', LowStockAlertView.as_view(), name='low-stock-alert'),
]

urlpatterns += router.urls

