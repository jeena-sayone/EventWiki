from django.urls import path
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),

    path('signup',views.signup,name='signup'),
    path('eventsList',views.eventsList,name='eventsList'),
    path('addEvent',views.addEvent,name='addEvent'),
    path('updateEvent',views.updateEvent,name='updateEvent'),
    path('deleteEvent',views.deleteEvent,name='deleteEvent'),
    path('loadPaymentMethod',views.loadPaymentMethod,name='loadPaymentMethod'),
    path('createCheckoutSession',views.createCheckoutSession,name='createCheckoutSession'),
    path('payment-success/',views.paymentSuccess,name='payment-success'),
    path('payment-cancel/',views.paymentCancel,name='payment-cancel'),
    path('my_webhook_view',views.my_webhook_view,name='my_webhook_view')



]
