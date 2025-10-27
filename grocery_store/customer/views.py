from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count
from django.db import transaction
from .models import Cart, CartItem, Wishlist, Order, OrderItem, WishlistItem
from store.models import Product, Sale
from .serializers import CartSerializer, WishlistSerializer, OrderSerializer, ProductSerializer
from django.utils import timezone


class BrowseProductsView(APIView):
    """
    Allows customers to browse available products."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
       try:   
        filter_type = request.query_params.get('filter', None)
        if filter_type == 'category':
            category = request.query_params.get('category', None)
            products = Product.objects.filter(category=category, stock__gt=0)

        elif filter_type == 'price_range':
            min_price = request.query_params.get('min_price', 0)
            max_price = request.query_params.get('max_price', 10000)
            products = Product.objects.filter(price__gte=min_price, price__lte=max_price, stock__gt=0)

        elif filter_type == 'most popular':
            products = Product.objects.annotate(total_sold=Count('sales')).order_by('-total_sold')

        else:

            products = Product.objects.filter(stock__gt=0)

        serializer  = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
       except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddOrRemoveFromCart(APIView):
    """
    Allows customers to add or remove products from their cart."""

    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

       
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return Response({'error': 'Product not available in requested quantity.'},
                            status=status.HTTP_400_BAD_REQUEST)
                            
                            
        cart = self.get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save() 

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        product_id = request.data.get('product_id')

        cart = self.get_cart(request.user)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id= product_id)
            cart_item.delete()

        except CartItem.DoesNotExist:
            return Response({'error': 'Item not in cart'}, status=status.HTTP_400_BAD_REQUEST)


        return Response({"message": "Removed from cart"}, status=status.HTTP_200_OK)




class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def post(self, request):
        try:
            with transaction.atomic():  # ✅ Start an atomic transaction block
                cart = self.get_cart(request.user)
                cart_items = CartItem.objects.filter(cart=cart)

                if not cart_items.exists():
                    return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

                total_price = 0
                order = Order.objects.create(user=request.user, total_price=0)

                for item in cart_items:
                    product = item.product

                    if product.stock < item.quantity:
                        raise ValueError(f"Product {product.name} not available in requested quantity.")

                    product.stock -= item.quantity
                    product.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.price * item.quantity
                    )

                    Sale.objects.create(
                        product=item.product,
                        quantity=item.quantity,
                        date=timezone.now()
                    )

                    total_price += item.quantity * product.price

                order.total_price = total_price
                order.save()
                cart_items.delete()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"error": "One of the products in your cart no longer exists."},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": "An unexpected error occurred during checkout.",
                             "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class WishListView(APIView):
    """
    Allows customers to add items to their wishlist and view it.
    """
    permission_classes =[IsAuthenticated]

    def get_wishlist(self, user):

        wishlist, _ = Wishlist.objects.get_or_create(user=user)
        return wishlist
    
    def get(self,request):
        wishlist = self.get_wishlist(request.user)
        serializer =WishlistSerializer(wishlist)
        return Response(serializer.data, status= status.HTTP_200_OK)
    
    def post(self, request):
        product_id= request.data.get('product_id')
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id= product_id)
            wishlist = self.get_wishlist(request.user)
           
            if WishlistItem.objects.filter(id=product_id).exists():
                return Response({}, status=status.HTTP_409_CONFLICT)
            
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotxist:
            return Response({'error': 'Product not founc'}, status = status.HTTP_404_NOT_FOUND)


        except Exception as e:
            return Response({'error': 'An error occurred while adding to wishlist', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self,request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist = self.get_wishlist(request.user)
            item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            item.delete()

            return Response({'message': 'Item removed from wishlist'}, status=status.HTTP_200_OK)
        
        except WishlistItem.DoesNotExist:
            return Response({'error': 'Item not found in wishlist'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error':'An error occurred while removing from wishlist', 'details': str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)


    

