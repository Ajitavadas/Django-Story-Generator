// StoryForm.js - Main form component
import React, { useState } from 'react';
import { Upload, Mic, Send, Loader } from 'lucide-react';
import AudioUpload from './AudioUpload';

const StoryForm = ({ onSubmit, loading }) => {
  const [prompt, setPrompt] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [useAudio, setUseAudio] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!prompt && !audioFile) {
      setError('Please provide either a text prompt or audio file');
      return;
    }

    const formData = new FormData();
    if (prompt) formData.append('user_prompt', prompt);
    if (audioFile) formData.append('audio_file', audioFile);

    try {
      await onSubmit(formData);
      // Reset form on success
      setPrompt('');
      setAudioFile(null);
      setUseAudio(false);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    }
  };

  return (
    <div className="story-form-container">
      <div className="story-form-card">
        <h2 className="form-title">Generate Your Story</h2>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="story-form">
          {/* Input Method Toggle */}
          <div className="input-toggle">
            <button
              type="button"
              className={`toggle-btn ${!useAudio ? 'active' : ''}`}
              onClick={() => setUseAudio(false)}
            >
              <Send size={16} />
              Text Prompt
            </button>
            <button
              type="button"
              className={`toggle-btn ${useAudio ? 'active' : ''}`}
              onClick={() => setUseAudio(true)}
            >
              <Mic size={16} />
              Audio Upload
            </button>
          </div>

          {/* Text Input */}
          {!useAudio && (
            <div className="form-group">
              <label htmlFor="prompt">Your Story Prompt</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the story you'd like me to create... (e.g., 'A brave knight discovers a magical forest')"
                rows={4}
                className="form-textarea"
              />
            </div>
          )}

          {/* Audio Upload */}
          {useAudio && (
            <div className="form-group">
              <AudioUpload
                onAudioSelect={setAudioFile}
                selectedFile={audioFile}
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || (!prompt && !audioFile)}
            className="submit-btn"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={16} />
                Generating Story...
              </>
            ) : (
              <>
                <Send size={16} />
                Generate Story
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default StoryForm;
