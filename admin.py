from django.contrib.admin import AdminSite


class LTEAdminSite(AdminSite):
    pass


site = LTEAdminSite(name='lte')
