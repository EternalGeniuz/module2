from django.contrib import admin

from web.models import TimeSlot, TimeSlotTag


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'start_date', 'end_date', 'is_realtime', 'get_spent_time')
    search_fields = ('title',)
    list_filter = ('start_date', 'end_date', 'is_realtime', 'user')
    ordering = ('-start_date',)
    readonly_fields = ('is_realtime', 'user')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate_spent_time()

    @admin.display(description='Потрачено времени')
    def get_spent_time(self, instance):
        return instance.spent_time


class TimeSlotTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user')
    search_fields = ('title',)
    list_filter = ('user',)


admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(TimeSlotTag, TimeSlotTagAdmin)
