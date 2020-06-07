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

    def clean(self):
        """
        We need to override the default clean because when introducing an
        already existing name, username is left empty by default clean(),
        thus making the is_valid() return false
        """
        username = self.cleaned_data.get("username", "")
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data.get("password2", "")
        clean_data = {'username': username, 'password': password,
                      'password2': password2}
        return clean_data


class MoveForm(forms.ModelForm):
    origin = forms.DecimalField(max_value=63, min_value=0)
    target = forms.DecimalField(max_value=63, min_value=0)

    class Meta:
        model = Move
        fields = ("origin", "target")
