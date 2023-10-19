from django.contrib import admin
from .models import *


# Register your models here.
class ReportAdmin(admin.ModelAdmin):
    list_filter = ("user__username", "created_at", "description")


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Report, ReportAdmin)
