from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, settings.OBJECTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'misc/index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, settings.OBJECTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, settings.OBJECTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and (Follow.objects.filter(
        user=request.user, author=author).exists())
    context = {
        'author': author,
        'page': page,
        'post_count': post_list.count(),
        'paginator': paginator,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    form = CommentForm()
    comments = post.comments.all()
    return render(
        request,
        'posts/post.html',
        {'post': post,
         'author': post.author,
         'comments': comments,
         'form': form,
         }
    )


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'posts/new_post.html',
                  {'form': form, 'rename': 'edit', 'post': post})


@login_required
def new_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            model = form.save(commit=False)
            model.author = request.user
            model.save()
            return redirect('index')

        return render(request, 'posts/new_post.html', {'form': form})

    return render(request, 'posts/new_post.html',
                  {'form': form, 'rename': 'add'})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', post_id=post_id,
                        username=username)
    return render(request, 'posts/comments.html',
                  {'form': form, 'comments': comments, 'post': post})


@login_required
def follow_index(request):
    post_owner = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_owner, settings.OBJECTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html',
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    if follower != following:
        Follow.objects.get_or_create(user=follower, author=following)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    Follow.objects.filter(user=follower, author=following).delete()
    return redirect('profile', username=username)
