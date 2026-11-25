import os
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Application, Category

def validate_image_file(image):
    if not image:
        raise forms.ValidationError('Необходимо прикрепить файл изображения.')

    ext = os.path.splitext(image.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    if ext not in allowed_extensions:
        raise forms.ValidationError(
            'Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.'
        )

    max_size = 2 * 1024 * 1024
    if image.size > max_size:
        raise forms.ValidationError(
            'Размер файла превышает максимально допустимые 2 МБ.'
        )

    return image

class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'})
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'ivan-ivanov'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'ivan@example.ru'})
    )
    agree_personal_data = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Необходимо дать согласие на обработку персональных данных.'}
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError('Поле ФИО обязательно для заполнения.')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', full_name):
            raise forms.ValidationError(
                'ФИО может содержать только кириллические буквы, пробелы и дефис.'
            )
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('Поле Логин обязательно для заполнения.')
        if not re.match(r'^[A-Za-z-]+$', username):
            raise forms.ValidationError(
                'Логин может содержать только латинские буквы и дефис.'
            )
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким Email уже зарегистрирован.')
        return email

class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Неверный логин или пароль. Проверьте правильность введенных данных.',
        'inactive': 'Данная учетная запись заблокирована.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

class ApplicationCreateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('title', 'description', 'category', 'plan_image')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Дизайн-проект гостиной'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваши пожелания к интерьеру...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию...'

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Название заявки не может быть пустым.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise forms.ValidationError('Описание заявки не может быть пустым.')
        return description

    def clean_plan_image(self):
        image = self.cleaned_data.get('plan_image')
        return validate_image_file(image)

class StatusInProgressForm(forms.ModelForm):
    comment = forms.CharField(
        label='Комментарий администратора',
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Укажите комментарий к принятию заявки в работу...'}),
        error_messages={'required': 'Для смены статуса на «Принято в работу» необходимо указать комментарий.'}
    )

    class Meta:
        model = Application
        fields = ('comment',)

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if not comment:
            raise forms.ValidationError('Комментарий не может состоять только из пробелов.')
        return comment


class StatusCompletedForm(forms.ModelForm):
    comment = forms.CharField(
        label='Комментарий администратора (необязательно)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите результат выполненной работы...'}),
    )

    class Meta:
        model = Application
        fields = ('design_image', 'comment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['design_image'].required = True

    def clean_design_image(self):
        image = self.cleaned_data.get('design_image')
        return validate_image_file(image)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например: 3D-дизайн'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Название категории не может быть пустым.')
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('Категория с таким названием уже существует.')
        return name