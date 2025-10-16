from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Subscription, SubscriptionItem
from .serializers import (
    SubscriptionSerializer,
    SubscriptionListSerializer,
    SubscriptionCreateSerializer,
    SubscriptionUpdateSerializer,
    SubscriptionItemSerializer,
    SubscriptionItemCreateSerializer
)
from accounts.models import Address


class SubscriptionListView(generics.ListAPIView):
    """Kullanıcının tüm abonelikleri"""
    serializer_class = SubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-created_at')


class SubscriptionCreateView(generics.CreateAPIView):
    """Yeni abonelik oluştur"""
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Adresin kullanıcıya ait olduğunu kontrol et
        address = serializer.validated_data.get('address')
        if address.user != self.request.user:
            raise serializers.ValidationError("Seçilen adres size ait değil.")

        serializer.save(user=self.request.user)


class SubscriptionDetailView(generics.RetrieveAPIView):
    """Abonelik detayı"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionUpdateView(generics.UpdateAPIView):
    """Abonelik güncelle"""
    serializer_class = SubscriptionUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Adres değişiyorsa, kullanıcıya ait olduğunu kontrol et
        if 'address' in request.data:
            address_id = request.data['address']
            try:
                address = Address.objects.get(id=address_id, user=request.user)
            except Address.DoesNotExist:
                return Response(
                    {'error': 'Seçilen adres size ait değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Detaylı response için SubscriptionSerializer kullan
        response_serializer = SubscriptionSerializer(instance)
        return Response(response_serializer.data)


class SubscriptionDeleteView(generics.DestroyAPIView):
    """Abonelik sil (is_active=False)"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Abonelik başarıyla iptal edildi.'},
            status=status.HTTP_200_OK
        )


class SubscriptionActivateView(APIView):
    """Aboneliği yeniden aktifleştir"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            subscription = Subscription.objects.get(id=id, user=request.user)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Abonelik bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

        subscription.is_active = True
        subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


# Abonelik Ürün İşlemleri

class SubscriptionItemListView(generics.ListAPIView):
    """Abonelikteki ürünler"""
    serializer_class = SubscriptionItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        subscription_id = self.kwargs['subscription_id']
        # Aboneliğin kullanıcıya ait olduğunu kontrol et
        subscription = get_object_or_404(
            Subscription,
            id=subscription_id,
            user=self.request.user
        )
        return SubscriptionItem.objects.filter(subscription=subscription)


class SubscriptionItemAddView(generics.CreateAPIView):
    """Aboneliğe ürün ekle"""
    serializer_class = SubscriptionItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, subscription_id):
        # Aboneliğin kullanıcıya ait olduğunu kontrol et
        subscription = get_object_or_404(
            Subscription,
            id=subscription_id,
            user=request.user
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Aynı ürün zaten var mı kontrol et
        sku = serializer.validated_data['sku']
        existing_item = SubscriptionItem.objects.filter(
            subscription=subscription,
            sku=sku
        ).first()

        if existing_item:
            # Mevcut ürünün miktarını artır
            existing_item.qty += serializer.validated_data['qty']
            existing_item.save()
            response_serializer = SubscriptionItemSerializer(existing_item)
            return Response(response_serializer.data)
        else:
            # Yeni ürün ekle
            item = serializer.save(subscription=subscription)
            response_serializer = SubscriptionItemSerializer(item)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionItemUpdateView(generics.UpdateAPIView):
    """Abonelikteki ürün miktarını güncelle"""
    serializer_class = SubscriptionItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        subscription_id = self.kwargs['subscription_id']
        return SubscriptionItem.objects.filter(
            subscription_id=subscription_id,
            subscription__user=self.request.user
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = SubscriptionItemSerializer(instance)
        return Response(response_serializer.data)


class SubscriptionItemDeleteView(generics.DestroyAPIView):
    """Abonelikten ürün çıkar"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        subscription_id = self.kwargs['subscription_id']
        return SubscriptionItem.objects.filter(
            subscription_id=subscription_id,
            subscription__user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {'message': 'Ürün abonelikten çıkarıldı.'},
            status=status.HTTP_200_OK
        )