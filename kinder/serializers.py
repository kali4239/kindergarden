from rest_framework import serializers
from .models import GameProgressGroup, PuzzleGameRecord,  ChimpGameRecord, XOGame, PredictionGameRecord
class GameProgressGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameProgressGroup
        fields = '__all__'

class PuzzleGameRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuzzleGameRecord
        fields = '__all__'

class ChimpGameRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChimpGameRecord
        fields = '__all__'

class XOGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = XOGame
        fields = '__all__'

class PredictionGameRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionGameRecord
        fields = '__all__'
        