from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.ViewCategory.as_view()),
    path('menu-items', views.ViewItems.as_view()),
    path('menu-items/<int:pk>', views.ViewSingleItem.as_view()),
    path('cart/menu-items', views.ViewOrdersCart.as_view()),
    path('orders', views.ViewOrder.as_view()),
    path('orders/<int:pk>', views.ViewOneOrder.as_view()),
    path('groups/manager/users', views.ViewGroups.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'})),

    path('groups/delivery-crew/users', views.WorkersView.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'}))
]