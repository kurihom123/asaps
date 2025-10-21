from django.contrib import admin

from asapcutapp.models.user_model import UserProfile, UserLog, Level, Report, ReportView


class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    list_filter = ('abbr',)


admin.site.register(Level, LevelAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'sex', 'phone', 'postal_address', 'photo', 'association', 'position')
    list_filter = ('user',)


admin.site.register(UserProfile, UserProfileAdmin)


class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'date')
    list_filter = ('activity',)


admin.site.register(UserLog, UserLogAdmin)


class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_about', 'report_file', 'created_at')
    list_filter = ('report_about',)


admin.site.register(Report, ReportAdmin)


class ReportViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'report', 'viewed_at')
    list_filter = ('report',)


admin.site.register(ReportView, ReportViewAdmin)