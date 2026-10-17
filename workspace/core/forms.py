from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import QUARTIERS, Initiative, Message, Signalement, User


class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "E-mail"
        self.fields["username"].widget = forms.EmailInput(attrs={"autofocus": True})
        self.error_messages["invalid_login"] = "E-mail ou mot de passe incorrect."
        self.error_messages["inactive"] = "Ce compte est désactivé."

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class RegisterForm(forms.ModelForm):
    mdp = forms.CharField(label="Mot de passe (8 caractères min.)", min_length=8, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["nom", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email

    def clean_mdp(self):
        pw = self.cleaned_data["mdp"]
        password_validation.validate_password(pw)
        return pw

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["mdp"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nom", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email


class PasswordForm(forms.Form):
    actuel = forms.CharField(label="Mot de passe actuel", widget=forms.PasswordInput)
    nouveau = forms.CharField(label="Nouveau (8 caractères min.)", min_length=8, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_actuel(self):
        if not self.user.check_password(self.cleaned_data["actuel"]):
            raise forms.ValidationError("Mot de passe actuel incorrect.")
        return self.cleaned_data["actuel"]

    def clean_nouveau(self):
        pw = self.cleaned_data["nouveau"]
        password_validation.validate_password(pw, self.user)
        return pw


class DeleteAccountForm(forms.Form):
    mdp = forms.CharField(label="Confirmez avec votre mot de passe", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_mdp(self):
        if not self.user.check_password(self.cleaned_data["mdp"]):
            raise forms.ValidationError("Mot de passe incorrect.")
        return self.cleaned_data["mdp"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["nom", "email", "sujet", "message"]
        labels = {"nom": "Nom", "email": "E-mail", "sujet": "Sujet", "message": "Message"}


class SignalementForm(forms.ModelForm):
    localisation = forms.ChoiceField(
        label="Localisation (facultatif)",
        required=False,
        choices=[("", "Choisir un quartier")] + QUARTIERS,
    )

    class Meta:
        model = Signalement
        fields = ["description", "localisation"]


class InitiativeForm(forms.ModelForm):
    class Meta:
        model = Initiative
        fields = ["titre", "description"]
        labels = {"titre": "Titre", "description": "Description"}
