from rest_framework import status

from api.tests.base import (COMMENTS_HISTORY_EXPORT_URL, COMMENTS_URL,
                            BaseRetrieveAPITestCase)


class GetCommentExportTestCase(BaseRetrieveAPITestCase):
    """
    Only json export data format tested. 
    Didn't figure out how to set `Accept` header.
    """
    def _api_get_comments(self, **kwargs):
        return self.client.get(COMMENTS_URL, kwargs)

    def test_export_comments_by_author(self):
        response = self.client.get(
            COMMENTS_URL, {
                'author': self.second_user.id,
                'dump': 1,
                'request_user_id': self.user.id
            })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        file_response = self.client.get(response.url)
        self.assertEqual(file_response.status_code, status.HTTP_200_OK)

        exports_response = self.client.get(COMMENTS_HISTORY_EXPORT_URL,
                                           {'user': self.user.id})
        self.assertEqual(exports_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(exports_response.data), 1)
        export = exports_response.data[0]
        self.assertEqual(export['request_user'], self.user.id)

        redownload_file_response = self.client.get(export['file'])
        self.assertEqual(redownload_file_response.status_code, status.HTTP_200_OK)
        self.assertEqual(file_response.json(), redownload_file_response.json())
