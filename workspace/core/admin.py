from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    Article, Campagne, Initiative, Inscription, Message, Parametre,
    PointCollecte, Signalement, User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("nom", "email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("nom", "email")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profil", {"fields": ("nom",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "nom", "password1", "password2")}),)


@admin.register(Campagne)
class CampagneAdmin(admin.ModelAdmin):
    list_display = ("titre", "date_debut", "lieu", "remplissage", "statut")
    list_filter = ("statut",)
    search_fields = ("titre", "lieu")

    def get_queryset(self, request):
        return super().get_queryset(request).with_n()

    @admin.display(description="Places")
    def remplissage(self, obj):
        return f"{obj.n} / {obj.capacite}"


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "campagne", "created_at")
    list_filter = ("campagne",)
    search_fields = ("user__nom", "user__email")


@admin.register(PointCollecte)
class PointCollecteAdmin(admin.ModelAdmin):
    list_display = ("nom", "quartier", "adresse", "horaires")
    list_filter = ("quartier",)
    search_fields = ("nom", "quartier", "adresse")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "created_at")
    list_filter = ("categorie",)
    search_fields = ("titre", "contenu")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "sujet", "traite", "created_at")
    list_filter = ("traite",)
    search_fields = ("nom", "email", "sujet", "message")
    actions = ["marquer_traite"]

    @admin.action(description="Marquer comme traité")
    def marquer_traite(self, request, queryset):
        queryset.update(traite=True)


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "extrait", "localisation", "statut", "created_at")
    list_display_links = ("id", "extrait")
    list_editable = ("statut",)
    list_filter = ("statut",)

    @admin.display(description="Description")
    def extrait(self, obj):
        return obj.description[:80]


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ("titre", "user", "statut", "created_at")
    list_editable = ("statut",)
    list_filter = ("statut",)


@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):
    list_display = ("cle", "valeur")
