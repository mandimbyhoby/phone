from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Avis, Commande, MessageContact, Profil


METHODE_PAIEMENT_CHOICES = [
    ('carte', 'Carte bancaire (Visa, Mastercard, Amex)'),
    ('paypal', 'PayPal'),
    ('orange_money', 'Orange Money'),
    ('especes', 'Paiement à la livraison'),
]

METHODES_PAIEMENT_DISPONIBLES = (
    METHODE_PAIEMENT_CHOICES
    if settings.PAIEMENTS_EN_LIGNE
    else [('especes', 'Paiement à la livraison')]
)


# ============================================================
# A U T H E N T I F I C A T I O N
# ============================================================

class InscriptionForm(UserCreationForm):
    nom_complet = forms.CharField(
        label='Nom complet',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Votre nom et prénom'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'}),
    )
    telephone = forms.CharField(
        label='Téléphone',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+261 34 00 000 00'}),
    )
    ville = forms.CharField(
        label='Ville',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Antananarivo'}),
    )
    adresse = forms.CharField(
        label='Adresse',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Adresse de livraison',
            'rows': 2,
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'nom_complet', 'email', 'telephone', 'ville', 'adresse', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom d\'utilisateur'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profil.objects.create(
                utilisateur=user,
                nom_complet=self.cleaned_data['nom_complet'],
                telephone=self.cleaned_data['telephone'],
                adresse=self.cleaned_data['adresse'],
                ville=self.cleaned_data['ville'],
            )
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d\'utilisateur ou email',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Votre nom d\'utilisateur'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Votre mot de passe'}),
    )


class ProfilForm(forms.ModelForm):
    nom_complet = forms.CharField(
        label='Nom complet',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Votre nom et prénom'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'}),
    )
    telephone = forms.CharField(
        label='Téléphone',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+261 34 00 000 00'}),
    )
    ville = forms.CharField(
        label='Ville',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Antananarivo'}),
    )
    adresse = forms.CharField(
        label='Adresse',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Adresse de livraison',
            'rows': 2,
        }),
    )
    photo = forms.ImageField(
        label='Photo de profil',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/*',
            'id': 'photo-input',
        }),
    )

    class Meta:
        model = Profil
        fields = ['nom_complet', 'telephone', 'ville', 'adresse', 'photo']

    def save(self, commit=True):
        profil = super().save(commit=False)
        user = profil.utilisateur
        user.email = self.cleaned_data['email']
        if self.cleaned_data['nom_complet']:
            user.first_name = self.cleaned_data['nom_complet'].split(' ')[0]
        if commit:
            user.save()
            profil.save()
        return profil


class ChangerMotDePasseForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Mot de passe actuel',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Votre mot de passe actuel'}),
    )
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nouveau mot de passe'}),
    )
    new_password2 = forms.CharField(
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmez le nouveau mot de passe'}),
    )


class MotDePasseOublieForm(PasswordResetForm):
    email = forms.EmailField(
        label='Votre email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'}),
    )


class ReinitialiserMotDePasseForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nouveau mot de passe'}),
    )
    new_password2 = forms.CharField(
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmez le nouveau mot de passe'}),
    )


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['nom', 'note', 'commentaire']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom',
                'required': True,
            }),
            'note': forms.Select(attrs={'class': 'form-input'}),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Partagez votre expérience avec ce produit...',
                'rows': 4,
                'required': True,
            }),
        }


class CommandeForm(forms.ModelForm):
    methode_paiement = forms.ChoiceField(
        choices=METHODES_PAIEMENT_DISPONIBLES,
        initial='especes',
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        label='Méthode de paiement',
    )

    class Meta:
        model = Commande
        fields = ['nom', 'email', 'telephone', 'adresse', 'ville']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+261 34 00 000 00'}),
            'adresse': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Adresse de livraison',
                'rows': 2,
            }),
            'ville': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ville'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemple.com'}),
            'sujet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Objet du message'}),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Votre message...',
                'rows': 5,
            }),
        }
