from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from .models import Match, MatchParticipation, Team, PlayerProfil
from .forms import ParticipationStatusForm, SetTeamForm, FinalizeMatchForm

class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "league/match_list.html"
    context_object_name = "matches"
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.order_by("-date", "-time")

@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    profile = request.user.profile
    participation = MatchParticipation.objects.filter(match=match, player=profile).first()
    teams = match.teams.all().order_by("id")
    participants = match.participations.select_related("player__user", "team").all()

    status_form = None
    if participation:
        status_form = ParticipationStatusForm(instance=participation)

    return render(request, "league/match_detail.html", {
        "match": match,
        "participation": participation,
        "teams": teams,
        "participants": participants,
        "status_form": status_form,
    })

@login_required
def join_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    profile = request.user.profile

    part, created = MatchParticipation.objects.get_or_create(match=match, player=profile)
    # naive capacity enforcement
    confirmed_count = match.participations.filter(status="going").count()
    if confirmed_count >= match.max_players:
        part.status = "waiting"
        messages.info(request, "Match is full, you’re on the waiting list.")
    else:
        part.status = "going"
        messages.success(request, "You’ve joined this match.")
    part.save()
    return redirect("league:match_detail", pk=pk)

@login_required
def leave_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    profile = request.user.profile
    MatchParticipation.objects.filter(match=match, player=profile).delete()
    messages.success(request, "You’ve left this match.")
    return redirect("league:match_detail", pk=pk)

@login_required
def set_status(request, pk):
    match = get_object_or_404(Match, pk=pk)
    profile = request.user.profile
    part = get_object_or_404(MatchParticipation, match=match, player=profile)

    if request.method == "POST":
        form = ParticipationStatusForm(request.POST, instance=part)
        if form.is_valid():
            status = form.cleaned_data["status"]
            # Capacity check only for "going"
            if status == "going":
                if match.participations.filter(status="going").exclude(id=part.id).count() >= match.max_players:
                    messages.warning(request, "No more slots — setting you to waiting list.")
                    part.status = "waiting"
                    part.save()
                else:
                    form.save()
                    messages.success(request, "Status updated.")
            else:
                form.save()
                messages.success(request, "Status updated.")
    return redirect("league:match_detail", pk=pk)

@login_required
def set_team(request, pk):
    match = get_object_or_404(Match, pk=pk)
    # Simple permission: only creator can assign teams
    if match.created_by != request.user.profile:
        messages.error(request, "Only the match organizer can assign teams.")
        return redirect("league:match_detail", pk=pk)

    if request.method == "POST":
        form = SetTeamForm(request.POST, match=match)
        if form.is_valid():
            part_id = form.cleaned_data["player_participation_id"]
            team = form.cleaned_data["team"]
            part = get_object_or_404(MatchParticipation, pk=part_id, match=match)
            part.team = team
            part.save()
            messages.success(request, "Team updated.")
    return redirect("league:match_detail", pk=pk)

@login_required
@transaction.atomic
def finalize_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if match.created_by != request.user.profile:
        messages.error(request, "Only the match organizer can finalize the match.")
        return redirect("league:match_detail", pk=pk)

    if request.method == "POST":
        form = FinalizeMatchForm(request.POST, match=match)
        if form.is_valid():
            # Save team scores
            for team in match.teams.all():
                team.score = form.cleaned_data[f"score_{team.id}"]
                team.save()

            # Update attendance (played/no_show)
            for p in match.participations.all():
                p.actually_played = form.cleaned_data.get(f"played_{p.id}", False)
                p.no_show = form.cleaned_data.get(f"no_show_{p.id}", False)
                p.save()

            match.is_finished = True
            match.save()
            messages.success(request, "Match finalized.")
            return redirect("league:match_detail", pk=pk)
    else:
        form = FinalizeMatchForm(match=match)

    return render(request, "league/finalize_match.html", {"match": match, "form": form})
