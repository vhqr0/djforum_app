from django import forms
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import VerifyRecord, Avatar, Section, Topic, Reply

LOGIN_TYPE_CHOICES = (
    ('login', 'User Login'),
    ('register', 'User Register'),
    ('password', 'Change Password'),
)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    login_type = forms.ChoiceField(choices=LOGIN_TYPE_CHOICES, initial='login')

    def clean(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        login_type = self.cleaned_data['login_type']
        if login_type == 'login':
            if not username:
                raise forms.ValidationError('Username cannot leave blank!')
            self.user = authenticate(username=username, password=password)
            if self.user is None or not self.user.is_active:
                raise forms.ValidationError('Invalid Username or Password!')
        elif login_type == 'register':
            if not username or not email:
                raise forms.ValidationError(
                    'Username or Email cannot leave blank!')
            query = Q(username=username) | Q(email=email)
            if User.objects.filter(query).count() != 0:
                raise forms.ValidationError(
                    'Username or Email is already exists!')
        else:
            if not email:
                raise forms.ValidationError('Email cannot leave blank!')
            if User.objects.filter(email=email).count() == 0:
                raise forms.ValidationError('Email is not exists!')
        return super().clean()

    def login(self, request):
        login(request, self.user)

    def verify(self):
        record = VerifyRecord(username=self.cleaned_data['username'],
                              email=self.cleaned_data['email'],
                              password=self.cleaned_data['password'],
                              verify_type=self.cleaned_data['login_type'])
        record.save()
        return record.pk


class VerifyForm(forms.Form):
    verify_code = forms.UUIDField()

    def clean(self):
        self.verify_record = VerifyRecord.objects.get(pk=self.verify_pk)
        if not self.verify_record.is_valid(self.cleaned_data['verify_code']):
            raise forms.ValidationError('Invalid Verify Code!')
        return super().clean()

    def do_action(self):
        return self.verify_record.do_action()


class AvatarUploadForm(forms.Form):
    avatar = forms.ImageField(help_text='Please upload an image < 4KB.')

    def clean(self):
        if self.cleaned_data['avatar'].size > 4096:
            raise forms.ValidationError('Image too big!')
        return super().clean()

    def save(self, request):
        Avatar.set(request.user, self.cleaned_data['avatar'])


class TopicCreateForm(forms.Form):
    section = forms.CharField(max_length=16, required=False)
    title = forms.CharField(max_length=64)
    keywords = forms.CharField(max_length=64, required=False)
    description = forms.CharField(max_length=2048,
                                  required=False,
                                  widget=forms.Textarea)

    def save(self, request):
        topic = Topic(user=request.user,
                      title=self.cleaned_data['title'],
                      keywords=self.cleaned_data['keywords'],
                      description=self.cleaned_data['description'])
        section_name = self.cleaned_data['section']
        if section_name:
            section, _ = Section.objects.get_or_create(name=section_name)
            section.count_topics += 1
            section.save()
            topic.section = section
        topic.save()
        return section_name


class ReplyCreateForm(forms.Form):
    reply = forms.CharField(max_length=2048, widget=forms.Textarea)

    def save(self, request, topic):
        topic.count_replies += 1
        topic.save()
        reply = Reply(user=request.user,
                      topic=topic,
                      content=self.cleaned_data['reply'])
        reply.save()
