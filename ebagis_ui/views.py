from django.views import generic
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from allauth.account.views import EmailView

from djcelery.models import TaskMeta

from ebagis.data.models.aoi import AOI
from ebagis.models.upload import Upload
from ebagis.models.download import Download
from ebagis.tasks import export_data


class AOIDetailsView(LoginRequiredMixin, generic.DetailView):
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


class DownloadRequestView(LoginRequiredMixin, generic.ListView):
    template_name = 'downloadrequests.html'
    success_url = reverse_lazy('account_requests_download')
    model = Download
    context_object_name = 'downloads'
    paginate_by = 20

    def get_queryset(self):
        return Download.objects.filter(user=self.request.user).order_by('-created_at')


class UploadRequestView(LoginRequiredMixin, generic.ListView):
    template_name = 'uploadrequests.html'
    success_url = reverse_lazy('account_requests_upload')
    model = Upload
    context_object_name = 'uploads'
    paginate_by = 20

    def get_queryset(self):
        return Upload.objects.filter(user=self.request.user).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        if 'cancel_upload' in request.POST:
            Upload.objects.get(id=request.POST['cancel_upload']).cancel()
        return HttpResponseRedirect(self.success_url)


class UserProfileView(LoginRequiredMixin, EmailView):
    template_name = "userprofile.html"
    success_url = reverse_lazy('account_profile')

    def post(self, request, *args, **kwargs):
        if "action_update" in request.POST:
            request.user.first_name = request.POST['first_name']
            request.user.last_name = request.POST['last_name']
            request.user.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'User details updated successfully.',
            )
            return HttpResponseRedirect(self.success_url)
        else:
            return super(UserProfileView, self).post(request, *args, **kwargs)
