from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class SignupForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label="Repeat password")

    class Meta:
        model = User
        fields = ("username", "password", "password2")


class MoveForm(forms.ModelForm):
    origin = forms.DecimalField(max_value=63, min_value=0)
    target = forms.DecimalField(max_value=63, min_value=0)

    class Meta:
        model = Move
        fields = ("origin", "target")
