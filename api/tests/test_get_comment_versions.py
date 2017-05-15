from django.core import management
from rest_framework import status

from api.tests.base import (COMMENT_ID_TEMPLATE_URL,
                            COMMENT_TEXT,
                            COMMENT_ID_VERSIONS_TEMPLATE_URL,
                            BaseRetrieveAPITestCase)


class GetCommentVersionsTestCase(BaseRetrieveAPITestCase):
    def setUp(self):
        super().setUp()
        management.call_command('createinitialrevisions')
        self.new_text = 'new text'
        self.client.patch(COMMENT_ID_TEMPLATE_URL.format(self.comment_1.id), {
            'text': self.new_text,
            'request_user_id': self.user.id,
        }, format='json')
        self.comment_1.refresh_from_db()

    def _api_get_comment_by_id(self, comment, **kwargs):
        return self.client.get(COMMENT_ID_TEMPLATE_URL.format(comment.id),
                               kwargs)

    def test_get_comment_versions(self):
        response = self.client.get(
            COMMENT_ID_VERSIONS_TEMPLATE_URL.format(self.comment_1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        texts = set(r['fields']['text'] for r in response.data)
        self.assertEqual(texts, {COMMENT_TEXT, self.new_text})
