from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import SerialsOfCategory, SerialsOfItems,SerialsOfCart,SerialsOfOrderedItems,SerialsOfCustomers
from rest_framework.response import Response
from rest_framework import viewsets, status ,generics
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group,User



class ViewCategory(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = SerialsOfCategory
    
    def get_permissions(self):
        permissions = []
        if self.request.method !='GET':
            permissions = [IsAuthenticated]
            
        return [permission() for permission in permissions]
    
    
class ViewItems(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = SerialsOfItems
    fetch_data = ['category__title']
    order = ['price','inventory']
    
    def __str__(self):
        return f'{self.title}:{str(self.price)}'
    
    def permission_granting(self):
        permissions =[]
        if self.request.method !='GET':
            permissions [IsAuthenticated]
            
        return [permission() for permission in permissions]
    
    
class ViewSingleItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = SerialsOfItems
    
    def permission_granting(self):
        permissions = []
        if self.request.method !='GET':
            permissions = [IsAuthenticated]
            
        return [permission() for permission in permissions]
    
class ViewOrdersCart(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = SerialsOfCart
    permission_classes = [IsAuthenticated]
    
    def fetching(self):
        return Cart.objects.all().filter(user=self.request.user)
    
    def remove(self,request,*args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("Deleted Successfully")
    
    
class ViewOrder(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = SerialsOfOrderedItems
    permission_classes = [IsAuthenticated]
    
    def fetching(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.count()==0:
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Workers').exists():
            return Order.objects.all().filter(workers=self.request.user)
        else:
            return Order.objects.all()
        
    def create(self,request,*args,**kwargs):
        counter =Cart.objects.all().filter(user=self.request.user).count()
        if counter == 0:
            return Response({"No Items In the Cart"})
        
        
        data = request.data.copy()
        total = self.fetch_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        Serial = SerialsOfOrderedItems(data=data)
        if (Serial.is_valid()):
            order = Serial.save()
            items = Cart.objects.all().filter(user=self.request.user).all()
            
            for item in items.values():
                itemsOfOrder = OrderItem(order=order,menuId=item['menuId'],price=item['price'],quantity=item['quantity'],)
                itemsOfOrder.save()
                
                Cart.objects.all().filter(user=self.request.user).delete()
                
                fetched_data = Serial.data.copy()
                fetched_data['total']=total 
                return Response(Serial.data)
                
                
    def fetchPrice(self,user):
        total =0
        item = Cart.objects.all().filter(user=user).all()
        for item in item.values():
            total = total + item['price']
            
        return total
    
    
class ViewOneOrder(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = SerialsOfOrderedItems
    permission_classes = [IsAuthenticated]
    
    def Patch(self,request,*args,**kwargs):
        if self.request.user.groups.count()==0:
            return Response('Something Went Wrong')
        else:
            return super().update(request,*args,**kwargs)
        
        
class ViewGroups(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Manager')
        items = SerialsOfCustomers(users, many=True)
        return Response(items.data)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        return Response({"User Added"}, 200)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"User Deleted"}, 200)

class WorkersView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Workers')
        items = SerialsOfCustomers(users, many=True)
        return Response(items.data)

    def create(self, request):

        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, username=request.data['username'])
        work_agents = Group.objects.get(name="Workers")
        work_agents.user_set.add(user)
        return Response({"User Added to Workers"}, 200)

    def destroy(self, request):

        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        work_agents = Group.objects.get(name="Workers")
        work_agents.user_set.remove(user)
        return Response({"User Deleted"}, 200)