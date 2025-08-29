// AudioUpload.js - Audio file upload component
import React, { useRef, useState } from 'react';
import { Upload, X, Play, Pause } from 'lucide-react';

const AudioUpload = ({ onAudioSelect, selectedFile }) => {
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/m4a'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid audio file (WAV, MP3, OGG, M4A)');
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }

      onAudioSelect(file);

      // Create audio URL for preview
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      const newAudioUrl = URL.createObjectURL(file);
      setAudioUrl(newAudioUrl);
    }
  };

  const handleRemoveFile = () => {
    onAudioSelect(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setIsPlaying(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  return (
    <div className="audio-upload">
      <label htmlFor="audio-file">Audio File</label>

      {!selectedFile ? (
        <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
          <Upload size={24} />
          <p>Click to upload audio file</p>
          <p className="upload-hint">Supports WAV, MP3, OGG, M4A (max 10MB)</p>
        </div>
      ) : (
        <div className="selected-file">
          <div className="file-info">
            <span className="file-name">{selectedFile.name}</span>
            <span className="file-size">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>

          <div className="file-controls">
            {audioUrl && (
              <button
                type="button"
                className="play-btn"
                onClick={togglePlayback}
              >
                {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              </button>
            )}

            <button
              type="button"
              className="remove-btn"
              onClick={handleRemoveFile}
            >
              <X size={16} />
            </button>
          </div>

          {audioUrl && (
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={handleAudioEnded}
              style={{ display: 'none' }}
            />
          )}
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        id="audio-file"
        accept=".wav,.mp3,.ogg,.m4a"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default AudioUpload;
