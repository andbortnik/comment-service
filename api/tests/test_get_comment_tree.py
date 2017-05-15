from rest_framework import status

from api.tests.base import COMMENTS_TREE_URL, BaseRetrieveAPITestCase


def get_id_set(data):
    return set(comm['id'] for comm in data)


class GetCommentTreeTestCase(BaseRetrieveAPITestCase):
    def _api_get_comment_tree(self, **kwargs):
        return self.client.get(COMMENTS_TREE_URL, kwargs)

    def test_get_descendants_by_root_comment_id(self):
        response = self._api_get_comment_tree(root_comment_id=self.comment_2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        comment_ids = set(relation['comment']['id']
                          for relation in response.data)
        self.assertEqual(comment_ids,
                         {self.comment_2.id, self.comment_3.id,
                          self.comment_4.id})

    def test_get_descendants_by_root_ancestor(self):
        response = self._api_get_comment_tree(
            root_ancestor_id=self.article.id,
            root_ancestor_type_id=self.article.type.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        comment_ids = set(relation['comment']['id']
                          for relation in response.data)
        self.assertEqual(comment_ids,
                         {self.comment_1.id, self.comment_2.id,
                          self.comment_3.id, self.comment_4.id})

    def test_get_descendants_fields(self):
        response = self._api_get_comment_tree(root_comment_id=self.comment_2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        relation = response.data[0]
        self.assertIn('root_ancestor_id', relation)
        self.assertIn('root_ancestor_type_id', relation)
        self.assertIn('depth', relation)

        comment = relation['comment']
        self.assertIn('ancestor_type_id', comment)
        self.assertIn('ancestor_id', comment)
        self.assertIn('type_id', comment)
        self.assertIn('id', comment)
        self.assertIn('author', comment)
        self.assertIn('text', comment)
        self.assertIn('updated_dt', comment)
        self.assertIn('created_dt', comment)
