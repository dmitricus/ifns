from django.shortcuts import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ifns.models import Requisites
from ifns.serializers import RequisitesSerializer, CodeIfnsSerializer


class GetIfnsRequisitesByCode(APIView):
    """Метод получения реквизитов ИФНС."""
    renderer_classes = (JSONRenderer,)
    serializer_class = RequisitesSerializer

    def get(self, request, **kwargs):
        param_serializer = CodeIfnsSerializer(data=kwargs)
        param_serializer.is_valid(raise_exception=True)
        code = param_serializer.validated_data.get('code')
        requisites = get_object_or_404(Requisites, nalog_code=code)
        if requisites:
            serializer = self.serializer_class(requisites)
            return Response(status=200, data=serializer.data)
