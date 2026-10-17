from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Count

QUARTIERS = [
    ("Kanadi", "Kanadi"),
    ("Grand marché", "Grand marché"),
    ("Yelwa", "Yelwa"),
]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("L'e-mail est obligatoire.")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Utilisateur identifié par e-mail (table `users` du projet PHP).
    is_staff = ancien rôle « admin » ; is_active = ancien champ « actif »."""

    username = None
    first_name = None
    last_name = None
    nom = models.CharField("Nom", max_length=100)
    email = models.EmailField("E-mail", max_length=150, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom"]
    objects = UserManager()

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def get_full_name(self):
        return self.nom

    def get_short_name(self):
        return self.nom

    def __str__(self):
        return self.nom or self.email


class CampagneQuerySet(models.QuerySet):
    def with_n(self):
        return self.annotate(n=Count("inscriptions"))


class Campagne(models.Model):
    class Statut(models.TextChoices):
        OUVERTE = "ouverte", "Ouverte"
        FERMEE = "fermee", "Fermée"

    titre = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    lieu = models.CharField(max_length=150, blank=True, choices=QUARTIERS)
    date_debut = models.DateTimeField("Date et heure")
    capacite = models.PositiveIntegerField("Capacité maximale", default=20)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.OUVERTE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CampagneQuerySet.as_manager()

    class Meta:
        ordering = ["-date_debut"]

    def __str__(self):
        return self.titre

    @property
    def inscrits(self):
        return self.n if hasattr(self, "n") else self.inscriptions.count()

    @property
    def pct(self):
        return min(100, round(self.inscrits / max(1, self.capacite) * 100))

    @property
    def complet(self):
        return self.inscrits >= self.capacite or self.statut != self.Statut.OUVERTE


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscriptions")
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name="inscriptions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        constraints = [models.UniqueConstraint(fields=["user", "campagne"], name="inscription_unique")]

    def __str__(self):
        return f"{self.user} → {self.campagne}"


class PointCollecte(models.Model):
    nom = models.CharField(max_length=150)
    quartier = models.CharField(max_length=100, blank=True, choices=QUARTIERS)
    adresse = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    horaires = models.CharField("Horaires (si connus)", max_length=150, blank=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "point de collecte"
        verbose_name_plural = "points de collecte"

    def __str__(self):
        return self.nom


class Article(models.Model):
    class Categorie(models.TextChoices):
        ACTUALITE = "actualite", "Actualité"
        CONSEIL = "conseil", "Conseil"
        ENVIRONNEMENT = "environnement", "Environnement"
        RECYCLAGE = "recyclage", "Recyclage"

    titre = models.CharField(max_length=200)
    categorie = models.CharField("Catégorie", max_length=20, choices=Categorie.choices)
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.titre


class Message(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    sujet = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    traite = models.BooleanField("Traité", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.nom} – {self.sujet or '(sans sujet)'}"


class Signalement(models.Model):
    class Statut(models.TextChoices):
        NOUVEAU = "nouveau", "Nouveau"
        EN_COURS = "en_cours", "En cours"
        TRAITE = "traite", "Traité"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="signalements")
    description = models.TextField()
    localisation = models.CharField(max_length=200, blank=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.NOUVEAU)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Signalement #{self.pk}"


class Initiative(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        VALIDEE = "validee", "Validée"
        REFUSEE = "refusee", "Refusée"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="initiatives")
    titre = models.CharField(max_length=150)
    description = models.TextField()
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_ATTENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.titre


class Parametre(models.Model):
    """Infos générales du site (table `parametres` : slogan, à propos, contact)."""

    cle = models.CharField("Clé", max_length=50, primary_key=True)
    valeur = models.TextField(blank=True)

    class Meta:
        verbose_name = "paramètre"
        verbose_name_plural = "infos du site"

    def __str__(self):
        return self.cle
