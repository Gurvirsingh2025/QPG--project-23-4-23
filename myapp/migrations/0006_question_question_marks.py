# Generated by Django 4.2 on 2023-04-23 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_question_question_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_marks',
            field=models.IntegerField(default=1, verbose_name=10),
            preserve_default=False,
        ),
    ]
