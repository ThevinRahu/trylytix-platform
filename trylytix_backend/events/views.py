from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
import csv
import io

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=False, methods=['post'], url_path='upload-csv')
    def upload_csv(self, request):
        file = request.FILES.get('file')
        match_id = request.data.get('match_id')

        if not file or not match_id:
            return Response({'error': 'file and match_id required'}, status=400)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        events_created = 0
        for row in reader:
            Event.objects.create(
                match_id=match_id,
                event_type=row.get('event_type'),
                timestamp=row.get('timestamp'),
                x_coord=row.get('x'),
                y_coord=row.get('y'),
                location_zone=row.get('zone', ''),
                description=row.get('description', ''),
                player_id=row.get('player_id', ''),
                team_id=row.get('team_id', ''),
                is_opponent_event=row.get('is_opponent_event', 'false').lower() == 'true'
            )
            events_created += 1

        return Response({'message': f'{events_created} events uploaded'})
