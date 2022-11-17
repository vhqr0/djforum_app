from django.urls import path

from .views import IndexView, LoginView, VerifyView, logout_view, \
    UserDetailView, UserProfileUpdateView, avatar, AvatarUploadView, \
    SectionListView, TopicListView, TopicDetailView, \
    TopicCreateView, ReplyCreateView, topic_like, reply_like

app_name = 'djforum'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/<int:pk>/', VerifyView.as_view(), name='verify'),
    path('logout/', logout_view, name='logout'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('userprofile-update/',
         UserProfileUpdateView.as_view(),
         name='userprofile-update'),
    path('avatar/<int:pk>/', avatar, name='avatar'),
    path('avatar-upload/', AvatarUploadView.as_view(), name='avatar-upload'),
    path('section/', SectionListView.as_view(), name='section-list'),
    path('topic/', TopicListView.as_view(), name='topic-list'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topic-create/', TopicCreateView.as_view(), name='topic-create'),
    path('reply-create/<int:pk>/',
         ReplyCreateView.as_view(),
         name='reply-create'),
    path('topic-like/<int:pk>/', topic_like, name='topic-like'),
    path('reply-like/<int:pk>/', reply_like, name='reply-like'),
]
