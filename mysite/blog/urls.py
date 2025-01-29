from django.urls import path, re_path
from . import views
from .feeds import LatestPostsFeed

urlpatterns = [
    # Use PostListView for the post listing
     path('', views.post_list, name='post_list'),
     # path('', views.PostListView.as_view(), name='post_list'),
 
    # Post detail view with a regular expression for the date and slug
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$',
            views.post_detail, name='post_detail'),
    path('<int:post_id>/share/',views.post_share, name='post_share'),
    path('<int:post_id>/comment/',views.post_comment, name='post_comment'),
    path('tag/<slug:tag_slug>/',
     views.post_list, name='post_list_by_tag'),
     path('feed/', LatestPostsFeed(), name='post_feed'),
     path('search/', views.post_search, name='post_search'),
 
]
