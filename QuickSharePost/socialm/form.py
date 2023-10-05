from django import forms

# profilese user import
from .models import *


class registerForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Adınız'}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Soyadınız'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Kullanıcı adınız'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Şifreniz', 'type': 'password'}))
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email adresiniz'}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "email"]

        help_texts = {

            "username": None
        }


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['text']


class ApprovalForm(forms.Form):
    approve = forms.BooleanField(label='Hesap Onayla', required=False, initial=False,
                                 widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
