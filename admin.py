from django.utils.translation import ugettext_lazy as _

from django.contrib.admin import AdminSite


class LTEAdminSite(AdminSite):
    site_title = _('AdminLTE')
    site_header = _('Site Administration')
    index_title = _('Dashboard')

    index_template = 'lte/index.html'


site = LTEAdminSite(name='lte')
