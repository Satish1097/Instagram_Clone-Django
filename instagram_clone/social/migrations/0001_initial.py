# Generated by Django 5.0.7 on 2024-07-25 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Image', models.ImageField(default='', upload_to='images/')),
                ('Contact', models.CharField(max_length=13)),
            ],
        ),
    ]
