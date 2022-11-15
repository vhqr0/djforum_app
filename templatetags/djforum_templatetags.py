from django import template

from ..models import Topic, Reply

register = template.Library()


@register.inclusion_tag('djforum/tags/reply_reference.djhtml')
def reply_reference(self_reply):
    reference_topic = self_reply.reference_topic
    reference_floor = self_reply.reference_floor
    self_topic = self_reply if isinstance(self_reply, Topic) else self_reply.topic

    context = {
        'topic': None,
        'reply': None,
        'is_top': False,
        'is_cross': False,
        'is_missing': False,
    }

    if not reference_topic:     # dont have reference
        return context

    if reference_topic == self_topic.pk: # in-topic reference
        context['topic'] = self_topic

    else:                       # cross reference
        context['is_cross'] = True
        topics = Topic.objects.filter(pk=reference_topic)

        if topics.count() == 0:     # missing topic
            context['is_missing'] = True
            return context

        context['topic'] = topics[0]

    if not reference_floor:     # refer to topic
        context['is_top'] = True
        context['reply'] = context['topic']
        return context

    replies = context['topic'].reply_set.filter(count_replies=reference_floor)

    if replies.count() == 0:    # missing reply
        context['is_missing'] = True
        return context

    context['reply'] = replies[0]

    return context
