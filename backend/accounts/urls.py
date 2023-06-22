from django.db import router
from django.urls import include, path
from accounts.views import ProdigiOrdersAPIView,AddOrderDataAPIView,UpdateUserDataView,GetUserOrdersView,RegisterView, VerifyEmailView,LoginView,CancelOrderView,GetAuthStatusView,LogoutView,UserDataView,check_fields,SaveEventView, RemoveEventView,ProdigiOrderDetailsView,CancelOrderView

from .serializers import urlpatterns as api_urls



urlpatterns = [
    
    path('register/', RegisterView.as_view()),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view()),
    path('login/', LoginView.as_view()),
    path('check-fields/<str:email>/<str:username>/<str:phone_number>/', check_fields),
    path('logout/',LogoutView.as_view()),
    path('addorders/',AddOrderDataAPIView.as_view()),
    path('orders/',ProdigiOrdersAPIView.as_view()),
    path('orders/<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
    path('get-orders/', GetUserOrdersView.as_view(), name='get_user_orders'),
    path('get-auth-status/',GetAuthStatusView.as_view()),
    path('user-data/', UserDataView.as_view(), name='user-data'),
    path('update-user-data/', UpdateUserDataView.as_view()),
    path('save-event/', SaveEventView.as_view(), name='save_event'),
    path('remove-event/', RemoveEventView.as_view(), name='remove_event'),
    path('order-details/',ProdigiOrderDetailsView.as_view()),
    path('cancel-order/<int:order_id>/',CancelOrderView.as_view())
    
]

urlpatterns += api_urls