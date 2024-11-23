
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from course.models import Course
from quiz.models import Question
from .models import Assessment,  StudentAssessmentAttempt, AnswerOption, UserAnswer, StudentAssessmentAttempt, InvitedCandidate
from .forms import AssessmentForm, AssessmentAttemptForm, InviteCandidatesForm
from exercises.models import Exercise

from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .tokens import invite_token_generator  # Adjust the import path as necessary
from django.utils.encoding import force_str
from django.db import transaction
from django.core.exceptions import ValidationError
from exercises.libs.submission import grade_submission, precheck
from exercises.models import Submission
from module_group.models import ModuleGroup

