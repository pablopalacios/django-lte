from braces import views as braces_views


class AdminPermissionViewMixin(braces_views.UserPassesTestMixin):
    """ CBV that implements AdminSite.has_permission """

    def has_permission(self, user):
        return user.is_active and user.is_staff

    def test_func(self, user):
        return self.has_permission(user)
