from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Match, MatchParticipation
from .serializers import MatchSerializer, MatchParticipationSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all().order_by("-date", "-time")
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # the logged-in user becomes created_by
        serializer.save(created_by=self.request.user.profile)

    @action(detail=True, methods=["get"])
    def participants(self, request, pk=None):
        match = self.get_object()
        participations = match.participations.select_related("player", "team")
        serializer = MatchParticipationSerializer(participations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        """
        Current user joins the match.
        Optional JSON body: {"status": "going" | "maybe" | "not_going"}
        Capacity is applied for status="going".
        """
        match = self.get_object()
        profile = request.user.profile  # PlayerProfil

        desired_status = request.data.get("status", "going")
        if desired_status not in ["going", "maybe", "not_going"]:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        part, created = MatchParticipation.objects.get_or_create(
            match=match,
            player=profile,
        )

        # capacity check only if status=going
        if desired_status == "going":
            confirmed_count = match.participations.filter(status="going").exclude(id=part.id).count()
            if confirmed_count >= match.max_players:
                part.status = "waiting"
            else:
                part.status = "going"
        else:
            part.status = desired_status

        part.save()
        serializer = MatchParticipationSerializer(part)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        """
        Current user leaves the match.
        """
        match = self.get_object()
        profile = request.user.profile
        deleted, _ = MatchParticipation.objects.filter(match=match, player=profile).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "You were not registered for this match."}, status=status.HTTP_400_BAD_REQUEST)
