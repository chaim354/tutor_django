from django.contrib import admin
from .models import Family, Student, Appointment
# Register your models here.
admin.site.register(Family)
admin.site.register(Student)
admin.site.register(Appointment)
