from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Article, Campagne, Parametre, PointCollecte, User

APROPOS = (
    "EcoIndustrial est un site web dynamique dédié à la lutte contre la pollution plastique à Garoua. "
    "Il informe sur les effets des déchets plastiques, mobilise autour de campagnes de nettoyage, "
    "oriente vers des points de collecte de bouteilles et promeut l'économie circulaire."
)


class Command(BaseCommand):
    help = "Charge les données de démonstration (équivalent de database.sql / migration.sql)."

    def handle(self, *args, **opts):
        if not User.objects.filter(email="admin@ecoindustrial.local").exists():
            User.objects.create_superuser("admin@ecoindustrial.local", "password", nom="Administrateur")
            self.stdout.write("Admin créé : admin@ecoindustrial.local / password (À CHANGER)")
        for cle, val in {"slogan": "Transformer les déchets en valeur", "apropos": APROPOS,
                         "adresse": "", "telephone": "", "email_contact": ""}.items():
            Parametre.objects.get_or_create(cle=cle, defaults={"valeur": val})
        now = timezone.now()
        campagnes = [
            ("Grand nettoyage de Kanadi", "Kanadi", now + timedelta(days=7), 40,
             "Ramassage des déchets plastiques le long des rues du quartier Kanadi, avec les habitants et les commerçants."),
            ("Collecte de bouteilles au Grand marché", "Grand marché", now + timedelta(days=14), 30,
             "Collecte de bouteilles plastiques propres sur le site du Grand marché, en lien avec les vendeurs."),
            ("Nettoyage du quartier Yelwa", "Yelwa", now + timedelta(days=21), 35,
             "Opération de nettoyage et de sensibilisation au tri dans le quartier Yelwa."),
        ]
        for titre, lieu, debut, capacite, description in campagnes:
            Campagne.objects.update_or_create(
                titre=titre,
                defaults={"lieu": lieu, "date_debut": debut, "capacite": capacite, "description": description},
            )

        points = [
            ("Point de collecte Kanadi", "Kanadi", "Carrefour Kanadi", "Lun–Sam, 8h–18h"),
            ("Point de collecte Grand marché", "Grand marché", "Entrée du marché central", "Tous les jours, 7h–19h"),
            ("Point de collecte Yelwa", "Yelwa", "Route de Yelwa", "Lun–Sam, 9h–17h"),
        ]
        for nom, quartier, adresse, horaires in points:
            PointCollecte.objects.update_or_create(
                nom=nom,
                defaults={"quartier": quartier, "adresse": adresse, "horaires": horaires,
                          "description": "Dépôt de bouteilles plastiques propres."},
            )
        if not Article.objects.exists():
            for titre, cat, contenu in [
                ("Les effets des déchets plastiques", "environnement", "Les plastiques à usage unique se dégradent très lentement. Mal gérés, ils s'accumulent dans l'espace public, obstruent les caniveaux et dégradent le cadre de vie."),
                ("Du déchet à la ressource", "recyclage", "Un plastique propre et trié peut être valorisé plutôt que jeté : c'est le principe de l'économie circulaire."),
                ("Trier ses bouteilles en 3 gestes", "conseil", "Vider la bouteille, la rincer, puis la déposer dans un point de collecte."),
                ("Lancement du site EcoIndustrial", "actualite", "Bienvenue sur la plateforme de sensibilisation, de collecte et de valorisation des déchets plastiques à Garoua."),
            ]:
                Article.objects.create(titre=titre, categorie=cat, contenu=contenu)
        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
