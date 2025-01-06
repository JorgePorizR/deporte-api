# Generated by Django 5.1.4 on 2024-12-15 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaapi', '0003_alter_apuesta_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deporte',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='static/deportes'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='static/equipos'),
        ),
        migrations.AlterField(
            model_name='liga',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='static/ligas'),
        ),
    ]
