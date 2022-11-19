from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import VerifyRecord, LikeTopic, LikeReply

from datetime import timedelta


class Command(BaseCommand):
    help = ('DJForum: clear the verify records and topic/reply likes'
            ' long than 30 days.')

    def handle(self, *args, **kwargs):
        dt = timezone.now() - timedelta(days=30)
        VerifyRecord.objects.filter(time_sent__lt=dt).delete()
        LikeTopic.objects.filter(date_created__lt=dt).delete()
        LikeReply.objects.filter(date_created__lt=dt).delete()
        self.stdout.write(
            self.style.SUCCESS('Successfully clear DJForum data.'))
