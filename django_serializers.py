"""
DRF Serializers for the story generator.
"""
from rest_framework import serializers
from .models import Story, GenerationLog

class GenerationLogSerializer(serializers.ModelSerializer):
    """Serializer for generation logs."""

    class Meta:
        model = GenerationLog
        fields = [
            'step', 'status', 'started_at', 'completed_at',
            'duration', 'error_message', 'service_used'
        ]

class StorySerializer(serializers.ModelSerializer):
    """Serializer for Story model."""

    logs = GenerationLogSerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = [
            'id', 'user_prompt', 'transcribed_text', 'story_text',
            'character_description', 'character_image', 'background_image',
            'composed_image', 'generation_parameters', 'processing_time',
            'created_at', 'updated_at', 'logs'
        ]
        read_only_fields = [
            'id', 'transcribed_text', 'story_text', 'character_description',
            'character_image', 'background_image', 'composed_image',
            'generation_parameters', 'processing_time', 'created_at',
            'updated_at', 'logs'
        ]

class StoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new stories."""

    class Meta:
        model = Story
        fields = ['user_prompt', 'audio_file']

    def validate(self, data):
        """Validate that either prompt or audio is provided."""
        if not data.get('user_prompt') and not data.get('audio_file'):
            raise serializers.ValidationError(
                "Either user_prompt or audio_file must be provided."
            )
        return data

    def validate_audio_file(self, value):
        """Validate audio file format and size."""
        if value:
            # Check file size (10MB limit)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Audio file too large. Maximum size is 10MB."
                )

            # Check file extension
            allowed_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
            file_extension = value.name.lower().split('.')[-1]

            if f'.{file_extension}' not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Unsupported audio format. Allowed formats: {allowed_extensions}"
                )

        return value

class StoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for story listings."""

    class Meta:
        model = Story
        fields = [
            'id', 'user_prompt', 'created_at', 'processing_time',
            'composed_image'
        ]
