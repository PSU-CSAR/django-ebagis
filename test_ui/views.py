from django.views import generic
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from ebagis.models.aoi import AOI
from ebagis.models.upload import Upload
from ebagis.models.download import Download

class AOIDetailsView(generic.DetailView):
    template_name = 'aois/details.html'
    queryset = AOI.objects.all()

class UserRequestView(LoginRequiredMixin, TemplateView):
	template_name = 'userrequests.html'

	def get_context_data(self, **kwargs):
		context = super(UserRequestView, self).get_context_data(**kwargs)
		context['uploads'] = Upload.objects.filter(user=self.request.user)
		context['downloads'] = Download.objects.filter(user=self.request.user)
		context['processing_states'] = ['PENDING', 'RETRY', 'STARTED']
		context['cancelled_states'] = ['ABORTED', 'REVOKED']
		return context

	# write post method to cancel an upload, cancel download UserRequestView
