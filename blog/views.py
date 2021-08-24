from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.http import HttpResponse
from .models import Post, Comment, Contact, About
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm, ContactForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity

# about = get_object_or_404(About, id=1)
# contact = get_object_or_404(Contact, id=1)


# Create your views here.
def index(request, tag_slug=None):  # function-based view.
    objects_list = Post.published.all()
    about = get_object_or_404(About, id=1)
    contact = get_object_or_404(Contact, id=1)
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        objects_list = objects_list.filter(tags__in=[tag])
    paginator = Paginator(objects_list, 3)  # 3 posts in each page.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #  if page is not an integer, display first page.
        posts = paginator.page(1)
    except EmptyPage:
        #  If page is out of range, deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/index.html',
                  {'posts': posts,
                   'page': page,
                   'tag': tag,
                   'about': about,
                   'contact': contact, })


# class PostListView(ListView):  # Class-based view.
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 4
#     template_name = 'blog/post/index.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    about = get_object_or_404(About, id=1)
    contact = get_object_or_404(Contact, id=1)

    # List of active comments for the current post.
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        #  A comment was posted.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #  Create comment object but don't save to database yet.
            new_comment = comment_form.save(commit=False)
            #  Assign the current post to the comment.
            new_comment.post = post
            #  Save the comment to the database.
            new_comment.save()
            return HttpResponseRedirect(request.build_absolute_uri(post.get_absolute_url()))
    else:
        comment_form = CommentForm()

    # List of similar posts.
    post_tag_ids = post.tags.values_list('id', flat=True)  # get tag ids of the current post.
    similar_posts = Post.published.filter(tags__in=post_tag_ids) \
        .exclude(id=post.id)  # retrieve posts that have similar tags as the tags in post_tag_ids except d current post.
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts,
                                                     'about': about,
                                                     'contact': contact})


def post_share(request, post_id):
    #  Retrieve post by id.
    post = get_object_or_404(Post, id=post_id, status='published')
    about = get_object_or_404(About, id=1)
    contact = get_object_or_404(Contact, id=1)
    sent = False
    if request.method == 'POST':
        #  Form was submitted.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #  form fields passed validation.
            cd = form.cleaned_data
            #  ...send email
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['firstname']} {cd['lastname']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['firstname']} {cd['lastname']}\'s comments: {cd['comment']}"
            send_mail(subject, message, 'admin@myblog.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent,
                                                    'about': about,
                                                    'contact': contact})


def post_search(request):
    about = get_object_or_404(About, id=1)
    contact = get_object_or_404(Contact, id=1)
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('body', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query)

            # stemming, ranking and weighting.
            results = Post.published.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')

            # trigram functionality
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query),
                                              ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results,
                                                     'about': about,
                                                     'contact': contact})


def contact(request):
    #  Retrieve post by id.
    contact = get_object_or_404(Contact, id=1)
    about = get_object_or_404(About, id=1)
    sent = False
    if request.method == 'POST':
        #  Form was submitted.
        form = ContactForm(request.POST)
        if form.is_valid():
            #  form fields passed validation.
            cd = form.cleaned_data
            #  ...send email
            subject = f"CONTACT from: {cd['name']}"
            message = cd['comment']
            send_mail(subject, message, cd['email'],
                      [contact.email])
            sent = True
    else:
        form = ContactForm()

    return render(request, 'blog/contact.html', {'contact': contact,
                                                 'form': form,
                                                 'sent': sent,
                                                 'about': about})


def about(request):
    about = get_object_or_404(About, id=1)
    contact = get_object_or_404(Contact, id=1)
    return render(request, 'blog/about.html', {'about': about,
                                               'contact': contact})