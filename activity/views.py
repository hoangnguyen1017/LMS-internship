from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserActivityLog
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse
from django.db.models.functions import TruncDate
import json 
import logging 

@login_required
def activity_view(request):
    # Get search and date filter parameters
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    # Get all activity logs for the user, ordered by newest first
    activity_logs = UserActivityLog.objects.filter(user=request.user).order_by('-activity_timestamp')

    # Log the activity if it's the first access or a search/filter is performed
    if not request.session.get('activity_page_accessed', False):
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='page_visit',
            activity_details="Accessed activity_view",
            activity_timestamp=timezone.now()
        )
        request.session['activity_page_accessed'] = True  # Set the flag to prevent further logging

    if search_query or from_date or to_date:
        # Log the search/filter activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='search',
            activity_details=f"Searched activities with query: '{search_query}' and dates: '{from_date}' to '{to_date}'",
            activity_timestamp=timezone.now()
        )

    # Filter activity logs based on search query and date range
    if search_query:
        activity_logs = activity_logs.filter(activity_details__icontains=search_query)

    if from_date:
        from_date_parsed = parse_date(from_date)
        if from_date_parsed:
            activity_logs = activity_logs.filter(activity_timestamp__gte=from_date_parsed)

    if to_date:
        to_date_parsed = parse_date(to_date)
        if to_date_parsed:
            to_date_with_time = datetime.combine(to_date_parsed, datetime.max.time())
            activity_logs = activity_logs.filter(activity_timestamp__lte=to_date_with_time)

    # Pagination setup
    page_number = request.GET.get('page', 1)
    page_size = 20
    paginator = Paginator(activity_logs, page_size)
    activity_logs_page = paginator.get_page(page_number)

    # Calculate the page range for pagination display
    page_range_start = max(activity_logs_page.number - 2, 1)
    page_range_end = min(activity_logs_page.number + 2, paginator.num_pages)
    page_range = range(page_range_start, page_range_end + 1)  # Include end page

    # Calculate the start index for the current page
    activity_logs_page.start_index = (activity_logs_page.number - 1) * page_size + 1

    # Render the template with context data
    return render(request, 'activity.html', {
        'activity_logs': activity_logs_page,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
        'page_range': page_range,
    })


logger = logging.getLogger(__name__)

@login_required
def activity_dashboard_view(request):
    try:
        # Log only on the first GET request of the session
        if request.method == 'GET' and not request.session.get('activity_dashboard_accessed', False):
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='page_visit',
                activity_details="Accessed activity_dashboard_view",
                activity_timestamp=timezone.now()
            )
            # Set session flag to avoid logging on subsequent visits
            request.session['activity_dashboard_accessed'] = True

        # Retrieve activities for the current user
        activities = UserActivityLog.objects.filter(user=request.user)
        
        # Handle filters based on POST request data
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                from_date = data.get('from_date')
                to_date = data.get('to_date')
                view_type = data.get('view_type', 'activity_type')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            view_type = request.GET.get('view_type', 'activity_type')

        # Apply date filters if provided
        if from_date:
            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                activities = activities.filter(activity_timestamp__gte=from_date)
            except ValueError:
                logger.error(f"Invalid from_date format: {from_date}")

        if to_date:
            try:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
                to_date = to_date.replace(hour=23, minute=59, second=59)
                activities = activities.filter(activity_timestamp__lte=to_date)
            except ValueError:
                logger.error(f"Invalid to_date format: {to_date}")

        # Process data based on view type
        if view_type == 'activity_details':
            recent_activities = activities.values('activity_details').annotate(count=Count('log_id'))
            recent_activities_labels = [activity['activity_details'] for activity in recent_activities]
            recent_activities_data = [activity['count'] for activity in recent_activities]
        else:  # Default to 'activity_type'
            recent_activities = activities.values('activity_type').annotate(count=Count('log_id'))
            recent_activities_labels = [activity['activity_type'] for activity in recent_activities]
            recent_activities_data = [activity['count'] for activity in recent_activities]

        # Activity over time data
        activity_over_time = (
            activities
            .annotate(date=TruncDate('activity_timestamp'))
            .values('date')
            .annotate(count=Count('log_id'))
            .order_by('date')
        )
        
        activity_over_time_labels = [entry['date'].strftime('%Y-%m-%d') for entry in activity_over_time]
        activity_over_time_data = [entry['count'] for entry in activity_over_time]

        response_data = {
            'total_activities': activities.count(),
            'recent_activities_labels': recent_activities_labels,
            'recent_activities_data': recent_activities_data,
            'activity_over_time_labels': activity_over_time_labels,
            'activity_over_time_data': activity_over_time_data,
        }

        # If POST request, return JSON response for filtering results
        if request.method == "POST":
            return JsonResponse(response_data)
        
        # For GET request, render the activity dashboard template
        return render(request, 'activity_dashboard.html', {
            **response_data,
            'view_type': view_type,
            'from_date': from_date.strftime('%Y-%m-%d') if isinstance(from_date, datetime) else '',
            'to_date': to_date.strftime('%Y-%m-%d') if isinstance(to_date, datetime) else '',
        })

    except Exception as e:
        logger.error(f"Error in activity_dashboard_view: {e}")
        if request.method == "POST":
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'activity_dashboard.html', {
            'error': 'An error occurred while loading the dashboard.',
            'total_activities': 0,
            'recent_activities_labels': [],
            'recent_activities_data': [],
            'activity_over_time_labels': [],
            'activity_over_time_data': [],
        })
        

# @login_required
# def fetch_activity_logs(request):
#     log_activity = request.GET.get('log_activity', 'false') == 'true'
#     search_query = request.GET.get('search', '')
#     from_date = request.GET.get('from_date')
#     to_date = request.GET.get('to_date')

#     activity_logs = UserActivityLog.objects.filter(user=request.user)

#     if search_query:
#         activity_logs = activity_logs.filter(activity_details__icontains=search_query)
#     if from_date:
#         activity_logs = activity_logs.filter(activity_timestamp__gte=parse_date(from_date))
#     if to_date:
#         activity_logs = activity_logs.filter(activity_timestamp__lte=parse_date(to_date))

#     activity_logs = activity_logs.order_by('-activity_timestamp')

#     if log_activity:
#         UserActivityLog.objects.create(
#             user=request.user,
#             activity_type='fetch_activity_logs',
#             activity_details='Fetched activity logs.',
#             activity_timestamp=timezone.now()
#         )

#     data = [
#         {
#             'activity_type': log.get_activity_type_display(),
#             'activity_details': log.activity_details,
#             'activity_timestamp': log.activity_timestamp,
#         }
#         for log in activity_logs
#     ]
#     return JsonResponse(data, safe=False)