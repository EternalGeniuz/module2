from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import (
    RegistrationForm,
    AuthForm,
    TimeSlotForm,
    TimeSlotTagForm,
    HolidayForm,
    TimeSlotFilterForm,
)
from .models import TimeSlot, TimeSlotTag, Holiday

User = get_user_model()


@login_required
def main_view(request):
    timeslots = TimeSlot.objects.filter(user=request.user).order_by("-start_date")
    current_timeslot = timeslots.filter(end_date__isnull=True).first()

    filter_form = TimeSlotFilterForm(request.GET)
    filter_form.is_valid()
    filters = filter_form.cleaned_data

    if filters["search"]:
        timeslots = timeslots.filter(title__icontains=filters["search"])

    if filters["is_realtime"] is not None:
        timeslots = timeslots.filter(is_realtime=filters["is_realtime"])

    if filters["start_date"]:
        timeslots = timeslots.filter(start_date__gte=filters["start_date"])

    if filters["end_date"]:
        timeslots = timeslots.filter(end_date__lte=filters["end_date"])

    total_count = timeslots.count()
    timeslots = (
        timeslots.prefetch_related("tags")
        .select_related("user")
        .annotate(tags_count=Count("tags"), spent_time=F("end_date") - F("start_date"))
    )

    page_number = request.GET.get("page", 1)
    paginator = Paginator(timeslots, per_page=10)

    return render(
        request,
        "web/main.html",
        {
            "current_timeslot": current_timeslot,
            "timeslots": paginator.get_page(page_number),
            "form": TimeSlotForm(),
            "filter_form": filter_form,
            "total_count": total_count,
        },
    )


@login_required
def analytics_view(request):
    overall_stat = TimeSlot.objects.aggregate(
        Count("id"),
        Max("end_date"),
        Min("start_date")
    )

    days_stat = (
        TimeSlot.objects.exclude(end_date__isnull=True)
        .annotate(date=TruncDate("start_date"))
        .values("date")
        .annotate(
            count=Count("id"),
            realtime_count=Count("id", filter=Q(is_realtime=True)),
            spent_time=Sum(F("end_date") - F("start_date"))
        )
        .order_by("-date")
    )

    return render(request, "web/analytics.html", {
        "overall_stat": overall_stat,
        "days_stat": days_stat
    })


def registration_view(request):
    form = RegistrationForm()
    is_success = False
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
            )
            user.set_password(form.cleaned_data["password"])
            user.save()
            is_success = True
    return render(
        request,
        "web/registration.html",
        {
            "form": form,
            "is_success": is_success
        }
    )


def auth_view(request):
    form = AuthForm()
    if request.method == "POST":
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is None:
                form.add_error(None, "Введены неверные данные!")
            else:
                login(request, user)
                return redirect("main")
    return render(request, "web/auth.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("main")


@login_required
def time_slot_add_view(request):
    form = TimeSlotForm()
    if request.method == "POST":
        form = TimeSlotForm(data=request.POST, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, "web/time_slot_form.html", {"form": form})


@login_required
def time_slot_edit_view(request, id=None):
    timeslot = None
    if id is not None:
        timeslot = get_object_or_404(TimeSlot, user=request.user, id=id)
    form = TimeSlotForm(instance=timeslot)
    if request.method == "POST":
        form = TimeSlotForm(
            data=request.POST,
            files=request.FILES,
            initial={"user": request.user},
            instance=timeslot,
        )
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, "web/time_slot_form.html", {"form": form})


@login_required
def time_slot_stop_view(request, id):
    if request.method == "POST":
        timeslot = get_object_or_404(TimeSlot, user=request.user, id=id)
        timeslot.end_date = timezone.now()
        timeslot.save()
    return redirect("main")


@login_required
def time_slot_delete_view(request, id):
    tag = get_object_or_404(TimeSlot, user=request.user, id=id)
    tag.delete()
    return redirect("main")


def _list_editor_view(request, model_cls, form_cls, template_name, url_name):
    items = model_cls.objects.filter(user=request.user)
    form = form_cls()
    if request.method == "POST":
        form = form_cls(
            data=request.POST,
            initial={"user": request.user},
        )
        if form.is_valid():
            form.save()
            return redirect(url_name)
    return render(
        request,
        f"web/{template_name}.html",
        {
            "items": items,
            "form": form
        }
    )


@login_required
def tags_view(request):
    return _list_editor_view(request, TimeSlotTag, TimeSlotTagForm, "tags", "tags")


@login_required
def tags_delete_view(request, id):
    tag = get_object_or_404(TimeSlotTag, user=request.user, id=id)
    tag.delete()
    return redirect("tags")


@login_required
def holidays_view(request):
    return _list_editor_view(request, Holiday, HolidayForm, "holidays", "holidays")


@login_required
def holidays_delete_view(request, id):
    holiday = get_object_or_404(Holiday, user=request.user, id=id)
    holiday.delete()
    return redirect("holidays")
