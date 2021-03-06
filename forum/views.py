from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, CreateView, ListView
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import AddPost, CommentForm
from .models import Game, Post, Comment
from django.urls import reverse_lazy, reverse


def LikeView(request, id):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return redirect(request.META['HTTP_REFERER'])


class GameList(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = 'index.html'


class PostList(View):

    def get(self, request, name, *args, **kwargs):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, name=name)
        posts = game.forum_posts.all()
        likes = []
        for post in posts:
            if post.likes.filter(id=self.request.user.id).exists():
                likes.append(post.id)
        return render(
            request,
            "postlist.html",
            {
                'posts': posts,
                'game': game,
                'likes': likes,
            },
        )


class PostView(View):

    def get(self, request, id, *args, **kwargs):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, id=id)
        comments = post.comments.all()
        total_likes = post.likes.count()
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        return render(
            request,
            "postview.html",
            {
                'post': post,
                'comments': comments,
                'liked': liked,
            },
        )


class Add_Post(LoginRequiredMixin, CreateView):
    model = Post
    form_class = AddPost
    template_name = 'add-post.html'

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_REFERER'):
            game_name = request.META.get('HTTP_REFERER').split('/')[3].replace(
                                                                    '%20', ' ')
            game_id = get_object_or_404(Game, name=game_name).id
            form = self.form_class
            context = {
                'form': form,
                'game_id': game_id,
            }
        else:
            form = self.form_class
            context = {
                'form': form,
            }
        return render(request, self.template_name, context)

    def get_success_url(self):
        return reverse('postview', kwargs={'id': self.object.id})


class Add_Comment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'add-comment.html'

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('postview', kwargs={'id': self.object.post_id})


class Delete_Post(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        return reverse('postlist', kwargs={'name': self.object.game})


class Delete_Comment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('postview', kwargs={'id': self.object.post_id})


class Edit_Post(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = AddPost
    template_name = 'edit-post.html'

    def get_success_url(self):
        return reverse('postview', kwargs={'id': self.object.id})
