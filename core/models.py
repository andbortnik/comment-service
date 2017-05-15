import reversion
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import (ForeignKey, PositiveIntegerField, FileField,
                              CharField)
from django.db.models import TextField, CASCADE, DateTimeField
from django.utils.timezone import now
from reversion.models import Version

from core.managers import CommentRelationQuerySet, CommentQuerySet


class CommentRelatedModelMixin(object):
    @property
    def type(self):
        return ContentType.objects.get_for_model(self)


@reversion.register(fields=('updated_dt', 'text'))
class Comment(CommentRelatedModelMixin, models.Model):
    created_dt = DateTimeField(auto_now_add=True, null=False, blank=True,
                               db_index=True)
    updated_dt = DateTimeField(auto_now=True, null=False, blank=True)
    author = ForeignKey(User, on_delete=CASCADE, related_name='comments',
                        related_query_name='comment', null=False, blank=False)
    text = TextField(null=False, blank=False)
    nearest_relation = ForeignKey('CommentRelation', related_name='+',
                                  null=True, blank=True)
    versions = GenericRelation(Version, related_name='comments',
                               related_query_name='comment')

    objects = CommentQuerySet.as_manager()


class CommentRelation(models.Model):
    ancestor_type = ForeignKey(ContentType)
    ancestor_id = PositiveIntegerField()
    ancestor = GenericForeignKey('ancestor_type', 'ancestor_id')
    comment = ForeignKey('Comment', on_delete=CASCADE,
                         related_name='relations',
                         related_query_name='relation', null=False,
                         blank=False)
    depth = PositiveIntegerField(default=0, null=False, blank=True,
                                 db_index=True)

    objects = CommentRelationQuerySet.as_manager()

    class Meta:
        index_together = ('ancestor_type', 'ancestor_id')


class CommentHistoryExport(models.Model):
    request_user = ForeignKey(User, null=False, blank=False)
    mime_type = CharField(max_length=127,
                          null=False, blank=False, db_index=True)
    file = FileField(upload_to='media/comment_history_dump/')


class CommentSubscription(models.Model):
    user = ForeignKey(User, null=False, blank=False)
    object_id = PositiveIntegerField()
    object_type = ForeignKey(ContentType)
    object = GenericForeignKey('object_type', 'object_id')

    class Meta:
        index_together = ('object_type', 'object_id')


class Article(CommentRelatedModelMixin, models.Model):
    """
    Just as example
    """
    created_dt = DateTimeField(default=now, null=False, blank=True)
    updated_dt = DateTimeField(default=now, null=False, blank=True)
    author = ForeignKey(User, on_delete=CASCADE, null=False, blank=False)
    text = TextField(null=False, blank=False)
