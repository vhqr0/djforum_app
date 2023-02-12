from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import LikeTopic, LikeReply

from datetime import timedelta


class Command(BaseCommand):
    help = ('DJForum: clear topic/reply likes long than 30 days.')

    def handle(self, *args, **kwargs):
        dt = timezone.now() - timedelta(days=30)
        LikeTopic.objects.filter(date_created__lt=dt).delete()
        LikeReply.objects.filter(date_created__lt=dt).delete()
        self.stdout.write(
            self.style.SUCCESS('Successfully clear DJForum data.'))
