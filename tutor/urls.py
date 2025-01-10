from django.urls import path
from tutor import views
from users import views as user_views

urlpatterns = [
    path("", views.home, name="home"),
    path("calendar/", views.week, name="calendar"),
    path("billing/", views.billing, name="billing"),
    path("new_appointment/", views.new_appointment, name="new_appointment"),
    path("new_student/", views.new_student, name="new_student"),
    path("new_family/", views.new_family, name="new_family"),
    path("week/", views.week, name="week"),
    path("week/<int:year>/<int:month>/<int:day>/", views.week, name="week"),
    path("submit_appointment/", views.submit_appointment, name="submit_appointment"),
    path("submit_student/", views.submit_student, name="submit_student"),
    path("submit_family/", views.submit_family, name="submit_family"),
    path('family_details/<int:family_id>/', views.family_details, name='family_details'),
    path('mark_appointment_paid/<int:appointment_id>/', views.mark_appointment_paid, name='mark_appointment_paid'),
    
    # path('rest/v1/calendar/init/', views.google_calendar_init, name='google_calendar_init'),
    # path('rest/v1/calendar/redirect/', user_views.google_calendar_redirect, name='google_calendar_redirect'),
    #path('rest/v1/calendar/events/', views.google_calendar_events, name='google_calendar_events'),
]
