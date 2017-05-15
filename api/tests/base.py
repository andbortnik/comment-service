from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from core.models import Article, Comment

ROOT_URL = '/'
API_URL = ROOT_URL + 'api/'
COMMENTS_URL = API_URL + 'comments/'
COMMENT_ID_TEMPLATE_URL = COMMENTS_URL + '{}/'
COMMENT_ID_VERSIONS_TEMPLATE_URL = COMMENT_ID_TEMPLATE_URL + 'versions/'
COMMENTS_TREE_URL = COMMENTS_URL + 'tree/'
COMMENTS_HISTORY_EXPORT_URL = COMMENTS_URL + 'history_export/'
COMMENTS_HISTORY_EXPORT_ID_TEMPLATE_URL = COMMENTS_HISTORY_EXPORT_URL + '{}/'
COMMENTS_HISTORY_EXPORT_ID_FILE_TEMPLATE_URL = (
    COMMENTS_HISTORY_EXPORT_ID_TEMPLATE_URL + 'file/')
COMMENT_TEXT = 'comment text'


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='test_user')
        self.second_user = User.objects.create(username='second_user')
        self.article = Article.objects.create(author=self.user,
                                              text='article text')
        self.second_article = Article.objects.create(author=self.user,
                                                     text='article text')
        self.article_ct = ContentType.objects.get_for_model(self.article)


class BaseRetrieveAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.comment_1 = Comment.objects.create(self.user, COMMENT_TEXT,
                                                self.article)
        self.comment_2 = Comment.objects.create(self.user, COMMENT_TEXT,
                                                self.article)
        self.comment_3 = Comment.objects.create(self.user, COMMENT_TEXT,
                                                self.comment_2)
        self.comment_4 = Comment.objects.create(self.user, COMMENT_TEXT,
                                                self.comment_3)

        self.comment_5 = Comment.objects.create(self.second_user, COMMENT_TEXT,
                                                self.second_article)
        self.comment_6 = Comment.objects.create(self.second_user, COMMENT_TEXT,
                                                self.comment_5)


def get_id_set(data):
    return set(comm['id'] for comm in data)
