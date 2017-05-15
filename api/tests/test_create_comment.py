from rest_framework import status

from api.tests.base import BaseAPITestCase, COMMENTS_URL, COMMENT_TEXT


class CreateCommentTestCase(BaseAPITestCase):
    def _api_create_comment(self, data):
        return self.client.post(COMMENTS_URL, data, format='json')

    def test_create_comment(self):
        response = self._api_create_comment({
            'author': self.user.id,
            'text': COMMENT_TEXT,
            'ancestor_type_id': self.article.type.id,
            'ancestor_id': self.article.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cant_create_without_ancestor(self):
        response = self._api_create_comment({
            'author': self.user.id,
            'text': COMMENT_TEXT,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_create_without_author(self):
        response = self._api_create_comment({
            'text': COMMENT_TEXT,
            'ancestor_type_id': self.article.type.id,
            'ancestor_id': self.article.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_create_with_nonexistent_author(self):
        response = self._api_create_comment({
            'author': -1,
            'text': COMMENT_TEXT,
            'ancestor_type_id': self.article.type.id,
            'ancestor_id': self.article.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
