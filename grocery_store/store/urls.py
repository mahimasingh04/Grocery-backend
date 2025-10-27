from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SalesReportView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
urlpatterns = [
    path('reports/', SalesReportView.as_view(), name='salesreport'),
]

urlpatterns += router.urls

