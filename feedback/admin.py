from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import InstructorFeedback, CourseFeedback, TrainingProgramFeedback

# Define resource classes for each model

class InstructorFeedbackResource(resources.ModelResource):
    class Meta:
        model = InstructorFeedback
        fields = ('id', 'student', 'instructor', 'course_knowledge', 'communication_skills', 
                  'approachability', 'engagement', 'professionalism', 'comments', 'created_at')

class CourseFeedbackResource(resources.ModelResource):
    class Meta:
        model = CourseFeedback
        fields = ('id', 'student', 'course', 'course_material', 'clarity_of_explanation', 
                  'course_structure', 'practical_applications', 'support_materials', 'comments', 'created_at')

class TrainingProgramFeedbackResource(resources.ModelResource):
    class Meta:
        model = TrainingProgramFeedback
        fields = ('id', 'student', 'training_program', 'relevance', 'organization', 
                  'learning_outcomes', 'resources', 'support', 'comments', 'created_at')

# Register the models with ImportExportModelAdmin

@admin.register(InstructorFeedback)
class InstructorFeedbackAdmin(ImportExportModelAdmin):
    resource_class = InstructorFeedbackResource
    list_display = ('student', 'instructor', 'average_rating', 'created_at')
    search_fields = ('student__username', 'instructor__username')

@admin.register(CourseFeedback)
class CourseFeedbackAdmin(ImportExportModelAdmin):
    resource_class = CourseFeedbackResource
    list_display = ('student', 'course', 'average_rating', 'created_at')
    search_fields = ('student__username', 'course__name')

@admin.register(TrainingProgramFeedback)
class TrainingProgramFeedbackAdmin(ImportExportModelAdmin):
    resource_class = TrainingProgramFeedbackResource
    list_display = ('student', 'training_program', 'average_rating', 'created_at')
    search_fields = ('student__username', 'training_program__name')
