from django.contrib import admin
from .models import (PlayerProfil, Match, Team, MatchParticipation, BadgeType, Badge, MatchComment, MatchHighlight)

class TeamInline(admin.TabularInline):
    model = Team
    extra = 2

class ParticipationInline(admin.TabularInline):
    model = MatchParticipation
    extra = 0
    fields = ("player", "team", "status", "goals", "assists", "is_mvp", "has_paid")
    autocomplete_fields = ("player", "team")

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "match", "score")
    search_fields = ("name", "match__title", "match__location")
    
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "location", "max_players", "final_score", "confirmed_count")
    list_filter = ("date", "location", "final_score")
    search_fields = ("title", "location", "notes")
    inlines = [TeamInline, ParticipationInline]

@admin.register(MatchParticipation)
class MatchParticipationAdmin(admin.ModelAdmin):
    list_display = ("match", "player", "status", "team", "actually_played", "goals", "assists", "is_mvp", "has_paid")
    list_filter = ("status", "actually_played", "is_mvp", "has_paid", "match__date")
    search_fields = ("match__title", "player__user__username", "player__nickname")
    autocomplete_fields = ("match", "player", "team")

@admin.register(PlayerProfil)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "preferred_position")
    search_fields = ("user__username", "nickname")

@admin.register(BadgeType)
class BadgeTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("player", "badge_type", "awarded_at", "period_start", "period_end")
    list_filter = ("badge_type", "awarded_at")

@admin.register(MatchComment)
class MatchCommentAdmin(admin.ModelAdmin):
    list_display = ("match", "author", "created_at")
    search_fields = ("text",)

@admin.register(MatchHighlight)
class MatchHighlightAdmin(admin.ModelAdmin):
    list_display = ("match", "added_by", "created_at")
