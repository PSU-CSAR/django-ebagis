from django.views import generic

from ebagis.models.aoi import AOI


class AOIDetailsView(generic.DetailView):
    template_name = 'aois/details.html'
    queryset = AOI.objects.all()
