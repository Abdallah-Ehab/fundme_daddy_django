from django.db import migrations
from django.utils.text import slugify


def seed_categories(apps, schema_editor):
    Category = apps.get_model("projects", "Category")
    categories = [
        "Art",
        "Comics & Illustration",
        "Design",
        "Film & Video",
        "Food",
        "Games",
        "Music",
        "Photography",
        "Publishing",
        "Technology",
        "Theater",
        "Writing & Journalism",
    ]
    for name in categories:
        Category.objects.get_or_create(name=name, slug=slugify(name))


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_category_tag_project_category_project_tags'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=migrations.RunPython.noop),
    ]
