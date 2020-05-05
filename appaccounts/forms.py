from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    PasswordChangeForm,
    SetPasswordForm
)
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import (
    SignupForm, LoginForm, AddEmailForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordKeyForm
)

from .models import Profile


class AllAuthSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'id': 'username',
            'class': 'form-control form-control-prepended',
            'placeholder': 'Login',
        })
        self.fields['email'].widget.attrs.update({
            'id': 'id_email',
            'class': 'form-control form-control-prepended',
            'placeholder': 'Email',
            'required': True,
        })
        self.fields['password1'].widget.attrs.update({
            'id': 'id_password1',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Пароль')
        })
        self.fields['password2'].widget.attrs.update({
            'id': 'id_password2',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Подтверждение'),
        })

    def clean_username(self):
        super(AllAuthSignupForm, self).clean_username()
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(email__iexact=username).exists():
            raise forms.ValidationError(_('Уже есть пользователь с таким e-mail, выберите другое имя.'))
        else:
            black_list = settings.ACCOUNT_USERNAME_BLACKLIST_SHORT
            available_letters = 'zxcvbnmasdfghjklqwertyuiop'
            new_word = ''
            for letter in username.lower():
                if letter in available_letters:
                    new_word += letter
                else:
                    new_word += '#'
            name_is_good = True
            if new_word:
                for check_word in new_word.split('#'):
                    if check_word in black_list:
                        name_is_good = False
            if not name_is_good:
                raise forms.ValidationError(_('Такое имя пользователя не может быть использовано, выберите другое.'))
        return username
        
        
class AllAuthLoginForm(LoginForm):
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.error_messages['username_password_mismatch'] = _('Не правильное имя пользователя и/или пароль')

        self.fields['login'].widget.attrs.update({
            'id': 'email',
            'type': 'text',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Email или login'),
        })
        self.fields['password'].widget.attrs.update({
            'id': 'password',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Пароль'),
        })
        self.fields['remember'].widget.attrs.update({
            'class': 'custom-control-input',
        })


class AllAuthAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })


class AllAuthChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['oldpassword'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })

    def clean_oldpassword(self):
        if self.user.profile.need_password:
            return super(AllAuthChangePasswordForm, self).clean_oldpassword()
        else:
            return self.cleaned_data["oldpassword"]


class AllAuthResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })


class AllAuthResetPasswordKeyForm(ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):

        print('asdf2')
    
        super(AllAuthResetPasswordKeyForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-prepended',
        })


class DjangoLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.EmailInput(attrs={
        'id': 'email',
        'type': 'text',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Email или login'),
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'password',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Пароль'),
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = _('Не правильное имя пользователя или пароль')


class UserPasswordResetForm(PasswordResetForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'id': 'id_email',
        'type': 'email',
        'class': 'form-control form-control-prepended',
        'placeholder': 'Email',
    }))

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('Пользователь с таким e-mail в базе не найден'))
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'old_password',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Старый пароль')
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'new_password1',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Подтверждение'),
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'new_password2',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Подтверждение'),
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['password_mismatch'] = _('Пароль и подтверждение не совпадают')


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'new_password1',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Новый пароль')
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'new_password2',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Подтверждение'),
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'password_mismatch': _('Пароль и подтверждение не совпадают'),
        }


class UserRegistrationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.error_messages = {
            'password_mismatch': _('Пароль и подтверждение не совпадают'),
        }
        self.fields['username'].widget.attrs.update({
            'id': 'username',
            'class': 'form-control form-control-prepended',
            'placeholder': 'Login',
        })
        self.fields['email'].widget.attrs.update({
            'id': 'id_email',
            'class': 'form-control form-control-prepended',
            'placeholder': 'Email',
            'required': True,
        })
        self.fields['password1'].widget.attrs.update({
            'id': 'id_password1',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Пароль')
        })
        self.fields['password2'].widget.attrs.update({
            'id': 'id_password2',
            'class': 'form-control form-control-prepended',
            'placeholder': _('Подтверждение'),
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('Пользователь с таким e-mail уже существует'))
        return email


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'id': 'first_name',
            'class': 'form-control',
            'placeholder': _('Имя'),
        })


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'id': 'username',
        'type': 'text',
        'class': 'form-control form-control-prepended',
        'placeholder': _('Login'),
    }))

    class Meta:
        model = Profile
        fields = ('description', 'avatar', 'index_avatar')
        widgets = {
                'avatar': forms.FileInput(attrs={'class': 'custom-file-input',}),
            }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Пара слов о себе...'),
        })

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if username != self.instance.user.username and User.objects.filter(username__iexact=username).exists():
            str1 = _('Уже есть пользователь с логином')
            str2 = _('выберите другое имя')
            raise forms.ValidationError(f'{str1} {username} {str2}')
        else:
            black_list = settings.ACCOUNT_USERNAME_BLACKLIST_SHORT
            available_letters = 'zxcvbnmasdfghjklqwertyuiop'
            new_word = ''
            for letter in username.lower():
                if letter in available_letters:
                    new_word += letter
                else:
                    new_word += '#'
            name_is_good = True
            if new_word:
                for check_word in new_word.split('#'):
                    if check_word in black_list:
                        name_is_good = False
            if not name_is_good:
                raise forms.ValidationError(_('Такое имя пользователя не может быть использовано, выберите другое.'))
        return username
