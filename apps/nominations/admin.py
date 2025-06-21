# apps/nominations/admin.py
from django.contrib import admin
from .models import MainCategory, NominationCategory, Nominee, Vote

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

@admin.register(NominationCategory)
class NominationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'description', 'created_at')
    list_filter = ('main_category',)
    search_fields = ('name', 'main_category__name')
    raw_id_fields = ('main_category',)
    readonly_fields = ('created_at',)

@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'approved', 'vote_count', 'created_at')
    list_filter = ('approved', 'category__main_category', 'category')
    search_fields = ('name', 'category__name')
    raw_id_fields = ('category',)
    actions = ['approve_nominees', 'disapprove_nominees']
    readonly_fields = ('created_at', 'vote_count')

    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Votes'

    def approve_nominees(self, request, queryset):
        queryset.update(approved=True)
    approve_nominees.short_description = "Approve selected nominees"

    def disapprove_nominees(self, request, queryset):
        queryset.update(approved=False)
    disapprove_nominees.short_description = "Disapprove selected nominees"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('nominee', 'category', 'voter_identifier', 'voter_type', 'created_at')
    list_filter = ('voter_type', 'nominee__category')
    search_fields = ('voter_identifier', 'nominee__name')
    raw_id_fields = ('nominee',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def category(self, obj):
        return obj.nominee.category
    category.short_description = 'Category'