from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings  # Import settings for email host configuration
from django.views.generic import ListView
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import CommentForm, EmailPostForm, SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, \
                                           SearchQuery, SearchRank

from blog import models
from django.db.models.functions import Cast
from django.db.models import CharField, Value
from django.db.models.functions import Cast


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    
    # Filter posts by tag if tag_slug is provided
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post.published,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    comments = post.comments.filter(active=True)
    paginator = Paginator(comments, 5)  # Show 5 comments per page
    # Form for users to comment
    form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                              .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                             .order_by('-same_tags','-publish')[:4]

    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/detail.html',
        {'post': post, 'comments': comments,'form': form,'similar_posts': similar_posts}
    )

def post_share(request, post_id):
    post = get_object_or_404(Post.published, id=post_id)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [cd['to']])
                sent = True
                messages.success(request, "Your email has been sent.")
                return redirect(post)
            except Exception as e:
                messages.error(request, "There was an error sending your email. Please try again.")
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post.published, id=post_id)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})




def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Cast the query to text for similarity comparison
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', Cast(Value(query), output_field=CharField()))
            ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
