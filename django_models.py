"""
Django models for the story generator application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid
import os

class Story(models.Model):
    """Model for storing generated stories and metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_prompt = models.TextField(help_text="Original user prompt")
    audio_file = models.FileField(
        upload_to='uploads/audio/',
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'ogg', 'm4a'])],
        blank=True,
        null=True,
        help_text="Optional audio file for speech-to-text"
    )
    transcribed_text = models.TextField(blank=True, help_text="Text from speech-to-text")

    # Generated content
    story_text = models.TextField(help_text="Generated story content")
    character_description = models.TextField(help_text="Generated character description")

    # Image references
    character_image = models.ImageField(
        upload_to='media/generated/images/characters/',
        blank=True,
        null=True
    )
    background_image = models.ImageField(
        upload_to='media/generated/images/backgrounds/',
        blank=True,
        null=True
    )
    composed_image = models.ImageField(
        upload_to='media/generated/compositions/',
        blank=True,
        null=True
    )

    # Generation metadata
    generation_parameters = models.JSONField(
        default=dict,
        help_text="Parameters used for AI generation"
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Total processing time in seconds"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional user association
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Story {self.id} - {self.user_prompt[:50]}..."

    def save(self, *args, **kwargs):
        # Create directories if they don't exist
        super().save(*args, **kwargs)


class GenerationLog(models.Model):
    """Log individual generation steps for debugging and monitoring."""

    STEP_CHOICES = [
        ('speech_to_text', 'Speech to Text'),
        ('story_generation', 'Story Generation'),
        ('character_generation', 'Character Description'),
        ('character_image', 'Character Image'),
        ('background_image', 'Background Image'),
        ('image_composition', 'Image Composition'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='logs')
    step = models.CharField(max_length=50, choices=STEP_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True, help_text="Duration in seconds")

    # Results and errors
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Service information
    service_used = models.CharField(max_length=100, blank=True)
    model_used = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['started_at']
        indexes = [
            models.Index(fields=['story', 'step']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.story.id} - {self.step} - {self.status}"


class AIServiceConfig(models.Model):
    """Configuration for AI services."""

    service_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    config_data = models.JSONField(default=dict)
    rate_limit_per_minute = models.IntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name} ({'Active' if self.is_active else 'Inactive'})"
