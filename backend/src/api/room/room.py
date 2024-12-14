from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from src.apps.room.services.room_service import RoomService
from src.apps.room.serializers.room import RoomSerializer
from src.apps.core.repositories.redis_repository import RedisRepository


class RoomViewSet(ViewSet):
    lookup_field = "room_id"
    repository = RedisRepository()
    service = RoomService(repository)
    serializer_class = RoomSerializer

    def list(self, request):
        rooms = self.service.get_rooms()
        serializer = self.serializer_class(rooms, many=True)
        return Response({"status": "success", "data": serializer.data}, status=200)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room_data = self.service.create_room(serializer.validated_data)
            return Response(
                {"status": "success", "message": "Room created", "data": room_data},
                status=201,
            )
        except ValueError as e:
            return Response({"status": "error", "message": str(e)}, status=400)


    def retrieve(self, request, room_id:str=None):
        room = self.service.get_room(room_id)
        serializer = self.serializer_class(room)
        return Response({"status": "success", "data": serializer.data}, status=200)


    def destroy(self, request, room_id:str=None):
        self.service.delete_room(room_id)
        return Response({"status": "success", "message": "Room deleted"}, status=200)
