from django import forms

class RegistrationForm(forms.Form):
    """
    A form for user registration.

    This form collects a username, password, and birthday from the user.
    It also validates that the two password entries match.

    Attributes:
        username (CharField): The user's desired username.
        password1 (CharField): The user's password.
        password2 (CharField): A confirmation of the user's password.
        birthday (DateField): The user's birthday.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    birthday = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Enter your birthday', 'type': 'date'}), required=True)

    def clean(self):
        """
        Clean and validate the form data.

        This method checks that the two password fields match. If they do not,
        a ValidationError is raised.

        Returns:
            dict: A dictionary containing the cleaned form data.

        Raises:
            forms.ValidationError: If the passwords do not match.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Check if both passwords have been provided and if they match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data  # Return cleaned_data after validation

class LoginForm(forms.Form):
    """
    A form for user login.

    This form collects the username and password for user authentication.

    Attributes:
        username (CharField): The user's username.
        password (CharField): The user's password.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))



class ForgetForm(forms.Form):
    """
    A form for password recovery.

    This form collects a username, security answer, and new password entries
    for resetting a user's password.

    Attributes:
        username (CharField): The user's username.
        security_answer (DateField): The user's security answer (e.g., birthday).
        new_password1 (CharField): The new password.
        new_password2 (CharField): A confirmation of the new password.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    security_answer = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter your birthday'}), required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))

