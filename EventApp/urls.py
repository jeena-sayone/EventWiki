from django.urls import path
from .import views

urlpatterns = [
    path('', views.index,name='index'),
    # path('login',views.login,name='login'),
    path('logout', views.logout, name='logout'),
    path('login', views.LoginClass.as_view(), name='login'),

<<<<<<< HEAD
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
=======
    path('signup', views.signup, name='signup'),
    path('events_list', views.events_list, name='events_list'),
    path('add_event', views.add_event, name='add_event'),
    path('edit-event/id=<int:key_id>', views.edit_event, name='edit_event'),
    path('update_event', views.update_event, name='update_event'),
    path('delete_event', views.delete_event, name='delete_event'),
    path('loadPaymentMethod', views.loadPaymentMethod, name='loadPaymentMethod'),
    path('createCheckoutSession', views.createCheckoutSession, name='createCheckoutSession'),
    path('payment-success/', views.paymentSuccess, name='payment-success'),
    path('payment-cancel/', views.paymentCancel, name='payment-cancel'),
    path('my_webhook_view', views.my_webhook_view, name='my_webhook_view')
>>>>>>> d207192cd6fc1fdd077052236cbf6786d7b73303



]
