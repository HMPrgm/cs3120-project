from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('', views.redirect_dashboard, name='redirect_dashboard'),
    path('upload/', views.upload, name='upload'),
    path('borrowed-books/', views.patron_borrowed_books, name='patron_borrowed_books'),
    path("dashboard/librarian/", views.librarian_dashboard, name="librarian_dashboard"),
    path("dashboard/patron/", views.patron_dashboard, name="patron_dashboard"),
    path("profile/", views.user_profile, name="user_profile"),
    path("dashboard/librarian/collections", views.collections, name="collections"),
    path('requests/', views.lib_view_requests, name='lib_view_requests'),
    path('collections/requests/', views.lib_patron_collection_request, name='lib_patron_collection_request'),
    path('collections/requests/<int:pk>/', views.collection_request_detail, name='collection_request_detail'),
    path('dashboard/patron/', views.patron_dashboard, name='patron_dashboard'),
    path('my-requests/', views.patron_view_requests, name='patron_view_requests'),
    path("lib-upgrade-patrons/", views.lib_upgrade_patrons, name="lib_upgrade_patrons"),
    path("lib-upgrade-patrons/<int:user_id>/", views.perform_upgrade, name="perform_upgrade"),
]
