import uuid
from os.path import basename

import reversion
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.status import HTTP_200_OK
from rest_framework_xml.renderers import XMLRenderer

from api.filtersets import CommentRelationFilterSet, CommentFilterSet
from api.serializers import (CreateRetrieveCommentSerializer,
                             CommentRelationSerializer, UpdateCommentSerializer,
                             CommentHistoryExportSerializer,
                             CommentRevisionSerializer)
from core.models import Comment, CommentRelation, CommentHistoryExport


class CommentViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    renderer_classes = [JSONRenderer, XMLRenderer]
    queryset = Comment.objects.select_related('nearest_relation').all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentFilterSet

    @detail_route(methods=['get'])
    def versions(self, request, pk):
        instance = self.get_object()
        serializer = CommentRevisionSerializer(instance.versions.all(),
                                               many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UpdateCommentSerializer
        else:
            return CreateRetrieveCommentSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.redirect_to_dump(request, response) or response

    def update(self, request, *args, **kwargs):
        request_user = self.get_request_user_or_raise_error(request)
        with reversion.create_revision():
            reversion.set_user(request_user)
            return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        self.validate_no_descentants(instance)
        super().perform_destroy(instance)

    def redirect_to_dump(self, request, response):
        dump_to_file = request.GET.get('dump')
        request_user_id = request.GET.get('request_user_id')
        if dump_to_file and request_user_id and response.status_code == HTTP_200_OK:
            response = self.finalize_response(request, response)
            mime_type = response.accepted_media_type
            extension = response.accepted_renderer.format
            file = ContentFile(response.rendered_content,
                               '{}.{}'.format(uuid.uuid4(), extension))
            dump_instance = CommentHistoryExport.objects.create(
                request_user_id=request_user_id,
                mime_type=mime_type,
                file=file)
            return redirect(
                reverse_lazy('comment-history-export-file', request=request,
                             kwargs={'pk': dump_instance.pk}))
        return None

    def validate_no_descentants(self, instance):
        if CommentRelation.objects.filter(ancestor_type=instance.type,
                                          ancestor_id=instance.id,
                                          depth__gt=0).exists():
            raise ValidationError(
                _('Unable to delete comment with descendants'))

    def get_request_user_or_raise_error(self, request):
        try:
            return User.objects.get(pk=request.data.get('request_user_id'))
        except User.DoesNotExist:
            raise ValidationError({'request_user_id': _('Not found')})


class CommentHistoryExportViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    renderer_classes = [JSONRenderer, XMLRenderer]
    queryset = CommentHistoryExport.objects.all()
    serializer_class = CommentHistoryExportSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('request_user', 'mime_type')

    @detail_route(methods=['get'])
    def file(self, request, pk):
        instance = self.get_object()
        response = HttpResponse(content=instance.file.read(),
                                content_type=instance.mime_type)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            basename(instance.file.name))
        return response


class CommentRelationViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = CommentRelation.objects.select_related(
        'comment', 'comment__nearest_relation').all()
    serializer_class = CommentRelationSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentRelationFilterSet
