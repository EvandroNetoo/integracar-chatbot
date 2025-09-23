from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group

from contas.models import Usuario

admin.site.unregister(Group)


@admin.register(Usuario)
class UserAdmin(auth_admin.UserAdmin):
    model = Usuario
    add_form_template = ''
    search_fields = ['email']
    list_filter = ['is_superuser']
    list_display = ['email']
    list_display_links = ['email']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    ordering = ['email']
    fieldsets = (
        (
            'Informações de login',
            {
                'fields': (
                    'email',
                    'password',
                )
            },
        ),
        (
            'Informações pessoais',
            {
                'fields': ('name',),
            },
        ),
        (
            'Permissões',
            {
                'fields': (
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
        (
            'Database',
            {
                'fields': ('is_active',),
            },
        ),
        (
            'Datas importantes',
            {
                'fields': (
                    'last_login',
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )
    add_fieldsets = (
        (
            'Informações de importantes',
            {
                'fields': (
                    'email',
                    'name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )
