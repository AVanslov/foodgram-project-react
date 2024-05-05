# Generated by Django 4.2 on 2024-05-05 08:03

from django.db import migrations, models
import django_extensions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#9BEFBE', max_length=7, unique=True, validators=[django_extensions.validators.HexValidator(length=7)], verbose_name='Цвет'),
        ),
    ]