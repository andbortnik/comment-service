from django.db import connection
from django.db.models.manager import QuerySet


class CommentQuerySet(QuerySet):
    def create(self, author, text, ancestor):
        from core.models import CommentRelation
        comment = super().create(author=author, text=text)
        comment.nearest_relation = CommentRelation.objects.create_for_comment(
            ancestor=ancestor, comment=comment)
        comment.save()
        return comment


class CommentRelationQuerySet(QuerySet):
    def create_for_comment(self, ancestor, comment):
        from core.models import Comment
        if isinstance(ancestor, Comment):
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO core_commentrelation '
                    '   (ancestor_id, ancestor_type_id, depth, comment_id) '
                    'SELECT'
                    '   ancestor_id, ancestor_type_id, depth + 1, %s '
                    'FROM core_commentrelation '
                    'WHERE comment_id = %s ',
                    (comment.id, ancestor.id)
                )
            nearest_relation = self.get(ancestor_type=ancestor.type,
                                        ancestor_id=ancestor.id,
                                        comment=comment, depth=1)
        else:
            nearest_relation = self.create(ancestor=ancestor, comment=comment,
                                           depth=1)
        self.create(ancestor=comment, comment=comment, depth=0)
        return nearest_relation
