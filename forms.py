from django import forms
from django.utils import timezone

from .models import Avatar, Section, Topic, Reply


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
