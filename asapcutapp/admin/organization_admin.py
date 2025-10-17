from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from ..models.organization_model import *


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    list_filter = ('abbr',)


admin.site.register(University, UniversityAdmin)


class AssociationAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'member_number', 'logo', 'university')
    list_filter = ('abbr',)


admin.site.register(Association, AssociationAdmin)


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('allocation','payment_date', 'amount_paid', 'balance', 'association', 'year')
    list_filter = ('association',)


admin.site.register(Contribution, ContributionAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


try:
    admin.site.register(Position, PositionAdmin)
except AlreadyRegistered:
    pass


class ContributionUploadAdmin(admin.ModelAdmin):
    list_display = ('excel_file', 'year', 'uploaded_at', 'uploaded_by')
    list_filter = ('year',)


admin.site.register(ContributionUpload, ContributionUploadAdmin)