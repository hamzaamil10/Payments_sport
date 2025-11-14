from django.db import models
from django.contrib.auth.models import User

class PlayerProfil(models.Model):
    position_choices = [('GK', 'Goalkeeper'),('DEF', 'Defender'),('MID', 'Midfielder'),('FW', 'Forward'),('ANY', 'Any'),]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True)
    preferred_position = models.CharField(max_length=4, choices=position_choices, default='ANY')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.nickname or self.user.username
    

class Match (models.Model):
    title = models.CharField(max_length=500, default='FRIENDLY MATCH')
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=500)
    price_per_player = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    max_players = models.PositiveIntegerField(default=14)
    created_by = models.ForeignKey(PlayerProfil, on_delete=models.SET_NULL, null=True, related_name='created_matches')
    final_score = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.date} @ {self.time}"
    
    @property
    def participants(self):
        return self.participations.filter(status='going')

    @property
    def confirmed_count(self):
        return self.participants.count()


class Team(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=50)
    score = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.match})"
    
class MatchParticipation(models.Model):
    STATUS_CHOICES = [('going', 'Going'),('maybe', 'Maybe'),('not_going', 'Not Going'),]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participations')
    player = models.ForeignKey(PlayerProfil, on_delete=models.CASCADE, related_name='participations')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    # Availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    actually_played = models.BooleanField(default=False)  # checked after the match
    no_show = models.BooleanField(default=False)         # confirmed but didn’t come

    # Stats
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    is_mvp = models.BooleanField(default=False)

    # Money
    has_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player} @ {self.match}"

    def points_earned(self):
        if not self.actually_played:
            return -50 if self.no_show else 0  # penalty for no-show

        points = 100  # base for playing
        points += self.goals * 30
        points += self.assists * 20
        if self.is_mvp:
            points += 40
        if self.goals >= 3:
            points += 30  # hat-trick bonus

        return points
    

class BadgeType(models.Model):
    code = models.CharField(max_length=50, unique=True)  
    name = models.CharField(max_length=100)              
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Badge(models.Model):
    player = models.ForeignKey(PlayerProfil, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.ForeignKey(BadgeType, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.badge_type} -> {self.player}"

class MatchComment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(PlayerProfil, on_delete=models.SET_NULL, null=True, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.match}"

class MatchHighlight(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='highlights')
    added_by = models.ForeignKey(PlayerProfil, on_delete=models.SET_NULL, null=True, related_name='highlights')
    image = models.ImageField(upload_to='highlights/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Highlight for {self.match}"