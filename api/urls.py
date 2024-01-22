from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from .views import main_view, TimeSlotModelViewSet, TagsModelViewSet

router = SimpleRouter()
router.register("timeslots", TimeSlotModelViewSet, basename='timeslots')
router.register("tags", TagsModelViewSet, basename='tags')

urlpatterns = [
    path('', main_view),
    path('token/', obtain_auth_token),
    *router.urls
]