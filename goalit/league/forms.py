from django import forms
from .models import MatchParticipation, Team

class ParticipationStatusForm(forms.ModelForm):
    class Meta:
        model = MatchParticipation
        fields = ["status"]

class SetTeamForm(forms.Form):
    player_participation_id = forms.IntegerField(widget=forms.HiddenInput)
    team = forms.ModelChoiceField(queryset=Team.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        match = kwargs.pop("match")
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = match.teams.all()

class FinalizeMatchForm(forms.Form):
    # Minimal: set team scores & mark who actually played
    def __init__(self, *args, **kwargs):
        match = kwargs.pop("match")
        super().__init__(*args, **kwargs)
        for team in match.teams.all():
            self.fields[f"score_{team.id}"] = forms.IntegerField(min_value=0, initial=team.score, required=True)

        for p in match.participations.all():
            self.fields[f"played_{p.id}"] = forms.BooleanField(required=False, initial=p.actually_played)
            self.fields[f"no_show_{p.id}"] = forms.BooleanField(required=False, initial=p.no_show)
