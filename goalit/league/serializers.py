from rest_framework import serializers
from .models import PlayerProfil, Match, Team, MatchParticipation


class PlayerProfilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # shows username

    class Meta:
        model = PlayerProfil
        fields = ["id", "user", "nickname", "preferred_position", "bio"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "score"]


class MatchSerializer(serializers.ModelSerializer):
    created_by = PlayerProfilSerializer(read_only=True)
    confirmed_count = serializers.SerializerMethodField()
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "title",
            "date",
            "time",
            "location",
            "price_per_player",
            "notes",
            "max_players",
            "final_score",
            "created_by",
            "confirmed_count",
            "teams",
        ]

    def get_confirmed_count(self, obj):
        return obj.confirmed_count


class MatchParticipationSerializer(serializers.ModelSerializer):
    player = PlayerProfilSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = MatchParticipation
        fields = [
            "id",
            "match",
            "player",
            "team",
            "status",
            "actually_played",
            "no_show",
            "goals",
            "assists",
            "is_mvp",
            "has_paid",
        ]
        read_only_fields = ["match", "player", "team"]

status = serializers.SerializerMethodField()
def get_status(self, obj):
    return "finalized" if obj.final_score else "open"
