from django import forms
from .models import MatchParticipation, Team
from django.contrib.auth.models import User

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
    pass
    

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        pw2 = cleaned_data.get("password_confirm")

        if pw != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data