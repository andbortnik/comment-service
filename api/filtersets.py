from django_filters.rest_framework import FilterSet, NumberFilter

from core.models import Comment, CommentRelation


class CommentFilterSet(FilterSet):
    ancestor_type_id = NumberFilter(name='nearest_relation__ancestor_type_id')
    ancestor_id = NumberFilter(name='nearest_relation__ancestor_id')

    class Meta:
        model = Comment
        fields = {
            'author': ('exact',),
            'ancestor_type_id': ('exact',),
            'ancestor_id': ('exact',),
            'created_dt': ('exact', 'gt', 'lt', 'gte', 'lte'),
        }
        together = ('ancestor_type_id', 'ancestor_id')


class CommentRelationFilterSet(FilterSet):
    root_ancestor_type_id = NumberFilter(name='ancestor_type')
    root_ancestor_id = NumberFilter(name='ancestor_id')
    root_comment_id = NumberFilter(name='comment_id',
                                   method='filter_by_comment_id')

    class Meta:
        model = CommentRelation
        fields = ('depth', 'root_ancestor_type_id', 'root_ancestor_id',
                  'root_comment_id')
        together = ('root_ancestor_type_id', 'root_ancestor_id')

    def filter_by_comment_id(self, queryset, field_name, comment_id):
        ancestor_comment = Comment.objects.get(pk=comment_id)
        return queryset.filter(ancestor_type=ancestor_comment.type,
                               ancestor_id=ancestor_comment.id)
