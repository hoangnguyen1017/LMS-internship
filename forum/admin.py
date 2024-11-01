from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import ForumQuestion, ForumComment, Reply

# Define resource classes for each model for import/export

class ForumQuestionResource(resources.ModelResource):
    class Meta:
        model = ForumQuestion
        fields = ('id', 'user', 'course', 'title', 'content', 'created_at', 'updated_at')

class ForumCommentResource(resources.ModelResource):
    class Meta:
        model = ForumComment
        fields = ('id', 'user', 'question', 'content', 'created_at', 'updated_at')

class ReplyResource(resources.ModelResource):
    class Meta:
        model = Reply
        fields = ('id', 'user', 'comment', 'content', 'created_at', 'updated_at')


# Register the models with ImportExportModelAdmin to add import/export functionality

@admin.register(ForumQuestion)
class ForumQuestionAdmin(ImportExportModelAdmin):
    resource_class = ForumQuestionResource
    list_display = ('title', 'user', 'course', 'created_at')
    search_fields = ('title', 'user__username', 'course__name')

@admin.register(ForumComment)
class ForumCommentAdmin(ImportExportModelAdmin):
    resource_class = ForumCommentResource
    list_display = ('content', 'user', 'question', 'created_at')
    search_fields = ('content', 'user__username', 'question__title')

@admin.register(Reply)
class ReplyAdmin(ImportExportModelAdmin):
    resource_class = ReplyResource
    list_display = ('content', 'user', 'comment', 'created_at')
    search_fields = ('content', 'user__username', 'comment__content')

