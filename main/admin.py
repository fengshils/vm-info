from django.contrib import admin
from .models import Vms, VCenter

# Register your models here.
class VcenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'remarks','disk')
    #筛选器
    list_filter =('name', 'ip') #过滤器
    search_fields =('name', 'ip') #搜索字段

class VmsAdmin(admin.ModelAdmin):
    list_display = ('name', 'powerstate', 'des')
    list_filter =( 'vcent', 'powerstate') #过滤器
    search_fields =('name','id', 'des') #搜索字段


admin.site.register(VCenter, VcenterAdmin)
admin.site.register(Vms, VmsAdmin)