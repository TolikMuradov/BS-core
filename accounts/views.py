from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ProAuthorApplicationSerializer
from .permissions import IsProAuthor
from .models import ProAuthorApplication

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class ProOnlyView(APIView):
    permission_classes = [IsProAuthor]
    def get(self, request):
        return Response({"ok": True, "role": request.user.role})


class ProApplyView(generics.CreateAPIView):
    """
    Kullanıcı kendi PRO başvurusunu oluşturur/günceller.
    Form-data (multipart) destekler: id_card_image, selfie_image, extra_doc
    """
    serializer_class = ProAuthorApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = []  # DRF default parsers (JSON + Form + MultiPart)

    def perform_create(self, serializer):
        serializer.save()  # create() içinde user bağlanıyor

class ProMyApplicationView(generics.RetrieveAPIView):
    """
    Kullanıcı yalnızca KENDİ başvurusunu görür.
    """
    serializer_class = ProAuthorApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = ProAuthorApplication.objects.get_or_create(user=self.request.user)
        return obj