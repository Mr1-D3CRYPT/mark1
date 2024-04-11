from django.shortcuts import redirect, render
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User,Group
import cv2

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

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

def profile(request):
    user = request.user 
    post = "no one"
    if user.is_authenticated:
        if user.groups.filter(name='teacher').exists():
            post = "teacher"
        return render(request, 'profile.html', {"post":post})
    else:
        return redirect('/login_view')

def logout_view(request):
    logout(request)
    return redirect('/login_view')

def take_attendance():
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    import face_recognition
    image = face_recognition.load_image_file("your_file.jpg")
    face_locations = face_recognition.face_locations(image)

    video_capture = cv2.VideoCapture(0)

    def detect_bounding_box(frame):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        return faces

    while True:

        result, video_frame = video_capture.read()  # read frames from the video
        if result is False:
            break  # terminate the loop if the frame is not read successfully

        faces = detect_bounding_box(
            video_frame
        )  # apply the function we created to the video frame

        cv2.imshow(
            "My Face Detection Project", video_frame
        )  # display the processed frame in a window named "My Face Detection Project"

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('/profile')
