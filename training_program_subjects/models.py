from django.db import models
from training_program.models import TrainingProgram
from subject.models import Subject

class TrainingProgramSubjects(models.Model):
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('program', 'subject')

    def __str__(self):
        return f"{self.program} - {self.subject}"
