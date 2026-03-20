from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Obligatorio. Ingresa una dirección de correo válida.',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está en uso.')
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        help_text='Obligatorio. Ingresa una dirección de correo válida.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': 'Obligatorio. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Obligatorio. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
    
    def clean_email(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data.get('username')
        
        if User.objects.exclude(username=username).filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está en uso por otro usuario.')
            
        return email

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirmar nueva contraseña', widget=forms.PasswordInput)

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )