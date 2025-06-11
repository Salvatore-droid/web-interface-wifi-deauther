from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()



class ScanForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-900 border border-gray-700 p-3 text-green-400 font-mono',
            'placeholder': 'sudo password'
        }),
        required=True,
        label="SUDO Password"
    )
    
    timeout = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-gray-900 border border-gray-700 p-3 text-green-400 font-mono',
            'value': '30'
        }),
        initial=30,
        validators=[
            MinValueValidator(5, message="Scan must run for at least 5 seconds"),
            MaxValueValidator(120, message="Scan cannot run longer than 120 seconds")
        ],
        required=False,
        label="Scan Duration (seconds)"
    )

class ProfileUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'bg-gray-800 border border-gray-700 rounded px-4 py-2 text-gray-300'}),
            'email': forms.EmailInput(attrs={'class': 'bg-gray-800 border border-gray-700 rounded px-4 py-2 text-gray-300'}),
            'first_name': forms.TextInput(attrs={'class': 'bg-gray-800 border border-gray-700 rounded px-4 py-2 text-gray-300'}),
            'last_name': forms.TextInput(attrs={'class': 'bg-gray-800 border border-gray-700 rounded px-4 py-2 text-gray-300'}),
        }

# class CustomPasswordChangeForm(PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({
#                 'class': 'bg-gray-800 border border-gray-700 rounded px-4 py-2 text-gray-300 w-full',
#                 'autocomplete': 'off'
#             })