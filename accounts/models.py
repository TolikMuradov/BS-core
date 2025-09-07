from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Roles(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    PRO_AUTHOR = "PRO_AUTHOR", "Pro Author"


class User(AbstractUser):
    # username, password come from AbstractUser
    email = models.EmailField(unique=True, blank=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.NORMAL)
    coins = models.PositiveIntegerField(default=0)  # virtual currency wallet
    is_email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username or self.email



class ProApplicationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

def pro_doc_upload_path(instance, filename):
    return f"pro_apps/{instance.user_id}/{filename}"

class ProAuthorApplication(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pro_application")
    # Kimlik & iletişim bilgileri
    first_name_legal = models.CharField(max_length=120)
    last_name_legal  = models.CharField(max_length=120)
    national_id = models.CharField(max_length=50)  # Thailand ID No.
    phone = models.CharField(max_length=50, blank=True)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=120, blank=True)
    province = models.CharField(max_length=120, blank=True)   # Thailand province
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=80, default="Thailand")

    # Belgeler
    id_card_image = models.ImageField(upload_to=pro_doc_upload_path)       # Kimlik foto
    selfie_image  = models.ImageField(upload_to=pro_doc_upload_path)       # Vesikalık/selfie
    extra_doc     = models.FileField(upload_to=pro_doc_upload_path, blank=True, null=True)  # opsiyonel PDF/JPG

    # Süreç
    status = models.CharField(max_length=20, choices=ProApplicationStatus.choices, default=ProApplicationStatus.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(blank=True, null=True)
    reviewer     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviewed_pro_apps")
    review_note  = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pro Author Application"
        verbose_name_plural = "Pro Author Applications"

    def __str__(self):
        return f"ProApp<{self.user_id}> {self.status}"