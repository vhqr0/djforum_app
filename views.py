from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.templatetags.static import static
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import RedirectView, TemplateView, DetailView, ListView, FormView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.http import require_GET
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import UserProfile, Section, Topic, TopTopic
from .forms import LoginForm, VerifyForm, AvatarUploadForm, TopicCreateForm, ReplyCreateForm

from urllib.parse import urlencode


class IndexView(TemplateView):
    template_name = 'djforum/views/index.djhtml'

    def get_context_data(self, **kwargs):
        toptopics = TopTopic.objects.all()
        topics = Topic.objects.order_by('-date_updated')[:20]
        return {'toptopics': toptopics, 'topics': topics}


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'djforum/views/forms/login.djhtml'

    def form_valid(self, form):
        self.login_type = self.request.POST['login_type']
        if self.login_type == 'login':
            form.login(self.request)
        else:
            self.verify_pk = form.verify()
        return super().form_valid(form)

    def get_success_url(self):
        if self.login_type == 'login':
            next = self.request.GET.get('next')
            return next if next else reverse('djforum:index')
        else:
            return reverse('djforum:verify', args=(self.verify_pk, )) + \
                '?' + self.request.GET.urlencode()


class VerifyView(FormView):
    form_class = VerifyForm
    template_name = 'djforum/views/forms/verify.djhtml'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.verify_pk = self.kwargs['pk']
        return form

    def form_valid(self, form):
        form.do_action()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:login') + \
            '?' + self.request.GET.urlencode()


class LogoutView(RedirectView):
    url = reverse_lazy('djforum:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class UserDetailView(DetailView):
    model = User
    template_name = 'djforum/views/user_detail.djhtml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = UserProfile.get_profile(self.object)
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['website', 'introduction']
    template_name = 'djforum/views/forms/userprofile_update.djhtml'
    login_url = reverse_lazy('djforum:login')

    def get_object(self, queryset=None):
        return UserProfile.get_profile(self.request.user)

    def get_success_url(self):
        return reverse('djforum:user-detail', args=(self.request.user.pk, ))


@require_GET
def get_avatar(request, pk):
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
    login_url = reverse_lazy('djforum:login')

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:user-detail', args=(self.request.user.pk, ))


class SectionListView(ListView):
    template_name = 'djforum/views/section_list.djhtml'
    paginate_by = 50

    def get_queryset(self):
        qs = Section.objects.all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('-count_topics')

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
        qs = Topic.objects.all()
        section_name = self.request.GET.get('section')
        if section_name:
            section = get_object_or_404(Section, name=section_name)
            qs = qs.filter(section=section)
        return qs.order_by('-date_updated')

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
        return self.object.reply_set.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.object
        return context


class TopicCreateView(LoginRequiredMixin, FormView):
    form_class = TopicCreateForm
    template_name = 'djforum/views/forms/topic_create.djhtml'
    login_url = reverse_lazy('djforum:login')

    def get_initial(self):
        initial = super().get_initial()
        section = self.request.GET.get('section')
        if section:
            initial['section'] = section
        return initial

    def form_valid(self, form):
        self.section = form.save(self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:topic-list') + \
            '?' + urlencode({'section': self.section or ''})


class ReplyCreateView(LoginRequiredMixin, FormView):
    form_class = ReplyCreateForm
    template_name = 'djforum/views/forms/reply_create.djhtml'
    login_url = reverse_lazy('djforum:login')

    def form_valid(self, form):
        topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        form.save(self.request, topic)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('djforum:topic-detail', args=(self.kwargs['pk'], ))
