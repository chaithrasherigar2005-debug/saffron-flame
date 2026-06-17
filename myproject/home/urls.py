from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('reservation/', views.reservation, name='reservation'),
    path('seat-selection/', views.seat_selection, name='seat_selection'),
    path('menu/', views.menu, name='menu'),
    path(
        'add-to-cart/<int:item_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/',
        views.cart,
        name='cart'
    ),
    path('increase/<int:cart_id>/', views.increase_quantity),
    path('decrease/<int:cart_id>/', views.decrease_quantity),
    path('delete-cart/<int:cart_id>/', views.delete_cart),
    path('receipt/', views.receipt, name='receipt'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('delivery/', views.delivery, name='delivery'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('dining-option/', views.dining_option, name='dining_option'),
    path('dine-in/', views.dine_in, name='dine_in'),
    path('contact/', views.contact, name='contact'),
    path('payment/', views.payment, name='payment'),
    path('pay-restaurant/',views.pay_restaurant,name='pay_restaurant'),
    path('my-orders/',views.my_orders,name='my_orders'),
    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('cash-on-delivery/',views.cash_on_delivery,name='cash_on_delivery'),
]