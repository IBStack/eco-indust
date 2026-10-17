from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("a-propos/", views.about, name="a_propos"),
    path("environnement/", views.articles, {"cat": "environnement"}, name="environnement"),
    path("recyclage/", views.articles, {"cat": "recyclage"}, name="recyclage"),
    path("conseils/", views.articles, {"cat": "conseil"}, name="conseils"),
    path("actualites/", views.articles, {"cat": "actualite"}, name="actualites"),
    path("articles/<int:pk>/", views.article_detail, name="article"),
    path("campagnes/", views.campagnes, name="campagnes"),
    path("campagnes/<int:pk>/", views.campagne_detail, name="campagne"),
    path("points/", views.points, name="points"),
    path("contact/", views.contact, name="contact"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.LoginView.as_view(), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("profil/", views.profil, name="profil"),
    path("signalement/", views.signalement, name="signalement"),
    path("initiatives/", views.initiatives, name="initiatives"),
]
