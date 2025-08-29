// App.js - Main React application
import React, { useState, useEffect } from 'react';
import { BookOpen, Sparkles } from 'lucide-react';
import StoryForm from './components/StoryForm';
import StoryDisplay from './components/StoryDisplay';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [currentStory, setCurrentStory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recentStories, setRecentStories] = useState([]);

  // Load recent stories on mount
  useEffect(() => {
    loadRecentStories();
  }, []);

  const loadRecentStories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stories/`);
      if (response.ok) {
        const data = await response.json();
        setRecentStories(data.results || []);
      }
    } catch (err) {
      console.error('Failed to load recent stories:', err);
    }
  };

  const handleGenerateStory = async (formData) => {
    setLoading(true);
    setError('');
    setCurrentStory(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/stories/generate/`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setCurrentStory(data.story);
        loadRecentStories(); // Refresh recent stories
      } else {
        throw new Error(data.error || 'Failed to generate story');
      }
    } catch (err) {
      setError(err.message);
      console.error('Generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = () => {
    setCurrentStory(null);
    setError('');
  };

  const handleSelectRecentStory = (story) => {
    setCurrentStory(story);
    setError('');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <BookOpen size={32} />
            <h1>AI Story Generator</h1>
            <Sparkles size={24} className="sparkle" />
          </div>
          <p className="tagline">
            Transform your ideas into captivating stories with AI-generated text and images
          </p>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError('')}>×</button>
          </div>
        )}

        <div className="content-grid">
          {/* Generation Form */}
          <div className="form-section">
            <StoryForm
              onSubmit={handleGenerateStory}
              loading={loading}
            />

            {/* Recent Stories */}
            {recentStories.length > 0 && !currentStory && (
              <div className="recent-stories">
                <h3>Recent Stories</h3>
                <div className="stories-grid">
                  {recentStories.slice(0, 6).map((story) => (
                    <div
                      key={story.id}
                      className="story-card"
                      onClick={() => handleSelectRecentStory(story)}
                    >
                      {story.composed_image && (
                        <img
                          src={story.composed_image}
                          alt="Story scene"
                          className="story-thumbnail"
                        />
                      )}
                      <div className="story-preview">
                        <p>{story.user_prompt}</p>
                        <small>
                          {new Date(story.created_at).toLocaleDateString()}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Story Display */}
          <div className="display-section">
            {loading && (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <h3>Generating Your Story...</h3>
                <p>This may take a few moments as we create your story and images.</p>
                <div className="generation-steps">
                  <div className="step">📝 Writing your story</div>
                  <div className="step">🎭 Describing characters</div>
                  <div className="step">🎨 Creating images</div>
                  <div className="step">🖼️ Composing final scene</div>
                </div>
              </div>
            )}

            {currentStory && (
              <StoryDisplay
                story={currentStory}
                onRegenerate={handleRegenerate}
              />
            )}

            {!currentStory && !loading && (
              <div className="welcome-state">
                <Sparkles size={48} />
                <h3>Ready to Create</h3>
                <p>
                  Enter a prompt or upload an audio file to generate your unique story
                  with AI-powered text and images.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Powered by LangChain, HuggingFace, and free AI services
        </p>
      </footer>
    </div>
  );
}

export default App;
