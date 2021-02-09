from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect

from ifns.handlers import IFNSHandler
from ifns.models import Setting, Requisites, PreviousConfig

admin.site.register(Setting)
admin.site.register(PreviousConfig)


@admin.register(Requisites)
class DownloadRequisitesAdmin(admin.ModelAdmin):
    change_list_template = "admin/load_ifns.html"

    def get_urls(self):
        urls = super(DownloadRequisitesAdmin, self).get_urls()
        custom_urls = [url('^ifns_download/$', self.process_download, name='process_download')]
        return custom_urls + urls

    def process_download(self, request):
        handler = IFNSHandler()
        handler.run()
        self.message_user(
            request,
            'создано {} новых записей, обновлено {} записей'.format(handler.load_count, handler.update_count),
        )
        return HttpResponseRedirect("../")
