from django.db import models

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
