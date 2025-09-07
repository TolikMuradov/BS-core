from django.contrib import admin
from .models import User, ProAuthorApplication, ProApplicationStatus
from django.utils.timezone import now

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "coins", "is_email_verified")
    search_fields = ("username", "email")


@admin.register(ProAuthorApplication)
class ProAuthorApplicationAdmin(admin.ModelAdmin):
    list_display = ("id","user","status","submitted_at","reviewed_at")
    list_filter  = ("status",)
    search_fields = ("user__username","user__email","national_id","first_name_legal","last_name_legal")
    actions = ["approve_selected","reject_selected"]

    def approve_selected(self, request, queryset):
        count = 0
        for app in queryset:
            app.status = ProApplicationStatus.APPROVED
            app.reviewed_at = now()
            app.reviewer = request.user
            app.save()
            # Kullanıcı rolünü PRO_AUTHOR yap
            u = app.user
            u.role = "PRO_AUTHOR"
            u.save(update_fields=["role"])
            count += 1
        self.message_user(request, f"{count} başvuru onaylandı.")
    approve_selected.short_description = "Approve selected applications (set user role to PRO_AUTHOR)"

    def reject_selected(self, request, queryset):
        updated = queryset.update(status=ProApplicationStatus.REJECTED, reviewed_at=now(), reviewer=request.user)
        self.message_user(request, f"{updated} başvuru reddedildi.")
    reject_selected.short_description = "Reject selected applications"