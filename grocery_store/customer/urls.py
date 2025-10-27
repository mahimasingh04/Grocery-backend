# customer/urls.py
from django.urls import path
from .views import AddOrRemoveFromCart, CheckoutView, WishListView, BrowseProductsView

urlpatterns = [
    path('cart/', AddOrRemoveFromCart.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('browseProducts/', BrowseProductsView.as_view(), name='browse_products')
]
