from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication (Epic 4, Story 23)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Asset Management (Epic 1)
    path('', views.AssetListView.as_view(), name='asset_list'),
    path('asset/<uuid:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('asset/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('asset/<uuid:pk>/edit/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('asset/<uuid:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    path('asset/<uuid:pk>/assign/', views.assign_asset_view, name='asset_assign'),
]