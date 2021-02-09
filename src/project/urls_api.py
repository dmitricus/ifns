from appversion.views import VersionAPIView
from django.conf.urls import url

from ifns.views import GetIfnsRequisitesByCode

urlpatterns = [
    url(
        r'^get_ifns_requisites_by_code/(?P<code>[A-Za-z0-9]+)/$',
        GetIfnsRequisitesByCode.as_view(),
        name='get_ifns_requisites_by_code'
    ),
    url(r'^version/$', VersionAPIView.as_view(), name='version'),
]
