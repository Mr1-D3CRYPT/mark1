import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User,Group
from markapp.models import Student,Teacher,Contact,Attendance
import cv2
from django.core.mail import send_mail
from datetime import datetime,date
import os
from django.shortcuts import redirect
from datetime import datetime
import face_recognition


def attd_calc():
    usr = User.objects.all()
    for usr in usr:
        if usr.groups.filter(name='student').exists():
            att = Attendance.objects.filter(user=usr)
            p,a = 0,0
            for at in att:
                if at.status == 'p':
                    p += 1
                else:
                    a += 1
            attd = round((p/(a+p))*100,2)
            stud = Student.objects.get(reg=usr)
            stud.attendance_percent = attd
            stud.save()


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    message = Contact.objects.all()
    stats = "nil"
    status = request.GET.get('status')
    return render(request, 'contact.html',{"message":message,"stats":stats,"status":status})

def delete_message(request):
    if request.method == 'POST':
        message_name = request.POST.get("message_name")
        message_email = request.POST.get("message_email")
        message = Contact.objects.filter(name=message_name,email=message_email)
        message.delete()
    return redirect('/contact')

def send_email(request):
    status="failed"
    if request.method == 'POST':
        mail_text = request.POST.get("mail_text")
        mail_id = request.POST.get("message_email")
        subject = 'Reply from Zuric'
        message = mail_text
        sender = 'ashish.23pmc111@mariancollege.org'
        recipient = [mail_id]
        stat = send_mail(subject, message, sender, recipient)
        if stat:
            status = "success"
        return redirect("/contact?status={}".format(status))
    return redirect("/contact?status={}".format(status))


def login_view(request):
    user = request.user
    if user.is_authenticated:
        return redirect('/profile')
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/profile')
        else:
            message = 'Invalid username or password. Please try again.'
            return render(request, 'login.html', {"message": message})
    return render(request, 'login.html')


def message(request):
    stats = "nil"
    if request.method == 'POST':
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            stats = Contact.objects.create(name=name, email=email, message=message)
    return render(request, "contact.html",{"stats":stats})

def view_deets(request):
    user = request.user
    attendances = Attendance.objects.filter(user=user)
    return render(request,'view_deets.html',{"attendances":attendances})

def profile(request):
    user = request.user 
    post = "no one"
    if user.is_authenticated:
        if user.groups.filter(name='teacher').exists():
            profile = Teacher.objects.get(reg=user)
            post = "teacher"
        elif user.groups.filter(name='student').exists():
            profile = Student.objects.get(reg=user)
            post = "student"
        else:
            profile = User.objects.get(username=user)
            post = "admin"
        try:
            return render(request, 'profile.html', {"post":post,"profile":profile})
        except User.DoesNotExist:
            return redirect('/login_view')
    else:
        return redirect('/login_view')
    
def edit_teacher(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            editable = Teacher.objects.all()
            if request.method == "GET":
                name = request.GET.get("name")
                val = Teacher.objects.filter(name=name)
                return render(request,"edit_teacher.html",{"val":val,"editable":editable})
            return render(request,"edit_teacher.html",{"editable":editable})
        else:
            return redirect('/profile')
    else:
        return redirect('/profile')

def logout_view(request):
    logout(request)
    return redirect('/login_view')


def edit_student(request):
    user = request.user
    if user.is_authenticated:
        if user.groups.filter(name='teacher').exists():
            editable = Student.objects.all()
            if request.method == "GET":
                name = request.GET.get("name")
                val = Student.objects.filter(username=name)
                return render(request,"edit_student.html",{"val":val,"editable":editable})
            return render(request,"edit_student.html",{"editable":editable})
        else:
            return redirect('/login_view')
    else:
        return redirect('/login_view')
    
def mark_attendance(request):
    message = None
    if request.method == 'GET':
        reg = request.GET.get("m_name")
        date_m = request.GET.get("m_date")
        users_n = Student.objects.all()
        for ur in users_n:
            try:
                user_instance = User.objects.get(username=ur.reg)
                try:
                    day_stat = Attendance.objects.get(user=user_instance, day=date_m)
                except Attendance.DoesNotExist:
                    day_stat = Attendance.objects.create(user=user_instance, day=date_m)
            except Student.DoesNotExist:
                pass   
            message = "attendance marked successfully"         
        try:
            user_instance = User.objects.get(username=reg)
            date_m = datetime.strptime(date_m, '%Y-%m-%d').date()
            try:    
                day_stat = Attendance.objects.get(user=user_instance, day=date_m)
                day_stat.status = "p"
                day_stat.save()
            except Attendance.DoesNotExist:
                day_stat = Attendance.objects.create(user=user_instance, day=date_m, status="p")
            message = "attendance marked successfully"
        except User.DoesNotExist:
                pass
        attd_calc()
        return redirect('/edit_student',{"message":message})

def take_attendance(request):
    def load_images_from_folder(folder):
        images = {}
        for filename in os.listdir(folder):
            img_path = os.path.join(folder, filename)
            img = face_recognition.load_image_file(img_path)
            face_encodings_list = face_recognition.face_encodings(img)
            if face_encodings_list:  
                images[filename.split(".")[0]] = face_encodings_list[0]
        return images

    known_images = load_images_from_folder("markapp/media/face_pics")
    
    date_m = date.today()
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(list(known_images.values()), face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = list(known_images.keys())[first_match_index] 

                #for the identified users
                try:
                    pc = "face_pics/"+name+".jpg"
                    users = Student.objects.get(pic=pc)
                    try:
                        day_stat = Attendance.objects.get(user=users.reg, day=date_m)
                        day_stat.status = "p"
                        day_stat.save()
                    except Attendance.DoesNotExist:
                        day_stat = Attendance.objects.create(user=users.reg, day=date_m, status="p")
                except:
                    pass 

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            users_n = Student.objects.all()
            #for all users to mark absent on that day
            for user_n in users_n:
                try:
                    user_instance = User.objects.get(username=user_n.reg)
                    try:
                        day_stat = Attendance.objects.get(user=user_instance, day=date_m)
                    except Attendance.DoesNotExist:
                        day_stat = Attendance.objects.create(user=user_instance, day=date_m)
                except User.DoesNotExist:
                    pass  
            attd_calc()
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return redirect('/profile')
