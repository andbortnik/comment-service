from rest_framework import status

from api.tests.base import COMMENT_ID_TEMPLATE_URL, BaseRetrieveAPITestCase


class DeleteCommentTestCase(BaseRetrieveAPITestCase):
    def test_delete_comment_by_id(self):
        response = self.client.delete(
            COMMENT_ID_TEMPLATE_URL.format(self.comment_4.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_comment_with_descendants(self):
        response = self.client.delete(
            COMMENT_ID_TEMPLATE_URL.format(self.comment_3.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
