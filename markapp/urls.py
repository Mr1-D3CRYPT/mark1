from django.urls import path
from . import views
from django.conf import settings
from  django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('index', views.index),
    path('about', views.about),
    path('contact', views.contact),
    path('profile',views.profile),
    path('login_view',views.login_view),
    path('logout_view',views.logout_view),
    path('take_attendance',views.take_attendance),
    path('message', views.message),
    path('delete_message', views.delete_message),
    path('send_email',views.send_email),
    path('edit_student',views.edit_student),
    path('edit_teacher',views.edit_teacher),
    path('mark_attendance',views.mark_attendance),
    path('view_deets',views.view_deets),
]