from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post',
        'created',
    )
    search_fields = ('author', 'text')


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
