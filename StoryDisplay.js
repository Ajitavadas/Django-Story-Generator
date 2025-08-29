// StoryDisplay.js - Display generated stories
import React from 'react';
import { Download, Share, RefreshCw } from 'lucide-react';
import ImageViewer from './ImageViewer';

const StoryDisplay = ({ story, onRegenerate }) => {
  if (!story) return null;

  const handleDownloadImage = () => {
    if (story.composed_image) {
      const link = document.createElement('a');
      link.href = story.composed_image;
      link.download = `story_${story.id}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'My Generated Story',
        text: story.story_text.substring(0, 100) + '...',
        url: window.location.href,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <div className="story-display">
      <div className="story-header">
        <h2>Your Generated Story</h2>
        <div className="story-actions">
          <button
            className="action-btn"
            onClick={onRegenerate}
            title="Generate Another"
          >
            <RefreshCw size={16} />
          </button>
          <button
            className="action-btn"
            onClick={handleShare}
            title="Share Story"
          >
            <Share size={16} />
          </button>
          {story.composed_image && (
            <button
              className="action-btn"
              onClick={handleDownloadImage}
              title="Download Image"
            >
              <Download size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="story-content">
        {/* Generated Image */}
        {story.composed_image && (
          <div className="story-image-section">
            <ImageViewer
              images={{
                composed: story.composed_image,
                character: story.character_image,
                background: story.background_image,
              }}
            />
          </div>
        )}

        {/* Story Text */}
        <div className="story-text-section">
          <h3>The Story</h3>
          <div className="story-text">
            {story.story_text}
          </div>
        </div>

        {/* Character Description */}
        {story.character_description && (
          <div className="character-section">
            <h3>Main Character</h3>
            <div className="character-description">
              {story.character_description}
            </div>
          </div>
        )}

        {/* Transcription (if from audio) */}
        {story.transcribed_text && (
          <div className="transcription-section">
            <h4>From your audio:</h4>
            <div className="transcribed-text">
              "{story.transcribed_text}"
            </div>
          </div>
        )}

        {/* Generation Info */}
        <div className="generation-info">
          <small>
            Generated in {story.processing_time ? `${story.processing_time.toFixed(1)}s` : 'processing...'}
            {story.generation_parameters?.model_used && (
              <span> using {story.generation_parameters.model_used}</span>
            )}
          </small>
        </div>
      </div>
    </div>
  );
};

export default StoryDisplay;
