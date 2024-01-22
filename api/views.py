from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import TimeSlotSerializer, TagSerializer
from web.models import TimeSlot, TimeSlotTag


@api_view(["GET"])
def main_view(request):
    return Response({"status": "ok"})


class TimeSlotModelViewSet(ModelViewSet):
    serializer_class = TimeSlotSerializer

    def get_queryset(self):
        return (
            TimeSlot.objects.all()
            .select_related("user")
            .prefetch_related("tags")
            .filter(user=self.request.user)
        )


class TagsModelViewSet(ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        return (
            TimeSlotTag.objects.all()
            .filter(user=self.request.user)
        )