from rest_framework import serializers
from .models import Category,MenuItem,Cart,Order,OrderItem
from django.contrib.auth.models import User
from decimal import Decimal


class SerialsOfCategory (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','slug']
        

class SerialsOfItems(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        
        
class SerialsOfCart(serializers.ModelSerializer):
    SessionOfUser = serializers.PrimaryKeyRelatedField(queryset = User.objects.all(),default = serializers.CurrentUserDefault())
    
    def checking(self,attrs):
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs
    
    
    class Meta:
        model = Cart
        fields = ['user','menuitem','unit_price','quantity','price']
        extra_kwargs = {'price': {'read_only' : True}}
        
        
class SerialsOfOrderedItems(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields=['order','menuitem','quantity','price']
        
        
class SerialsOfOrders(serializers.ModelSerializer):
    
    OrderedItem= SerialsOfOrderedItems(many=True,read_only=True,source='order')
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew','status', 'date', 'total', 'orderitem']
        
class SerialsOfCustomers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']