from django import template
from django.urls import reverse

from ..models import Topic

from urllib.parse import urlencode

register = template.Library()


@register.inclusion_tag('djforum/tags/reply_reference.djhtml')
def reply_reference(self_reply, self_topic):
    reference_topic = self_reply.reference_topic
    reference_floor = self_reply.reference_floor

    context = {
        'topic': None,
        'reply': None,
        'is_top': False,
        'is_cross': False,
        'is_missing': False,
    }

    if not reference_topic:  # dont have reference
        return context

    if reference_topic == self_topic.pk:  # in-topic reference
        context['topic'] = self_topic

    else:  # cross reference
        context['is_cross'] = True
        topics = Topic.objects.filter(pk=reference_topic)

        if topics.count() == 0:  # missing topic
            context['is_missing'] = True
            return context

        context['topic'] = topics[0]

    if not reference_floor:  # refer to topic
        context['is_top'] = True
        context['reply'] = context['topic']
        return context

    replies = context['topic'].reply_set.filter(count_replies=reference_floor)

    if replies.count() == 0:  # missing reply
        context['is_missing'] = True
        return context

    context['reply'] = replies[0]

    return context


@register.simple_tag
def reply_floor(reply, is_top):
    floor = 0 if is_top else reply.count_replies
    return '#' + str(floor)


@register.simple_tag
def topic_create_url_with_ref(topic, reply=None):
    params = {'reference_topic': topic.pk}
    if topic.section:
        params['section'] = topic.section
    if reply:
        params['reference_floor'] = reply.count_replies
    return reverse('djforum:topic-create') + '?' + urlencode(params)


@register.simple_tag
def reply_create_url_with_ref(topic, reply=None):
    params = {'reference_topic': topic.pk}
    if reply:
        params['reference_floor'] = reply.count_replies
    return reverse('djforum:reply-create',
                   args=(topic.pk, )) + '?' + urlencode(params)


@register.simple_tag
def reply_ref(topic, reply, is_top):
    if is_top:
        return reply_create_url_with_ref(topic)
    else:
        return reply_create_url_with_ref(topic, reply)


@register.simple_tag
def reply_cross_ref(topic, reply, is_top):
    if is_top:
        return topic_create_url_with_ref(topic)
    else:
        return topic_create_url_with_ref(topic, reply)


@register.simple_tag
def reply_like_url(reply, is_top):
    if is_top:
        return reverse('djforum:topic-like', args=(reply.pk, ))
    else:
        return reverse('djforum:reply-like', args=(reply.pk, ))
