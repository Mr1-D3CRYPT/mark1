# Generated by Django 5.0.4 on 2024-04-11 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markapp', '0003_alter_teacher_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='pic',
            field=models.FileField(upload_to='markapp/media/face_pics/'),
        ),
    ]
