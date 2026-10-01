from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'autocomplete':'username','placeholder':'Your username','autofocus':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete':'current-password','placeholder':'Your password'}))

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'autocomplete':'username','placeholder':'Choose a username','autofocus':True}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete':'email','placeholder':'you@example.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete':'new-password','placeholder':'At least 8 characters'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete':'new-password','placeholder':'Type your password again'}))
    def clean_username(self):
        username=self.cleaned_data['username']
        validator=User._meta.get_field('username').validators[0];validator(username)
        if User.objects.filter(username__iexact=username).exists():raise forms.ValidationError('This username is already taken.')
        return username
    def clean(self):
        data=super().clean()
        if data.get('password') and data.get('confirm_password') and data['password']!=data['confirm_password']:
            self.add_error('confirm_password','Passwords do not match.')
        if data.get('password'):
            user=User(username=data.get('username',''),email=data.get('email',''))
            try:validate_password(data['password'],user)
            except forms.ValidationError as e:self.add_error('password',e)
        return data
