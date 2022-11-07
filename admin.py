from django.contrib import admin

from .models import VerifyRecord, Section, Topic, TopTopic, Reply


class TopicInline(admin.StackedInline):
    model = Topic


class SectionAdmin(admin.ModelAdmin):
    inlines = [TopicInline]


class ReplyInline(admin.StackedInline):
    model = Reply


class TopicAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]


admin.site.register(VerifyRecord)
admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TopTopic)
