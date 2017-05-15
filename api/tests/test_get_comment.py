from rest_framework import status

from api.tests.base import (COMMENTS_URL, COMMENT_ID_TEMPLATE_URL,
                            BaseRetrieveAPITestCase, get_id_set)


class GetCommentTestCase(BaseRetrieveAPITestCase):
    def _api_get_comment_by_id(self, comment, data=None):
        return self.client.get(COMMENT_ID_TEMPLATE_URL.format(comment.id), data)

    def _api_get_comments(self, **kwargs):
        return self.client.get(COMMENTS_URL, kwargs)

    def test_get_comment_by_id(self):
        response = self._api_get_comment_by_id(self.comment_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.comment_1.id)

    def test_get_first_level_comments_by_ancestor(self):
        response = self._api_get_comments(ancestor_type_id=self.article.type.id,
                                          ancestor_id=self.article.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_id_set(response.data),
                         {self.comment_1.id, self.comment_2.id})

    def test_get_first_level_comments_by_ancestor_with_pagination(self):
        response = self._api_get_comments(ancestor_type_id=self.article.type.id,
                                          ancestor_id=self.article.id,
                                          limit=1, offset=0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(get_id_set(response.data['results']),
                         {self.comment_1.id})

        next_response = self.client.get(response.data['next'])
        self.assertEqual(next_response.status_code, status.HTTP_200_OK)
        self.assertEqual(next_response.data['count'], 2)
        self.assertEqual(get_id_set(next_response.data['results']),
                         {self.comment_2.id})

    def test_get_comment_history_by_user(self):
        response = self._api_get_comments(author=self.second_user.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_id_set(response.data),
                         {self.comment_5.id, self.comment_6.id})
