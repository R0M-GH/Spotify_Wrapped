from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter your birthday'}), required=True)

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ForgetForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    securityAnswer = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter your birthday'}), required=True)

    #securityAnswer = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter in the format: MM/DD/YYYY'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))


