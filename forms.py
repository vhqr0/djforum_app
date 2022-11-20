from django import forms
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import VerifyRecord, Avatar, Section, Topic, Reply


class FormControlMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


LOGIN_TYPE_CHOICES = (
    ('login', 'User Login'),
    ('register', 'User Register'),
    ('password', 'Change Password'),
)


class LoginForm(FormControlMixin, forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        help_text='Please enter username if you want to login or register.')
    email = forms.EmailField(
        required=False,
        help_text=('Please enter email '
                   'if you want to register or change password.'))
    password = forms.CharField(max_length=128,
                               help_text='Please enter password.',
                               widget=forms.PasswordInput)
    login_type = forms.ChoiceField(choices=LOGIN_TYPE_CHOICES,
                                   initial='login',
                                   help_text='Please select an action.')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        login_type = cleaned_data.get('login_type')
        if login_type == 'login':
            if not username or not password:
                raise forms.ValidationError(
                    'Username or Password cannot leave blank!')
            self.user = authenticate(username=username, password=password)
            if self.user is None or not self.user.is_active:
                raise forms.ValidationError('Invalid Username or Password!')
        elif login_type == 'register':
            if not username or not email or not password:
                raise forms.ValidationError(
                    'Username, Email or Password cannot leave blank!')
            query = Q(username=username) | Q(email=email)
            if User.objects.filter(query).count() != 0:
                raise forms.ValidationError(
                    'Username or Email is already exists!')
        elif login_type == 'password':
            if not email or not password:
                raise forms.ValidationError(
                    'Email or Password cannot leave blank!')
            if User.objects.filter(email=email).count() == 0:
                raise forms.ValidationError('Email is not exists!')
        else:
            raise forms.ValidationError('Invalid Login Type!')
        return cleaned_data

    def login(self, request):
        login(request, self.user)

    def verify(self):
        record = VerifyRecord(username=self.cleaned_data['username'],
                              email=self.cleaned_data['email'],
                              password=self.cleaned_data['password'],
                              verify_type=self.cleaned_data['login_type'])
        record.save()
        return record.pk


class VerifyForm(FormControlMixin, forms.Form):
    verify_code = forms.UUIDField(
        help_text='Please enter the verify code sent to your email.')

    def clean(self):
        cleaned_data = super().clean()
        verify_code = cleaned_data.get('verify_code')
        if not verify_code:
            raise forms.ValidationError('Verify Code cannot leave blank!')
        try:
            self.verify_record = VerifyRecord.objects.get(pk=self.verify_pk)
        except VerifyRecord.DoesNotExist:
            raise forms.ValidationError('Invalid Verify Record!')
        if not self.verify_record.is_valid(self.cleaned_data['verify_code']):
            raise forms.ValidationError('Invalid Verify Code!')
        return cleaned_data

    def do_action(self):
        return self.verify_record.do_action()


class AvatarUploadForm(FormControlMixin, forms.Form):
    avatar = forms.ImageField(help_text='Please upload an image < 4KB.')

    def clean(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get('avatar')
        if avatar and avatar.size > 4096:
            raise forms.ValidationError('Image too big!')
        return cleaned_data

    def save(self, request):
        Avatar.set(request.user, self.cleaned_data['avatar'])


class TopicCreateForm(FormControlMixin, forms.Form):
    section = forms.CharField(max_length=16,
                              required=False,
                              help_text='Please enter a section if you want.')
    title = forms.CharField(max_length=64, help_text='Please enter the title.')
    keywords = forms.CharField(max_length=64,
                               required=False,
                               help_text='Please enter keywords if you want.')
    reference_topic = forms.IntegerField(required=False,
                                         help_text='Refer to a topic.')
    reference_floor = forms.IntegerField(required=False,
                                         help_text='Refer to a reply.')
    content = forms.CharField(
        max_length=2048,
        required=False,
        help_text='Please enter a description < 2048 chars if you want.',
        widget=forms.Textarea)

    def save(self, request):
        topic = Topic(user=request.user,
                      title=self.cleaned_data['title'],
                      keywords=self.cleaned_data['keywords'],
                      reference_topic=self.cleaned_data['reference_topic'],
                      reference_floor=self.cleaned_data['reference_floor'],
                      content=self.cleaned_data['content'])
        section_name = self.cleaned_data['section']
        if section_name:
            section, _ = Section.objects.get_or_create(name=section_name)
            section.count_topics += 1
            section.save()
            topic.section = section
        topic.save()
        return topic.pk


class ReplyCreateForm(FormControlMixin, forms.Form):
    reference_topic = forms.IntegerField(required=False,
                                         help_text='Refer to a topic.')
    reference_floor = forms.IntegerField(required=False,
                                         help_text='Refer to a reply.')
    reply = forms.CharField(max_length=2048,
                            help_text='Please input text < 2048 chars.',
                            widget=forms.Textarea)

    def save(self, request, topic):
        topic.count_replies += 1
        topic.date_updated = timezone.now()
        topic.save()
        reply = Reply(user=request.user,
                      topic=topic,
                      count_replies=topic.count_replies,
                      reference_topic=self.cleaned_data['reference_topic'],
                      reference_floor=self.cleaned_data['reference_floor'],
                      content=self.cleaned_data['reply'])
        reply.save()
