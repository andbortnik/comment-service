from unittest import mock

from rest_framework import status

from api.tests.base import (COMMENT_ID_TEMPLATE_URL, COMMENTS_URL,
                            BaseRetrieveAPITestCase)
from core.models import CommentSubscription, Comment


class CommentSubscriptionCommentTestCase(BaseRetrieveAPITestCase):
    def setUp(self):
        super().setUp()
        CommentSubscription.objects.create(user=self.user,
                                           object=self.article)

    def _api_update_comment(self, comment, data):
        return self.client.patch(
            COMMENT_ID_TEMPLATE_URL.format(comment.id), data, format='json')

    def test_comment_subscription_on_change(self):
        with mock.patch('core.signal_handlers.'
                        'notify_user_on_comment_change') as notify_mock:
            response = self.client.patch(
                COMMENT_ID_TEMPLATE_URL.format(self.comment_1.id),
                {'text': 'new text', 'request_user_id': self.user.id},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(notify_mock.call_count, 1)

    def test_comment_subscription_on_create(self):
        with mock.patch('core.signal_handlers.'
                        'notify_user_on_comment_change') as notify_mock:
            response = self.client.post(
                COMMENTS_URL, {
                    'author': self.user.id,
                    'text': 'text',
                    'ancestor_type_id': self.article.type.id,
                    'ancestor_id': self.article.id
                },
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(notify_mock.call_count, 1)

    def test_comment_subscription_on_delete(self):
        comment = Comment.objects.create(self.user, 'text', self.article)
        with mock.patch('core.signal_handlers.'
                        'notify_user_on_comment_change') as notify_mock:
            response = self.client.delete(
                COMMENT_ID_TEMPLATE_URL.format(comment.id),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(notify_mock.call_count, 1)
