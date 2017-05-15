import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from core.models import Comment, CommentSubscription

logger = logging.getLogger(__name__)


@receiver([post_save, pre_delete], sender=Comment)
def on_coment_change(instance, **kwargs):
    if instance.nearest_relation is None:
        return
    ancestor = instance.nearest_relation.ancestor
    subscriptions = CommentSubscription.objects.select_related('user').filter(
        object_type=ancestor.type,
        object_id=ancestor.id)
    for subscription in subscriptions:
        notify_user_on_comment_change(subscription.user, instance)


def notify_user_on_comment_change(user, comment):
    """
    TODO: implement user push notification
    """
    logger.info('Notifying user id {} on comment id {} change'.format(
        user.id, comment.id))
