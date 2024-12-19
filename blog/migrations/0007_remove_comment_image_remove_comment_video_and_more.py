# Generated by Django 5.1.2 on 2024-12-06 07:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_post_content_alter_post_title_chat_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='image',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='video',
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.RemoveField(
            model_name='post',
            name='video',
        ),
        migrations.CreateModel(
            name='CommentMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='comment_media/')),
                ('file_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], max_length=10)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='blog.comment')),
            ],
        ),
        migrations.CreateModel(
            name='PostMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='post_media/')),
                ('file_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], max_length=10)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='blog.post')),
            ],
        ),
    ]