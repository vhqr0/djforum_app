from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.templatetags.static import static
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, ListView, \
    FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import UserProfile, Section, Topic, TopTopic, Reply, \
    LikeTopic, LikeReply
from .forms import AvatarUploadForm, TopicCreateForm, ReplyCreateForm


class IndexView(TemplateView):
    template_name = 'djforum/views/index.djhtml'

    def get_context_data(self, **kwargs):
        toptopics = TopTopic.objects.all()
        topics = Topic.objects.order_by('-date_updated')[:20]
        return {'toptopics': toptopics, 'topics': topics}


class UserDetailView(DetailView):
    model = User
    template_name = 'djforum/views/user_detail.djhtml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = UserProfile.get_profile(self.object)
        context['topics'] = self.object.topic_set.order_by(
            '-date_created')[:10]
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['website', 'introduction']
    template_name = 'djforum/views/forms/userprofile_update.djhtml'

    def get_object(self, queryset=None):
        return UserProfile.get_profile(self.request.user)

    def get_success_url(self):
        return reverse('djforum:user-detail', args=(self.request.user.pk, ))


@require_GET
def avatar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if hasattr(user, 'avatar'):
        return HttpResponse(user.avatar.data,
                            headers={'Content-Type': 'image/png'})
    else:
        return HttpResponseRedirect(
            static('djforum/images/default_avatar.png'))


class AvatarUploadView(LoginRequiredMixin, FormView):
    form_class = AvatarUploadForm
    template_name = 'djforum/views/forms/avatar_upload.djhtml'

    def form_valid(self, form):
        form.save(self.request)
        messages.add_message(self.request, messages.SUCCESS,
                             'Upload avatar success')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:user-detail', args=(self.request.user.pk, ))


class SectionListView(ListView):
    template_name = 'djforum/views/section_list.djhtml'
    paginate_by = 50

    def get_queryset(self):
        return Section.filter(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        params = self.request.GET.copy()
        params.pop('page', True)
        context['params'] = params.urlencode()
        return context


class TopicListView(ListView):
    template_name = 'djforum/views/topic_list.djhtml'
    paginate_by = 20

    def get_queryset(self):
        return Topic.filter(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.request.GET.get('section')
        params = self.request.GET.copy()
        params.pop('page', True)
        context['params'] = params.urlencode()
        return context


class TopicDetailView(SingleObjectMixin, ListView):
    template_name = 'djforum/views/topic_detail.djhtml'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Topic.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.reply_filter(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.object
        params = self.request.GET.copy()
        params.pop('page', True)
        context['params'] = params.urlencode()
        return context


class TopicCreateView(LoginRequiredMixin, FormView):
    form_class = TopicCreateForm
    template_name = 'djforum/views/forms/topic_create.djhtml'

    def get_initial(self):
        initial = super().get_initial()
        section = self.request.GET.get('section')
        reference_topic = self.request.GET.get('reference_topic')
        reference_floor = self.request.GET.get('reference_floor')
        if section:
            initial['section'] = section
        if reference_topic:
            initial['reference_topic'] = reference_topic
        if reference_floor:
            initial['reference_floor'] = reference_floor
        return initial

    def form_valid(self, form):
        self.topic_pk = form.save(self.request)
        messages.add_message(self.request, messages.SUCCESS,
                             'Create topic success')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:topic-detail', args=(self.topic_pk, ))


class ReplyCreateView(LoginRequiredMixin, FormView):
    form_class = ReplyCreateForm
    template_name = 'djforum/views/forms/reply_create.djhtml'

    def get_initial(self):
        initial = super().get_initial()
        reference_topic = self.request.GET.get('reference_topic')
        reference_floor = self.request.GET.get('reference_floor')
        if reference_topic:
            initial['reference_topic'] = reference_topic
        if reference_floor:
            initial['reference_floor'] = reference_floor
        return initial

    def form_valid(self, form):
        topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        form.save(self.request, topic)
        messages.add_message(self.request, messages.SUCCESS,
                             'Create reply success')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:topic-detail', args=(self.kwargs['pk'], ))


@require_POST
@login_required()
def topic_like(request, pk):
    user = request.user
    topic = get_object_or_404(Topic, pk=pk)
    likes = LikeTopic.objects.filter(user=user, topic=topic)
    if likes.count() == 0:
        LikeTopic.objects.create(user=user, topic=topic)
        topic.count_likes += 1
        topic.save()
    return HttpResponse()


@require_POST
@login_required()
def reply_like(request, pk):
    user = request.user
    reply = get_object_or_404(Reply, pk=pk)
    likes = LikeReply.objects.filter(user=user, reply=reply)
    if likes.count() == 0:
        LikeReply.objects.create(user=user, reply=reply)
        reply.count_likes += 1
        reply.save()
    return HttpResponse()
