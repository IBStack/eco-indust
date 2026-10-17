from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    ContactForm, DeleteAccountForm, EmailAuthenticationForm, InitiativeForm,
    PasswordForm, ProfileForm, RegisterForm, SignalementForm,
)
from .models import QUARTIERS, Article, Campagne, Initiative, Inscription, PointCollecte, Signalement

EFFETS = [
    ("c1", "pin", "Caniveaux obstrués", "Les déchets bloquent caniveaux et drains et aggravent le risque d'inondation lors des fortes pluies."),
    ("c2", "leaf", "Cadre de vie dégradé", "Aspect visuel et odeurs : les déchets accumulés abîment l'espace public."),
    ("c3", "flag", "Risques sanitaires", "L'eau stagnante et les déchets accumulés peuvent nuire à la santé."),
    ("c4", "recycle", "Ressources perdues", "Un plastique propre et trié peut être valorisé plutôt que jeté."),
]

# clé en base -> (titre, nom d'URL, sous-titre)
CATEGORIES = {
    "environnement": ("Environnement", "environnement", "Les effets de la pollution plastique sur notre cadre de vie."),
    "recyclage": ("Recyclage", "recyclage", "Du déchet à la ressource : comprendre l'économie circulaire."),
    "conseil": ("Conseils", "conseils", "Gestes simples pour trier et réduire ses déchets."),
    "actualite": ("Actualités", "actualites", "Les dernières nouvelles d'EcoIndustrial."),
}


def home(request):
    camps = Campagne.objects.with_n()
    context = {
        "prochaine": camps.filter(statut=Campagne.Statut.OUVERTE, date_debut__gte=timezone.now()).order_by("date_debut").first(),
        "camps": camps.order_by("-date_debut")[:3],
        "points": PointCollecte.objects.order_by("id")[:4],
        "actus": Article.objects.filter(categorie=Article.Categorie.ACTUALITE)[:3],
        "effets": EFFETS,
        "hero": bool(finders.find("img/hero.jpg")),
    }
    return render(request, "core/home.html", context)


def about(request):
    objectifs = [
        "Présenter des contenus sur la pollution plastique, le recyclage et l'économie circulaire",
        "Publier et gérer des campagnes de nettoyage",
        "Permettre l'inscription en ligne à une campagne",
        "Localiser les points de collecte",
        "Permettre de signaler un dépôt de déchets",
        "Offrir un canal de contact et de proposition d'initiative",
    ]
    return render(request, "core/about.html", {"objectifs": objectifs})


def articles(request, cat):
    if cat not in CATEGORIES:
        raise Http404
    titre, _, sous_titre = CATEGORIES[cat]
    context = {
        "cat": cat,
        "titre": titre,
        "sous_titre": sous_titre,
        "tabs": [(k, v[0], v[1]) for k, v in CATEGORIES.items()],
        "articles": Article.objects.filter(categorie=cat),
        "effets": EFFETS if cat == "environnement" else None,
    }
    return render(request, "core/articles.html", context)


def article_detail(request, pk):
    return render(request, "core/article_detail.html", {"article": get_object_or_404(Article, pk=pk)})


def campagnes(request):
    lieu = request.GET.get("lieu", "").strip()
    rows = Campagne.objects.with_n()
    if lieu:
        rows = rows.filter(lieu=lieu)
    return render(request, "core/campagnes.html", {
        "campagnes": rows,
        "lieux": [code for code, _ in QUARTIERS],
        "lieu": lieu,
    })


def campagne_detail(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        with transaction.atomic():
            c = Campagne.objects.select_for_update().get(pk=pk)
            if c.statut != Campagne.Statut.OUVERTE or c.inscriptions.count() >= c.capacite:
                messages.error(request, "Cette campagne est complète ou fermée.")
            else:
                _, created = Inscription.objects.get_or_create(user=request.user, campagne=c)
                if created:
                    messages.success(request, "Inscription enregistrée.")
                else:
                    messages.error(request, "Vous êtes déjà inscrit(e) à cette campagne.")
        return redirect("campagne", pk=pk)
    c = get_object_or_404(Campagne.objects.with_n(), pk=pk)
    return render(request, "core/campagne_detail.html", {"c": c})


def points(request):
    quartier = request.GET.get("quartier", "").strip()
    rows = PointCollecte.objects.all()
    if quartier:
        rows = rows.filter(quartier=quartier)
    quartiers = PointCollecte.objects.exclude(quartier="").order_by("quartier").values_list("quartier", flat=True).distinct()
    return render(request, "core/points.html", {"points": rows, "quartiers": quartiers, "quartier": quartier})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Message envoyé. Merci !")
        return redirect("contact")
    return render(request, "core/contact.html", {"form": form})


def inscription(request):
    if request.user.is_authenticated:
        return redirect("profil")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Compte créé. Connectez-vous.")
        return redirect("login")
    return render(request, "core/register.html", {"form": form})


class LoginView(auth_views.LoginView):
    template_name = "core/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse("admin:index") if self.request.user.is_staff else reverse("profil")


@login_required
def profil(request):
    user = request.user
    forms = {
        "maj": ProfileForm(instance=user),
        "mdp": PasswordForm(user),
        "supprimer": DeleteAccountForm(user),
    }
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "annuler":
            Inscription.objects.filter(pk=request.POST.get("id") or 0, user=user).delete()
            messages.success(request, "Inscription annulée.")
            return redirect("profil")
        if action == "maj":
            form = ProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profil mis à jour.")
                return redirect("profil")
            forms["maj"] = form
        elif action == "mdp":
            form = PasswordForm(user, request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["nouveau"])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe modifié.")
                return redirect("profil")
            forms["mdp"] = form
        elif action == "supprimer":
            if user.is_staff:
                messages.error(request, "Le compte administrateur ne peut pas être supprimé ici.")
                return redirect("profil")
            form = DeleteAccountForm(user, request.POST)
            if form.is_valid():
                user.delete()
                logout(request)
                messages.success(request, "Votre compte a été supprimé.")
                return redirect("home")
            forms["supprimer"] = form
    inscriptions = user.inscriptions.select_related("campagne").order_by("campagne__date_debut")
    return render(request, "core/profil.html", {"forms": forms, "inscriptions": inscriptions})


@login_required
def signalement(request):
    form = SignalementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        s = form.save(commit=False)
        s.user = request.user
        s.save()
        messages.success(request, "Signalement enregistré. Merci !")
        return redirect("signalement")
    mes = Signalement.objects.filter(user=request.user)
    return render(request, "core/signalement.html", {"form": form, "signalements": mes})


def initiatives(request):
    form = InitiativeForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if form.is_valid():
            i = form.save(commit=False)
            i.user = request.user
            i.save()
            messages.success(request, "Initiative envoyée. Elle sera examinée par l'administrateur.")
            return redirect("initiatives")
    publiees = Initiative.objects.filter(statut=Initiative.Statut.VALIDEE).select_related("user")
    mine = Initiative.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, "core/initiatives.html", {"form": form, "publiees": publiees, "mine": mine})
