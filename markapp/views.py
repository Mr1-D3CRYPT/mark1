from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User,Group
from markapp.models import Student,Teacher,Contact
import cv2
from django.core.mail import send_mail

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
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/profile')
        else:
            message = 'enter the correct username and password'
            return render(request, 'login.html', {"message":message})
    return render(request, 'login.html')


def message(request):
    stats = "nil"
    if request.method == 'POST':
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            stats = Contact.objects.create(name=name, email=email, message=message)
    return render(request, "contact.html",{"stats":stats})


def profile(request):
    user = request.user 
    post = "no one"
    if user.is_authenticated:
        if user.groups.filter(name='teacher').exists():
            post = "teacher"
            profile = Teacher.objects.all()
        else:
            profile = Student.objects.all()
        return render(request, 'profile.html', {"post":post,"profile":profile})
    else:
        return redirect('/login_view')

def logout_view(request):
    logout(request)
    return redirect('/login_view')


def edit_student(request):
    i = 1
    user = request.user
    if user.is_authenticated:
        editable = Student.objects.all()
        if request.method == "GET":
            name = request.GET.get("name")
            val = Student.objects.filter(username=name)
            return render(request,"edit_student.html",{"val":val,"editable":editable,"i":i})
        return render(request,"edit_student.html",{"editable":editable,"i":i})

    else:
        return redirect('/login')

def take_attendance(request):
    import face_recognition
    from face_recognition import load_image_file, face_encodings
    import os

    # Load known images and create face encodings
    def load_images_from_folder(folder):
        images = {}
        for filename in os.listdir(folder):
            img_path = os.path.join(folder, filename)
            img = load_image_file(img_path)
            face_encodings_list = face_encodings(img)
            if face_encodings_list:  # Check if the list is not empty
                images[filename.split(".")[0]] = face_encodings_list[0]
        return images

    known_images = load_images_from_folder("markapp/media/face_pics")

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Loop over each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(list(known_images.values()), face_encoding)

            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = list(known_images.keys())[first_match_index]


            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('/profile')