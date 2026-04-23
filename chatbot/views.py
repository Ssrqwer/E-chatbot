from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer
from .services import GeminiService


class ChatAPIView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = GeminiService()
            reply = service.chat(
                serializer.validated_data['message'],
                serializer.validated_data.get('history', [])
            )
            return Response({'reply': reply})
        except Exception as e:
            return Response({'reply': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
