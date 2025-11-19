from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Subscription, SubscriptionItem
from .serializers import SubscriptionSerializer, SubscriptionCreateSerializer
from apps.accounts.models import Address


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionCreateView(generics.CreateAPIView):
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        address = serializer.validated_data['address']
        if address.user != self.request.user:
            raise serializers.ValidationError("Adres size ait degil")
        serializer.save(user=self.request.user)


class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionUpdateView(generics.UpdateAPIView):
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'message': 'Abonelik iptal edildi'}, status=status.HTTP_200_OK)