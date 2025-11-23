from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


@extend_schema(tags=['📂 Categories'])
class CategoryListView(generics.ListAPIView):
    """
    Kategori Listesi

    Tüm ürün kategorilerini listeler.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['🥬 Products'],
    parameters=[
        OpenApiParameter(name='category', type=OpenApiTypes.INT, description='Kategori ID'),
        OpenApiParameter(name='is_organic', type=OpenApiTypes.BOOL, description='Organik ürünler'),
        OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Ürün adı veya açıklamasında ara'),
        OpenApiParameter(name='ordering', type=OpenApiTypes.STR,
                         description='Sıralama (price_cents, -price_cents, created_at)'),
    ]
)
class ProductListView(generics.ListAPIView):
    """
    Ürün Listesi

    Tüm aktif ürünleri listeler. Filtreleme, arama ve sıralama yapılabilir.
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_organic']
    search_fields = ['name', 'description']
    ordering_fields = ['price_cents', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


@extend_schema(tags=['💰 Discounts'])
class DiscountedProductsView(generics.ListAPIView):
    """
    İndirimli Ürünler

    Aktif indirimi olan ürünleri en yüksek indirimden başlayarak listeler.
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            discount_active=True,
            discount_percentage__gt=0
        ).order_by('-discount_percentage')


@extend_schema(tags=['🥬 Products'])
class ProductDetailView(generics.RetrieveAPIView):
    """
    Ürün Detayı

    Belirli bir ürünün detay bilgilerini gösterir.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


@extend_schema(tags=['👨‍💼 Admin - Products'])
class ProductCreateView(generics.CreateAPIView):
    """
    Yeni Ürün Ekle (Admin)

    Yeni ürün oluşturur. Sadece admin kullanıcılar erişebilir.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


@extend_schema(tags=['👨‍💼 Admin - Products'])
class ProductUpdateView(generics.UpdateAPIView):
    """
    Ürün Güncelle (Admin)

    Mevcut ürünü günceller. Sadece admin kullanıcılar erişebilir.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


@extend_schema(tags=['👨‍💼 Admin - Products'])
class ProductDeleteView(generics.DestroyAPIView):
    """
    Ürün Sil (Admin)

    Ürünü siler. Sadece admin kullanıcılar erişebilir.
    """
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'