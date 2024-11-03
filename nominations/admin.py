from django.contrib import admin
from .models import MainCategory, NominationCategory, Nominee, Vote

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(NominationCategory)
class NominationCategoryAdmin(admin.ModelAdmin):
    list_display = ('main_category', 'name', 'description')
    list_filter = ('main_category',)

@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'approved')
    list_filter = ('category', 'approved')
    actions = ['approve_nominees']

    def approve_nominees(self, request, queryset):
        queryset.update(approved=True)
    approve_nominees.short_description = "Approve selected nominees"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('nominee', 'voter_identifier', 'voter_type', 'created_at')
    list_filter = ('nominee', 'voter_type')
    search_fields = ('voter_identifier',)
    ordering = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('nominee')
