from .models import Parametre

DEFAUTS = {
    "slogan": "Transformer les déchets en valeur",
    "apropos": "",
    "adresse": "",
    "telephone": "",
    "email_contact": "",
}


def site(request):
    try:
        valeurs = dict(Parametre.objects.values_list("cle", "valeur"))
    except Exception:  # table pas encore migrée
        valeurs = {}
    return {"site": {k: valeurs.get(k) or d for k, d in DEFAUTS.items()}}
