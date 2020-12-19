from django.urls import path
from . import views
from .feeds import LatestPostsFeed
from django.conf.urls.static import static
from django.conf import settings

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('tag/<slug:tag_slug>/', views.index, name='post_list_by_tag'),
    # path('', views.PostListView.as_view(), name='index'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]\
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
