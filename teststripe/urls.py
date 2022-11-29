from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'items', views.ItemViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('cart', views.cart, name='cart'),
    path('buy/<id>', views.buy, name='buy'),
    path('checkpromo/', views.checkpromo, name='checkpromo'),
    path('buyorder/', views.buyorder, name='buyorder'),
    path('checkcart/', views.checkcart, name='checkcart'),
    path('create-payment-intent/', views.create_intent, name='intent'),
    path('item/<id>', views.item, name='item'),
    path('addtocart/', views.add_to_cart, name='add_to_cart'),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]