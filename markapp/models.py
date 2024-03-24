from django.db import models
from django.contrib.auth.models import User
  
class Teacher(models.Model):
    id = models.CharField(max_length = 50, primary_key=True)
    name = models.CharField(max_length=255)
    pic = models.FileField(upload_to='markapp/static/assets/images/face_pics/')
    date_of_join = models.DateField()
    contact_no = models.IntegerField()
    courses_taught = models.CharField(max_length=255)
    programme = models.CharField(max_length=255)
    college = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Student(models.Model):
    reg = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length = 50)
    pic = models.FileField(upload_to='markapp/static/assets/images/face_pics/')
    class_name = models.CharField(max_length=255)
    contact_no = models.IntegerField()
    programme = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    attendance_percent = models.IntegerField()
    parent_name = models.CharField(max_length=255)
    parent_contact = models.IntegerField()

    def __str__(self):
        return self.username
    
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.DateField()
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.day}"

class Contact(models.Model):
    name = models.CharField(max_length=200)
    phone_no = models.IntegerField()
    mail = models.EmailField()

    def __str__(self):
        return f"{self.name}, {self.phone_no}"