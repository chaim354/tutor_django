from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Family(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=25)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=25)

    def __str__(self):
        return self.last_name


class Student(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.ForeignKey(Family, on_delete=models.CASCADE)
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + " " + self.last_name.__str__()

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=50)
    notes = models.TextField(blank=True, default="")
    paid = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.student} - {self.subject} on {self.date}"
