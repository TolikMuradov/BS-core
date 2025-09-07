import os
import json
import requests
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
import jwt

User = get_user_model()


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"detail": "id_token required"}, status=400)

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        try:
            info = google_id_token.verify_oauth2_token(
                token, google_requests.Request(), client_id
            )
            # info contains 'sub'(google uid), 'email', 'email_verified', 'name', 'picture'
        except Exception:
            return Response({"detail": "Invalid Google token"}, status=401)

        email = info.get("email")
        if not email:
            return Response({"detail": "No email in token"}, status=400)

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": f"g_{info.get('sub')}",
                "display_name": info.get("name", ""),
                "is_email_verified": bool(info.get("email_verified")),
            },
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"


class AppleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get("id_token")
        if not id_token:
            return Response({"detail": "id_token required"}, status=400)

        try:
            # Get Apple's public keys (cached per-process; simplistic cache)
            jwks = requests.get(APPLE_KEYS_URL, timeout=5).json()
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header.get("kid")
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not key:
                return Response({"detail": "Apple key not found"}, status=401)

            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            payload = jwt.decode(
                id_token,
                key=public_key,
                algorithms=["RS256"],
                audience=os.getenv("APPLE_AUD"),  # your bundle id / Services ID
                issuer="https://appleid.apple.com",
            )
        except Exception:
            return Response({"detail": "Invalid Apple token"}, status=401)

        email = payload.get("email")
        sub = payload.get("sub")
        if not (email or sub):
            return Response({"detail": "Missing subject/email"}, status=400)

        username = f"a_{sub}"
        user, _ = User.objects.get_or_create(
            email=email or f"{username}@apple.local",
            defaults={
                "username": username,
                "is_email_verified": True,
            },
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })