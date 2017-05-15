from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse_lazy
from reversion.models import Version

from core.models import Comment, CommentRelation, CommentRelatedModelMixin, \
    CommentHistoryExport


class CreateRetrieveCommentSerializer(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source='type.id', read_only=True)
    ancestor_type_id = serializers.IntegerField(
        source='nearest_relation.ancestor_type_id')
    ancestor_id = serializers.IntegerField(
        source='nearest_relation.ancestor_id')

    class Meta:
        model = Comment
        fields = ('id', 'type_id', 'created_dt', 'updated_dt', 'author', 'text',
                  'ancestor_type_id', 'ancestor_id')
        read_only_fields = ('id', 'type_id', 'created_dt', 'updated_dt')

    def validate(self, attrs):
        attrs['ancestor'] = self.get_ancestor_or_raise_error(
            **attrs.pop('nearest_relation'))
        return super().validate(attrs)

    def get_ancestor_or_raise_error(self, ancestor_type_id, ancestor_id):
        try:
            ancestor_ct = ContentType.objects.get_for_id(ancestor_type_id)
            if not issubclass(ancestor_ct.model_class(), CommentRelatedModelMixin):
                raise ValidationError({'ancestor': _(
                    'Object of this kind can not be related in comments')})
            return ancestor_ct.get_object_for_this_type(pk=ancestor_id)
        except ObjectDoesNotExist:
            raise ValidationError({'ancestor': _('Not found')})


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)


class CommentHistoryExportSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = CommentHistoryExport
        fields = ('id', 'request_user', 'mime_type', 'file')
        read_only_fields = fields

    def get_file(self, instance):
        return reverse_lazy('comment-history-export-file',
                            request=self.context['request'],
                            kwargs={'pk': instance.id})


class CommentRelationSerializer(serializers.ModelSerializer):
    comment = CreateRetrieveCommentSerializer()
    root_ancestor_type_id = serializers.IntegerField(source='ancestor_type_id')
    root_ancestor_id = serializers.IntegerField(source='ancestor_id')

    class Meta:
        model = CommentRelation
        fields = ('root_ancestor_id', 'root_ancestor_type_id', 'comment',
                  'depth')
        read_only_fields = fields


class CommentRevisionSerializer(serializers.ModelSerializer):
    created_dt = serializers.DateTimeField(source='revision.date_created')
    user_id = serializers.IntegerField(source='revision.user_id')
    fields = serializers.JSONField(source='field_dict')

    class Meta:
        model = Version
        fields = ('id', 'fields', 'created_dt', 'user_id')
        read_only_fields = fields
