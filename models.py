from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User

import uuid
import datetime

from io import BytesIO
from PIL import Image

VERIFY_TYPE_CHOICES = (
    ('register', 'User Register'),
    ('password', 'Change Password'),
)


class VerifyRecord(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    verify_code = models.UUIDField()
    verify_type = models.CharField(max_length=10, choices=VERIFY_TYPE_CHOICES)
    time_sent = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.verify_code:
            self.verify_code = uuid.uuid4()
        if self.verify_type == 'password':
            self.username = User.objects.get(email=self.email)
        self.send_mail()
        super().save(*args, **kwargs)

    def send_mail(self):
        subject = f'DJForum Verify For {self.get_verify_type_display()}'
        message = f'Username: {self.username}\nUUID: {self.verify_code}\n'
        from_email = 'www@DJForum.net'
        to_emails = [self.email]
        send_mail(subject, message, from_email, to_emails)

    def is_valid(self, verify_code):
        now = timezone.now()
        delta = datetime.timedelta(minutes=30)
        return self.is_active and \
            now - self.time_sent < delta and \
            verify_code == self.verify_code

    def do_action(self):
        self.is_active = False
        if self.verify_type == 'register':
            self.do_register()
        else:
            self.do_change_password()

    def do_register(self):
        query = Q(username=self.username) | Q(email=self.email)
        assert User.objects.filter(query).count() == 0
        user = User.objects.create_user(self.username, \
                                        self.email, \
                                        self.password)
        user.save()

    def do_change_password(self):
        user = User.objects.get(email=self.email)
        user.set_password(self.password)
        user.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    introduction = models.TextField(max_length=2048, blank=True)

    def __str__(self):
        return str(self.user)

    @classmethod
    def get_profile(cls, user):
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
        else:
            profile = UserProfile(user=user)
            profile.save()
        return profile


class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data = models.BinaryField(max_length=4096)

    @classmethod
    def set(cls, user, img):
        bio = BytesIO()
        img = Image.open(img).resize((32, 32))
        img.save(bio, format='png')
        Avatar.objects.update_or_create(user=user,
                                        defaults={'data': bio.getvalue()})


class Section(models.Model):
    name = models.CharField(max_length=16)
    count_topics = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=64)
    keywords = models.CharField(max_length=64, blank=True)
    content = models.TextField(max_length=2048, blank=True)
    count_replies = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TopTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.topic)


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.TextField(max_length=2048)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Replies'

    def __str__(self):
        return f'{self.user}: {self.topic}'
