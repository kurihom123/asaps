from django.contrib import admin

from ..models.organization_model import University, Association, Contribution, Position


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    list_filter = ('abbr',)


admin.site.register(University, UniversityAdmin)


class AssociationAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'member_number', 'logo', 'university')
    list_filter = ('abbr',)


admin.site.register(Association, AssociationAdmin)


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('association', 'allocation', 'amount_paid', 'payment_date', 'balance')
    list_filter = ('association',)


admin.site.register(Contribution, ContributionAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


admin.site.register(Position, PositionAdmin)
