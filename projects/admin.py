from django.contrib import admin

from .models import Project, Category, Tag, Donation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug", "project_count")

    def project_count(self, obj):
        return obj.projects.count()
    project_count.short_description = "Projects"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "total_target", "start_time", "end_time", "created_at")
    list_filter = ("category", "tags")
    search_fields = ("title", "details")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("project", "donor", "amount", "created_at")
    list_select_related = ("project", "donor")
