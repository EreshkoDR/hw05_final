from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()
LIMIT = 10


def paginator_func(list, limit, request):
    paginator = Paginator(list, limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator_func(post_list, LIMIT, request)
    follow = Follow.objects.filter(user=request.user.is_authenticated)
    if follow.exists():
        following = True
    else:
        following = False
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
        'post_list': post_list,
        'index': True,
        'following': following
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.filter(group=group)
    page_obj = paginator_func(posts, LIMIT, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.filter(author=author)
    page_obj = paginator_func(posts, LIMIT, request)
    title = 'Последние обновления на сайте'
    if author != request.user:
        is_author = True
    else:
        is_author = False
    if Follow.objects.filter(
        user=request.user.is_authenticated,
        author=author
    ).exclude():
        following = True
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'title': title,
        'posts': posts,
        'following': following,
        'is_author': is_author,
    }
    return render(request, 'posts/profile.html', context)


# @login_required
# при текстах практикума выходит ошибка
# AttributeError: 'NoneType' object has no attribute 'keys'
# ---------------------------------------------------------
# context = None, field_type = <class 'posts.models.Post'>
#
#     def get_field_from_context(context, field_type):
# >       for field in context.keys():
# E       AttributeError: 'NoneType' object has no attribute 'keys'
#
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'form': form,
        'posts': post,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    group = Group.objects.all()
    if request.method == 'POST':
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            author = request.user
            image = form.cleaned_data['image']
            Post.objects.create(
                text=text,
                group=group,
                author=author,
                image=image
            ).save()
            return redirect('posts:profile', username=author)
        else:
            return render(request, template, {'form': form})
    return render(request, template, {'form': form})


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    is_edit = True
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    else:
        if request.method == 'POST':
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                PostForm(instance=post, data=request.POST).save()
                return redirect('posts:post_detail', post_id=post_id)
            else:
                return render(request, template, {'form': form})

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.text = form.cleaned_data['text']
        comment.author = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(posts, LIMIT, request)
    title = 'Последние обновления авторов'
    context = {
        'page_obj': page_obj,
        'title': title,
        'follow': True,
        'following': True
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    is_follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and (is_follow.exists() is not True):
        Follow.objects.create(user=request.user, author=author)
        return redirect('posts:profile', username=username)
    else:
        return redirect('posts:profile', username=username)


@login_required
def profil_unfollow(request, username):
    author = User.objects.get(username=username)
    if Follow.objects.filter(user=request.user, author=author):
        Follow.objects.get(user=request.user, author=author).delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)
