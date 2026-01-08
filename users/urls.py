from django.urls import path
from .views import (
    # API Views (Xử lý logic, trả về JSON)
    RegisterView, LoginView, UserProfileView, AdminUserListView, AdminStatsView,
    # HTML Views (Trả về giao diện trang web)
    login_page, register_page, home, profile_page, dashboard_page
)

urlpatterns = [
    path('', home, name='home'),

    path('login/', login_page, name='login_html'),     

    path('register/', register_page, name='register_html'),

    path('profile/', profile_page, name='profile_html'), 

    path('api/login/', LoginView.as_view(), name='api_login'),     

    path('api/register/', RegisterView.as_view(), name='api_register'),

    path('api/profile/', UserProfileView.as_view(), name='api_profile'), 

    path('dashboard/', dashboard_page, name='dashboard'),

    path('api/admin/users/', AdminUserListView.as_view(), name='api_admin_users'),

    path('api/admin/stats/', AdminStatsView.as_view(), name='api_admin_stats'),
]