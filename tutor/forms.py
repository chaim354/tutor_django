from django import forms
from .models import Appointment, Student, Family

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['student', 'date', 'start_time', 'end_time', 'subject']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['student'].queryset = Student.objects.filter(user=user)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(StudentForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['last_name'].queryset = Family.objects.filter(user=user)

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['last_name', 'address', 'city', 'state', 'zipcode', 'price', 'phone_number']