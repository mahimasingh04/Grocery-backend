from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.db.models import Sum
from .models import Sale
from django.utils import timezone
from django.db import models 
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import Product
from rest_framework.decorators import action
from .serializers import ProductSerializer
from .permissions import IsStoreManager
from store.models import Product , Sale
from .serializers import SalesReportSerializer
from .models import PromoCode
from .serializers import PromoCodeSerializer
from rest_framework.permissions import IsAuthenticated


class ProductViewSet(viewsets.ModelViewSet):
    """
    Handles all product CRUD operations.
    Only store managers can add/edit/delete.
    All authenticated users can view.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStoreManager]

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    
   
    @action(detail=False, methods=['post'], url_path='add')
    def add_product(self, request):
        """
        POST /api/products/add/
        Only store managers can add products.
        """
        try:
            if getattr(request.user, 'role', None) != 'manager':
                raise PermissionDenied("Only store managers can add products.")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response(
                {"error": e.message_dict if hasattr(e, 'message_dict') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"error": "Unexpected error while adding product."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            if getattr(request.user, 'role', None) != 'manager':
                raise PermissionDenied("Only store managers can edit products.")
            partial = True
            return super().update(request, *args, partial=partial, **kwargs)
         
        except ObjectDoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
      
        except Exception as e:
        
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            if getattr(request.user, 'role', None) != 'manager':
                raise PermissionDenied("Only store managers can delete products.")
            return super().destroy(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"error": "Unexpected error while deleting the product."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


class SalesReportView(APIView):
    permission_classes = [IsStoreManager]

    def get(self, request):
        try:
            filter_type = request.query_params.get('filter')  # most_sold, least_sold, or category
            category = request.query_params.get('category')

            
            products = Product.objects.annotate(
                total_quantity_sold=Sum('sales__quantity')
            ).order_by('-total_quantity_sold')

            
            products = products.annotate(
                total_quantity_sold=Sum('sales__quantity')
            ).values('id', 'name', 'category', 'price', 'total_quantity_sold')

            
            if filter_type == 'category':
                if not category:
                    return Response(
                        {"error": "Category parameter is required for category filter."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                products = products.filter(category__iexact=category)

           
            elif filter_type == 'most_sold':
                products = products.order_by('-total_quantity_sold')
            elif filter_type == 'least_sold':
                products = products.order_by('total_quantity_sold')
            elif filter_type not in [None, 'most_sold', 'least_sold', 'category']:
                return Response(
                    {"error": "Invalid filter type. Use 'most_sold', 'least_sold', or 'category'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            for p in products:
                if p['total_quantity_sold'] is None:
                    p['total_quantity_sold'] = 0

            serializer = SalesReportSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromoCodeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
         if getattr(request.user, 'role', None) != 'manager':
            return Response(
                {"error": "Only managers can create promo codes."},
                status=status.HTTP_403_FORBIDDEN
            ) 
         serializer = PromoCodeSerializer(data=request.data)
         if serializer.is_valid():
            serializer.save()
            return Response({"message": "Promo code created successfully"}, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def get(self, request):
        promo_codes = PromoCode.objects.filter(active=True, expiry_date__gt=timezone.now())
        serializer = PromoCodeSerializer(promo_codes, many=True)
        return Response(serializer.data)


class ApplyPromoView(APIView):
   
    def post(self, request):
        code = request.data.get("code")
        try:
            promo = PromoCode.objects.get(code=code)
            if promo.is_valid():
                return Response({"discount_percent": promo.discount_percent}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Promo code expired or inactive"}, status=status.HTTP_400_BAD_REQUEST)
        except PromoCode.DoesNotExist:
            return Response({"error": "Invalid promo code"}, status=status.HTTP_404_NOT_FOUND)

class LowStockAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
      
        if getattr(request.user, 'role', None) != 'manager':
            return Response({"error": "Only managers can view low-stock alerts."}, status=status.HTTP_403_FORBIDDEN)
        
        low_stock_products = Product.objects.filter(stock__lte=models.F('low_stock_threshold'))
        if not low_stock_products.exists():
            return Response({"message": "All stocks are sufficient!"}, status=status.HTTP_200_OK)

        data = [{"product": p.name, "quantity": p.stock} for p in low_stock_products]
        return Response({"low_stock_alerts": data}, status=status.HTTP_200_OK)