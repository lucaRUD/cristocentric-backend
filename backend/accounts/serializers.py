from rest_framework import serializers,viewsets
from .models import CustomUser, Product
from rest_framework import routers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'bio', 'birth_date']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'colors', 'sizes', 'description', 'price', 'image']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = router.urls