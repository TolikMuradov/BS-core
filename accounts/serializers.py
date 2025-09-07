from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ProAuthorApplication, ProApplicationStatus


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "avatar", "bio",
            "role", "coins", "is_email_verified"
        )
        read_only_fields = ("id", "role", "coins", "is_email_verified")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data



class ProAuthorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProAuthorApplication
        # Kullanıcıya gereksiz süreç alanları yazdırmıyoruz
        read_only_fields = ("status","submitted_at","reviewed_at","reviewer")
        fields = (
            "first_name_legal","last_name_legal","national_id","phone",
            "address_line","city","province","postal_code","country",
            "id_card_image","selfie_image","extra_doc",
            "status","submitted_at","reviewed_at",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        # Tekil (OneToOne) olduğu için var ise update gibi davranabiliriz
        instance, created = ProAuthorApplication.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return instance