from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'model'])
    content = serializers.CharField(max_length=1000)


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)
    history = MessageSerializer(many=True, required=False, default=list)
