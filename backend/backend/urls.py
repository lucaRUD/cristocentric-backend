"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from accounts.views import ProdigiProductsAPIView,CreatePaymentView,CreateCheckoutSessionView,ArticleList,ArticleDetail,CreateArticle,ArticleUpdate,ArticleDelete,ArticleFileUploadView,EventCreateView,EventDetailView,EventFileUploadView,PublicEventListView,AddOrderDataAPIView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('products/<str:product_id>',ProdigiProductsAPIView.as_view()),
    path('create-payment/',CreatePaymentView.as_view(), name='create_payment'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('articles/', ArticleList.as_view()),
    path('articles/<int:pk>/', ArticleDetail.as_view()),
    path('create-article/', CreateArticle.as_view()),
    path('articles/<int:pk>/update/', ArticleUpdate.as_view()),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view()),
    path('upload-file/<int:article_id>/', ArticleFileUploadView.as_view()),
    path('event-upload-file/<int:event_id>/', EventFileUploadView.as_view()),
    path('events/', EventCreateView.as_view(), name='event-create'),
    path('events-public/', PublicEventListView.as_view(), name='event-create'),
    path('events/<int:event_id>/', EventDetailView.as_view(), name='event-detail'),
    path('addorders/',AddOrderDataAPIView.as_view(), name='add-order-data')

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)