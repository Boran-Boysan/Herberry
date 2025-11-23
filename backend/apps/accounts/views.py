from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import User, Address
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, AddressSerializer


@extend_schema(tags=['🔐 Authentication'])
class RegisterView(generics.CreateAPIView):
    """
    Kullanıcı Kaydı

    Yeni kullanıcı kaydı oluşturur ve authentication token döner.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['🔐 Authentication'])
class LoginView(generics.GenericAPIView):
    """
    Kullanıcı Girişi

    Email ve şifre ile giriş yapar, authentication token döner.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })


@extend_schema(tags=['👤 User Profile'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı Profili

    Giriş yapmış kullanıcının profil bilgilerini görüntüler ve günceller.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['📍 Addresses'])
class AddressListCreateView(generics.ListCreateAPIView):
    """
    Adres Listesi ve Ekleme

    Kullanıcının tüm adreslerini listeler ve yeni adres ekler.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['📍 Addresses'])
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Adres Detay, Güncelleme ve Silme

    Belirli bir adresi görüntüler, günceller veya siler.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)