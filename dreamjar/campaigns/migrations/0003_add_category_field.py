from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='category',
            field=models.CharField(
                choices=[
                    ('sports', 'Sports'),
                    ('education', 'Education'),
                    ('hobbies', 'Hobbies'),
                    ('health', 'Health'),
                    ('dreams', 'Dreams')
                ],
                max_length=50,
                default='dreams',  # choose a default so existing rows work
            ),
        ),
    ]
