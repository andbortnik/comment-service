from rest_framework import routers

from api.viewsets import (CommentViewSet, CommentRelationViewSet,
                          CommentHistoryExportViewSet)

router = routers.DefaultRouter()
router.register(r'comments/tree', CommentRelationViewSet,
                base_name='comment-tree')
router.register(r'comments/history_export', CommentHistoryExportViewSet,
                base_name='comment-history-export')
router.register(r'comments', CommentViewSet, base_name='comment')
urlpatterns = router.get_urls()
