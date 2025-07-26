from django.urls import path
from . import views
from . import class_views
from . import collections_views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path("<int:pk>/", views.textbook_detail, name="textbook_detail"),
    path('<int:pk>/review/', views.create_review, name='create_review'),
    path('class', class_views.index, name='class_index'),
    path('class/create/', class_views.create, name='class_create'),
    path('class/update/<int:pk>/', class_views.update, name='class_update'),
    path('class/delete/<int:pk>/', class_views.delete, name='class_delete'),
    path("class/<int:pk>/", class_views.detail, name="class_detail"),
    path("collections/", views.public_collections_index, name="collections_index"),
    path("collections/private", collections_views.private_index, name="collections_private_index"),
    path("collections/private/request/<int:pk>", collections_views.request_collection_access, name="request_collection_access"),
    path("collections/<int:pk>/add_patron", collections_views.view_add_patrons, name="collections_add_patron_view"),
    path("collections/<int:pk>/add_patron/<int:user_id>", collections_views.perform_add_patron, name="collections_add_patron"),
    path("collections/<int:pk>/remove_patron/<int:user_id>", collections_views.perform_remove_patron, name="collections_remove_patron"),
    path("collections/create", collections_views.create, name="collections_create"),
    path('collections/update/<int:pk>/', collections_views.update, name='collections_update'),
    path('collections/delete/<int:pk>/', collections_views.delete, name='collections_delete'),
    path("collections/<int:pk>/", collections_views.detail, name="collections_detail"),
    path('<int:pk>/request/', views.request_textbook, name='request_textbook'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path("libraries/", views.libraries_index, name="libraries_index"),
    path('libraries/create/', views.libraries_create, name='libraries_create'),
    path('libraries/<int:library_id>/', views.library_detail, name='libraries_detail'),
    path("libraries/<int:library_id>/update/", views.library_update, name="library_update"),
    path('<int:pk>/return/', views.return_textbook, name='return_textbook'),
]