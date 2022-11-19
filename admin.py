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
        ('Detail', {
            'classes': ('collapse', ),
            'fields': (('reference_topic', 'reference_floor'), 'content'),
        }),
    )


@admin.action(description='Set Top')
def set_top(modeladmin, request, queryset):
    for topic in queryset:
        TopTopic.set_top(topic)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]
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
    actions = [set_top]
