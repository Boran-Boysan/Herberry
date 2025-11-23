from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers
from drf_spectacular.utils import extend_schema
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionCreateSerializer


@extend_schema(tags=['🔄 Subscriptions'])
class SubscriptionListView(generics.ListAPIView):
    """
    Abonelik Listesi

    Kullanıcının tüm aboneliklerini listeler.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


@extend_schema(tags=['🔄 Subscriptions'])
class SubscriptionCreateView(generics.CreateAPIView):
    """
    Yeni Abonelik Oluştur

    Haftalık sebze/meyve kutusu aboneliği oluşturur.

    **Abonelik Tipleri:**
    - `veg_box`: Sebze Kutusu
    - `fruit_box`: Meyve Kutusu
    - `custom_box`: Özel Kutu

    **Teslimat Günleri:**
    - 1: Pazartesi, 2: Salı, 3: Çarşamba, 4: Perşembe, 5: Cuma, 6: Cumartesi, 7: Pazar
    """
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        address = serializer.validated_data['address']
        if address.user != self.request.user:
            raise drf_serializers.ValidationError("Adres size ait değil")
        serializer.save(user=self.request.user)


@extend_schema(tags=['🔄 Subscriptions'])
class SubscriptionDetailView(generics.RetrieveAPIView):
    """
    Abonelik Detayı

    Belirli bir aboneliğin detay bilgilerini gösterir.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


@extend_schema(tags=['🔄 Subscriptions'])
class SubscriptionUpdateView(generics.UpdateAPIView):
    """
    Abonelik Güncelle

    Mevcut aboneliği günceller (adres, gün, tip değiştirme).
    """
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


@extend_schema(tags=['🔄 Subscriptions'])
class SubscriptionDeleteView(generics.DestroyAPIView):
    """
    Aboneliği İptal Et

    Aboneliği iptal eder (pasif yapar).
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'message': 'Abonelik iptal edildi'}, status=status.HTTP_200_OK)