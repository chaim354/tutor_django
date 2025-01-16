from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Family, Student, Appointment
from .forms import AppointmentForm, StudentForm, FamilyForm
from django.utils import timezone
from datetime import timedelta, date, datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .utilities import WeekCalendar
from collections import defaultdict
import decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import pytz
def home(request):
    return render(request, "tutor/index.html")
@login_required
def calendar(request):
    appointments = request.user.appointment_set.order_by('date')
    context = {
        "appointments": appointments
    }
    return render(request, "tutor/calendar.html", context)
@login_required
def billing(request):
    # Get the start and end dates from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    now = timezone.now()
    if start_date and end_date:
        # Convert the dates to datetime objects
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
    else:
        # Default to the past week if no dates are provided
        today = datetime.today()
        start_date = today - timedelta(days=(today.weekday() + 1) % 7)
        end_date = now

    # Get all appointments in the specified date range
    appointments = request.user.appointment_set.filter(date__gte=start_date, date__lte=end_date, user=request.user)

    # Calculate the total amounts
    amount_paid = sum(appointment.student.last_name.price for appointment in appointments if appointment.paid)
    amount_unpaid = sum(appointment.student.last_name.price for appointment in appointments if not appointment.paid)
    upcoming_appointments = request.user.appointment_set.filter(date__gte=now, user=request.user)
    amount_upcoming = sum(appointment.student.last_name.price for appointment in upcoming_appointments)

    family_amounts = defaultdict(decimal.Decimal)
    for appointment in appointments:
        family_name = appointment.student.last_name
        family_amounts[family_name] += appointment.student.last_name.price

    context = {
        "amount_paid": amount_paid,
        "amount_unpaid": amount_unpaid,
        "amount_upcoming": amount_upcoming,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "family_amounts": dict(family_amounts)
    }
    return render(request, "tutor/billing.html", context)
@login_required
def new_appointment(request):
    if request.method != 'POST':
        form = AppointmentForm()
    else:
        form = AppointmentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('calendar')
    context = {'form': form}
    return render(request, 'tutor/new_appointment.html', context)
@login_required
def new_student(request):
    if request.method != 'POST':
        form = StudentForm(request.POST, user=request.user)
    else:
        form = StudentForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('new_appointment')
    context = {'form': form}
    return render(request, 'tutor/new_student.html', context)
@login_required
def new_family(request):
    if request.method != 'POST':
        form = FamilyForm()
    else:
        form = FamilyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('new_student')
    context = {'form': form}
    return render(request, 'tutor/new_family.html', context)


# Create your views here.
@login_required
def week(request):
    start_date_str = request.GET.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        today = datetime.today()
        start_date = today - timedelta(days=(today.weekday() + 1) % 7)  # Start of the current week

    calendar = WeekCalendar(start_date)
    week_days = calendar.get_week_days()
    # Fetch events for the week
    events = request.user.appointment_set.filter(date__range=(week_days[0], week_days[-1]))
    events_by_date = {day.date(): [] for day in week_days}  # Use date() to match the format

    for event in events:
        event_date = event.date  # No need to use date() since date is already a DateField
        if event_date in events_by_date:
            events_by_date[event_date].append(event)

    # Prepare the data for the template
    week_data = []
    for day in week_days:
        day_date = day.date()
        week_data.append({
            'date': day_date,
            'events': events_by_date.get(day_date, [])
        })

    context = {
        'week_data': week_data,
        'start_date': start_date,
        'form': AppointmentForm(request.POST, user=request.user)
    }
    return render(request, 'tutor/week.html', context)


@login_required
@require_POST
def submit_appointment(request):
    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.user = request.user
        appointment.save()

        # Load credentials from the user's profile
        profile = request.user.profile
        credentials = Credentials(
            token=profile.token,
            refresh_token=profile.refresh_token,
            token_uri=profile.token_uri,
            client_id=profile.client_id,
            client_secret=profile.client_secret,
            scopes=profile.scopes.split(',')
        )

        service = build('calendar', 'v3', credentials=credentials)
        start_datetime = datetime.combine(appointment.date, appointment.start_time)
        end_datetime = datetime.combine(appointment.date, appointment.end_time)

        # Set the timezone
        timezone = pytz.timezone('America/New_York')
        start_datetime = timezone.localize(start_datetime).isoformat()
        end_datetime = timezone.localize(end_datetime).isoformat()

        event = {
            'summary': f'Tutor Session with {appointment.student.first_name} {appointment.student.last_name}',
            'location': f'{appointment.student.last_name.address} {appointment.student.last_name.city} {appointment.student.last_name.state} {appointment.student.last_name.zipcode}',
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/New_York',
            },
        }

        service.events().insert(calendarId='primary', body=event).execute()
    return redirect('week')

@login_required
@require_POST
def submit_student(request):
    form = StudentForm(request.POST, user=request.user)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        return render(request, "tutor/week.html#appointment_form-partial", {'form': AppointmentForm(request.POST, user=request.user)})
    return HttpResponse(status=400)
@login_required
@require_POST
def submit_family(request):
    form = FamilyForm(request.POST)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        return render(request, 'tutor/new_student.html', {'form': StudentForm(request.POST, user=request.user)})
    return HttpResponse(status=204)

@login_required
def family_details(request, family_id):
    family = get_object_or_404(Family, id=family_id, user=request.user)
    now = timezone.now()
    students = Student.objects.filter(last_name_id=family.id)
    past_appointments = Appointment.objects.filter(student__in=students, date__lt=now)
    upcoming_appointments = Appointment.objects.filter(student__in=students, date__gte=now)
    total_amount = sum(appointment.student.last_name.price for appointment in past_appointments)
    student_amounts = {}
    for appointment in past_appointments:
        if appointment.student.first_name not in student_amounts:
            student_amounts[appointment.student.first_name] = 0
        student_amounts[appointment.student.first_name] += appointment.student.last_name.price
    return render(request, 'tutor/family_details.html', {
        'family': family,
        'past_appointments': past_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_amount': total_amount,
        'student_amounts': student_amounts
    })

@require_POST
@login_required
def mark_appointment_paid(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, student__last_name__user=request.user)
    appointment.paid = True
    appointment.save()
    return HttpResponse("""<button class="bg-green-500 text-white px-2 py-1 rounded-md" disabled>Paid</button>""")


from django.shortcuts import render

def family_list(request):
    tab = request.GET.get('tab', '')
    if tab == 'students':
        students = Student.objects.all()
        return render(request, 'tutor/partials/students.html', {'students': students})
    elif tab == 'families':
        families = Family.objects.all()
        return render(request, 'tutor/partials/families.html', {'families': families})
    elif tab == 'appointments':
        appointments = Appointment.objects.all()
        return render(request, 'tutor/partials/appointments.html', {'appointments': appointments})
    else:
        students = Student.objects.all()
        return render(request, 'tutor/family_list.html', {'students': students})