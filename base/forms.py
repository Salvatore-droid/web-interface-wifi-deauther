from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

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