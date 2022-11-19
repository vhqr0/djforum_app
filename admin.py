from django.contrib import admin

from .models import VerifyRecord, Topic, TopTopic, Reply


@admin.register(VerifyRecord)
class VerifyRecordAdmin(admin.ModelAdmin):
    date_hierarchy = 'time_sent'
    readonly_fields = (
        'email',
        'time_sent',
        'verify_type',
        'verify_code',
        'username',
        'password',
    )
    fieldsets = (
        (
            None,
            {
                'fields': ('email', 'verify_type', 'time_sent'),
            },
        ),
        (
            'Detail',
            {
                'classes': ('collapse', ),
                'fields': ('verify_code', 'username', 'password'),
            },
        ),
    )
    list_display = ('email', 'verify_type', 'time_sent')
    list_filter = ('verify_type', 'time_sent')


@admin.register(TopTopic)
class TopTopicAdmin(admin.ModelAdmin):
    date_hierarchy = 'topic__date_created'


class ReplyInline(admin.StackedInline):
    model = Reply
    extra = 0
    readonly_fields = (
        'user',
        'date_created',
        'reference_topic',
        'reference_floor',
    )
    fieldsets = (
        (
            None,
            {
                'fields': (('user', 'date_created'), )
            },
        ),
        (
            'Detail',
            {
                'classes': ('collapse', ),
                'fields': (('reference_topic', 'reference_floor'), 'content'),
            },
        ),
    )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    inlines = (ReplyInline, )
    date_hierarchy = 'date_created'
    readonly_fields = ('user', 'section')
    fieldsets = (
        (
            None,
            {
                'fields': ('section', 'title', 'keywords', 'user'),
            },
        ),
        (
            'Detail',
            {
                'classes': ('collapse', ),
                'fields': (('reference_topic', 'reference_floor'), 'content'),
            },
        ),
    )
    list_display = ('title', 'section', 'user', 'date_updated', 'date_created')
    list_filter = ('section', 'user', 'date_updated', 'date_created')
    search_fields = ('title', 'keywords')
    search_help_text = ('Magic search, # for user, @ for topic id, '
                        'or else for title and keyword.')
    actions = ('set_top', )

    def get_search_results(self, result, queryset, search_term):
        """
        Magic search with magic prefix.
        # for search specific user.
        @ for search specific topic.
        Or else use default search results.
        """
        if len(search_term) == 0:
            return super().get_search_results(result, queryset, search_term)
        magic = search_term[0]
        if magic == '#':  # for user
            qs = Topic.filter_by_username(search_term[1:])
            if qs is None:
                return super().get_search_results(result, queryset, '')
            else:
                return qs, False
        elif magic == '@':  # for topic
            return Topic.objects.filter(pk=search_term[1:]), False
        else:
            return super().get_search_results(result, queryset, search_term)

    @admin.action(description='Set selected topics as toptopics')
    def set_top(self, request, queryset):
        for topic in queryset:
            TopTopic.set_top(topic)
