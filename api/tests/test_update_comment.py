from rest_framework import status

from api.tests.base import (BaseAPITestCase, COMMENT_TEXT,
                            COMMENT_ID_TEMPLATE_URL)
from core.models import Comment


class UpdateCommentTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.create(self.user, COMMENT_TEXT,
                                              self.article)
        self.new_text = 'new text'

    def _api_update_comment(self, comment, data):
        return self.client.patch(
            COMMENT_ID_TEMPLATE_URL.format(comment.id), data, format='json')

    def test_update_comment_text(self):
        response = self._api_update_comment(self.comment,
                                            {'text': self.new_text,
                                             'request_user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.new_text)

    def test_cannot_update_comment_without_request_user(self):
        response = self._api_update_comment(self.comment,
                                            {'text': self.new_text})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
