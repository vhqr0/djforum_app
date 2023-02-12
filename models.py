from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.models import User

from io import BytesIO
from PIL import Image


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

    @classmethod
    def filter(cls, GET):
        qs = cls.objects.all()
        search = GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('-count_topics')


class Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=64)
    keywords = models.CharField(max_length=64, blank=True)
    content = models.TextField(max_length=2048, blank=True)
    reference_topic = models.BigIntegerField(null=True)
    reference_floor = models.IntegerField(null=True)
    count_replies = models.IntegerField(default=0)
    count_likes = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('djforum:topic-detail', args=(self.pk, ))

    @classmethod
    def filter(cls, GET):
        qs = cls.objects.all()
        section_name = GET.get('section')
        user_name = GET.get('user')
        search = GET.get('search')
        order = GET.get('order')
        if section_name:
            section = get_object_or_404(Section, name=section_name)
            qs = qs.filter(section=section)
        if user_name:
            user = get_object_or_404(User, username=user_name)
            qs = qs.filter(user=user)
        if search:
            query = Q(title__icontains=search) | Q(keywords__icontains=search)
            qs = qs.filter(query)
        if order == 'create':
            qs = qs.order_by('-date_created')
        else:
            qs = qs.order_by('-date_updated')
        return qs

    @classmethod
    def filter_by_username(cls, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        return cls.objects.filter(user=user)

    def reply_filter(self, GET):
        qs = self.reply_set
        floor = GET.get('floor')
        user_name = GET.get('user')
        search = GET.get('search')
        order = GET.get('order')
        if floor:
            qs = qs.filter(count_replies=floor)
        if user_name:
            user = get_object_or_404(User, username=user_name)
            qs = qs.filter(user=user)
        if search:
            qs = qs.filter(content__icontains=search)
        if order == 'likes':
            qs = qs.order_by('-count_likes')
        elif order == 'new':
            qs = qs.order_by('-id')
        else:
            qs = qs.order_by('id')
        return qs


class TopTopic(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.topic)

    @classmethod
    def set(cls, topic):
        qs = cls.objects.filter(topic=topic)
        if qs.count() == 0:
            cls.objects.create(topic=topic)


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    count_replies = models.IntegerField()
    content = models.TextField(max_length=2048)
    reference_topic = models.BigIntegerField(null=True)
    reference_floor = models.IntegerField(null=True)
    count_likes = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Replies'

    def __str__(self):
        return str(self.count_replies)


class LikeTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} likes {self.topic}'


class LikeReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Like Replies'

    def __str__(self):
        return f'{self.user} likes {self.reply}'
