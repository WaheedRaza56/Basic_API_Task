from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_stores']

    def approve_stores(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} store(s) approved successfully.")
    approve_stores.short_description = "Approve selected stores"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size_code',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('color',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('store', 'name', 'price', 'on_sale', 'get_discounted_price', 'category','stock','created_by_super_admin')

    filter_horizontal = ('sizes', 'colors')






class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", "name", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []

admin.site.register(User, UserModelAdmin)
