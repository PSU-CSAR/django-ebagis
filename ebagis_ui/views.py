from django.views import generic
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from djcelery.models import TaskMeta

from ebagis.data.models.aoi import AOI
from ebagis.models.upload import Upload
from ebagis.models.download import Download
from ebagis.tasks import export_data


class AOIDetailsView(generic.DetailView):
    template_name = 'aois/details.html'
    queryset = AOI.objects.all()

    def post(self, request, *args, **kwargs):
        if 'action_download' in request.POST:
            return self._action_download(request)

    def _action_download(self, request):
            download = Download(
                user=request.user,
                content_type=ContentType.objects.get(
                    id=request.POST['content_type']
                ),
                object_id=request.POST['object_id'],
                name=request.POST['object_name'],
            )
            download.save()
            result = export_data.delay(str(download.pk))
            download.task, created = \
                TaskMeta.objects.get_or_create(task_id=result.task_id)
            download.save()
            messages.add_message(
                request,
                messages.INFO,
                mark_safe(('AOI download request submitted successfully. '
                           '<a href="{}">View your download requests here.</a>'
                           .format(reverse('account_requests_download')))),
            )
            return HttpResponseRedirect(request.path)


class DownloadRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'downloadrequests.html'
    success_url = reverse_lazy('account_requests_download')

    def get_context_data(self, **kwargs):
        context = super(DownloadRequestView, self).get_context_data(**kwargs)
        context['downloads'] = Download.objects.filter(user=self.request.user).order_by('-created_at')
        context['processing_states'] = ['PENDING', 'RETRY', 'STARTED']
        context['cancelled_states'] = ['ABORTED', 'REVOKED']
        return context


class UploadRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'uploadrequests.html'
    success_url = reverse_lazy('account_requests_upload')

    def get_context_data(self, **kwargs):
        context = super(UploadRequestView, self).get_context_data(**kwargs)
        context['uploads'] = Upload.objects.filter(user=self.request.user).order_by('-created_at')
        context['processing_states'] = ['PENDING', 'RETRY', 'STARTED']
        context['cancelled_states'] = ['ABORTED', 'REVOKED']
        return context

    def post(self, request, *args, **kwargs):
        if 'cancel_upload' in request.POST:
            Upload.objects.get(id=request.POST['cancel_upload']).cancel()
        return HttpResponseRedirect(self.success_url)
