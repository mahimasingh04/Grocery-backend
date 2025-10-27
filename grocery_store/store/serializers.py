
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_by']
       

       
    
class SalesReportSerializer(serializers.ModelSerializer):
    total_quantity_sold = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'total_quantity_sold']