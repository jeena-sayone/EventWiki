from django import forms

class loginForm(forms.Form):

    email = forms.EmailField(label = 'Email')
    password =forms.CharField(label = 'Password')
