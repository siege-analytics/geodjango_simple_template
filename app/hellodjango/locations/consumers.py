"""
WebSocket consumers for real-time location updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Place
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


class LocationUpdateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for location updates
    Clients can subscribe to location changes in real-time
    """

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_group_name = 'location_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to location updates'
        }))

    async def disconnect(self, close_code):
        """Leave room group on disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        Expected format: {"action": "get_places", "lat": 33.4, "lon": -111.9, "radius": 1000}
        """
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'get_places':
            places = await self.get_nearby_places(
                lat=data.get('lat'),
                lon=data.get('lon'),
                radius=data.get('radius', 1000)
            )
            await self.send(text_data=json.dumps({
                'type': 'places_list',
                'places': places
            }))
        
        elif action == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'message': 'Server is alive'
            }))

    async def location_update(self, event):
        """
        Receive location update from room group
        """
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_nearby_places(self, lat, lon, radius):
        """
        Get places within radius of point
        """
        point = Point(lon, lat, srid=4326)
        distance = Distance(m=radius)
        
        places = Place.objects.filter(
            geom__dwithin=(point, distance)
        )[:20]  # Limit to 20
        
        return [{
            'id': p.id,
            'name': p.name,
            'lat': p.geom.y if p.geom else None,
            'lon': p.geom.x if p.geom else None,
        } for p in places]


class LiveLocationConsumer(AsyncWebsocketConsumer):
    """
    Simple WebSocket consumer for testing
    Echoes back messages and provides live updates
    """

    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'WebSocket connection established'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        """
        Echo back received message
        """
        data = json.loads(text_data)
        
        # Echo back with timestamp
        import datetime
        await self.send(text_data=json.dumps({
            'type': 'echo',
            'original': data,
            'timestamp': datetime.datetime.now().isoformat(),
            'message': 'Message received and echoed back'
        }))

