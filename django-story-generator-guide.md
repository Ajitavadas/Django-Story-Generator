# Complete Development Guide: Django LangChain Story Generator with Docker

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites and Setup](#prerequisites-and-setup)
3. [Project Structure Creation](#project-structure-creation)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Docker Configuration](#docker-configuration)
7. [Environment Configuration](#environment-configuration)
8. [AI Services Integration](#ai-services-integration)
9. [Testing and Debugging](#testing-and-debugging)
10. [Production Deployment](#production-deployment)
11. [API Documentation](#api-documentation)
12. [Troubleshooting](#troubleshooting)

## Project Overview

This guide walks you through building a comprehensive **Django LangChain Story Generator** web application that:

- Takes text prompts or audio input from users
- Generates creative stories using LangChain and free AI services
- Creates character descriptions and generates images
- Composes character and background images into unified scenes
- Provides a modern React frontend with Django REST API backend
- Uses only **free and open-source AI services** (HuggingFace, Stable Diffusion)
- Implements proper error handling, logging, and monitoring
- Includes comprehensive Docker setup for development and production

### Key Technologies Used

**Backend:**
- Django 5.0+ with Django REST Framework
- LangChain for AI orchestration  
- PostgreSQL database
- HuggingFace Transformers & Inference API (free tier)
- PIL/Pillow for image composition
- SpeechRecognition for audio processing

**Frontend:**
- React 18+ with modern hooks
- Responsive design with CSS Grid/Flexbox
- File upload with drag-and-drop
- Audio playback controls
- Image galleries and viewers

**Infrastructure:**
- Docker & Docker Compose
- Nginx reverse proxy
- Redis for caching (optional)
- GitHub Actions for CI/CD (optional)

## Prerequisites and Setup

### Required Software

1. **Docker Desktop** (v4.37+)
   ```bash
   # Download from: https://www.docker.com/products/docker-desktop/
   ```

2. **VS Code** with extensions:
   ```bash
   # Install these extensions:
   # - Dev Containers (ms-vscode-remote.remote-containers)
   # - Docker (ms-azuretools.vscode-docker)
   # - Python (ms-python.python)
   # - ES7+ React/Redux/React-Native snippets
   ```

3. **Git** for version control
   ```bash
   git --version
   # Should show version 2.30+
   ```

### Free AI Service Accounts

1. **HuggingFace Account** (Free tier: 1000 requests/hour)
   - Sign up at: https://huggingface.co/join
   - Generate API token: https://huggingface.co/settings/tokens
   - Free tier includes access to thousands of models

2. **Google Speech-to-Text** (Optional, 60 minutes/month free)
   - Create Google Cloud account
   - Enable Speech-to-Text API
   - Generate service account key

## Project Structure Creation

### Step 1: Initialize Project Directory

```bash
# Create main project directory
mkdir django-story-generator
cd django-story-generator

# Create the complete project structure
mkdir -p {story_generator/{settings,},apps/stories/{migrations,langchain_handlers,ai_services,utils},frontend/{src/{components,services},public},requirements,docker,static/{css,js,images},media/uploads/{audio,generated/{stories,images,compositions}},docs,.devcontainer}
```

### Step 2: Create Base Configuration Files

Create `.env.example`:
```bash
# Database Configuration
DB_NAME=story_generator
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Service Keys (Free Tiers)
HUGGINGFACE_API_KEY=your-huggingface-token
GOOGLE_SPEECH_API_KEY=your-google-api-key

# Port Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
REDIS_PORT=6379

# Development Settings
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true
```

### Step 3: Create .gitignore
```bash
# Python
__pycache__/
*.py[cod]
*.so
.env
*.sqlite3
db.sqlite3

# Django
media/
staticfiles/
logs/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Backend Development

### Step 1: Django Project Setup

Create `manage.py`:
```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'story_generator.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
```

### Step 2: Django Settings Configuration

Create `story_generator/settings/base.py` with the base settings (use the previously created django_settings_base.py content).

Create `story_generator/settings/development.py`:
```python
from .base import *

DEBUG = True

# Additional development settings
INSTALLED_APPS += [
    'django_extensions',
]

# Allow all origins for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging for development
LOGGING['loggers']['apps.stories']['level'] = 'DEBUG'
```

### Step 3: Models Implementation

Create `apps/stories/models.py` using the previously created django_models.py content.

### Step 4: LangChain Integration

Create `apps/stories/langchain_handlers/story_chain.py` using the langchain_story_chain.py content.

### Step 5: AI Services Implementation

Create the AI service clients:

1. `apps/stories/ai_services/huggingface_client.py` (use huggingface_client.py)
2. `apps/stories/utils/image_composer.py` (use image_composer.py)  
3. `apps/stories/ai_services/speech_client.py` (use speech_client.py)

### Step 6: Views and Serializers

1. Create `apps/stories/serializers.py` (use django_serializers.py)
2. Create `apps/stories/views.py` (use django_views.py)

### Step 7: URL Configuration

Create `apps/stories/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoryViewSet

router = DefaultRouter()
router.register(r'stories', StoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

Create `story_generator/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.stories.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Frontend Development

### Step 1: Initialize React Application

Create `frontend/package.json`:
```json
{
  "name": "story-generator-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### Step 2: React Components

Create the React components using the previously created files:

1. `frontend/src/App.js` (use App.js)
2. `frontend/src/components/StoryForm.js` (use StoryForm.js)
3. `frontend/src/components/AudioUpload.js` (use AudioUpload.js)
4. `frontend/src/components/StoryDisplay.js` (use StoryDisplay.js)

### Step 3: Additional Components

Create `frontend/src/components/ImageViewer.js`:
```jsx
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, X, ZoomIn } from 'lucide-react';

const ImageViewer = ({ images }) => {
  const [currentView, setCurrentView] = useState('composed');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const imageOptions = [
    { key: 'composed', label: 'Complete Scene', image: images.composed },
    { key: 'character', label: 'Character', image: images.character },
    { key: 'background', label: 'Background', image: images.background },
  ].filter(option => option.image);

  const currentIndex = imageOptions.findIndex(option => option.key === currentView);

  const nextImage = () => {
    const nextIndex = (currentIndex + 1) % imageOptions.length;
    setCurrentView(imageOptions[nextIndex].key);
  };

  const prevImage = () => {
    const prevIndex = currentIndex === 0 ? imageOptions.length - 1 : currentIndex - 1;
    setCurrentView(imageOptions[prevIndex].key);
  };

  const currentImage = imageOptions[currentIndex];

  if (!currentImage) return null;

  return (
    <div className="image-viewer">
      <div className="image-controls">
        <div className="image-tabs">
          {imageOptions.map((option) => (
            <button
              key={option.key}
              className={`tab-btn ${currentView === option.key ? 'active' : ''}`}
              onClick={() => setCurrentView(option.key)}
            >
              {option.label}
            </button>
          ))}
        </div>
        
        <button
          className="fullscreen-btn"
          onClick={() => setIsFullscreen(true)}
        >
          <ZoomIn size={16} />
        </button>
      </div>

      <div className="image-container">
        {imageOptions.length > 1 && (
          <button className="nav-btn prev" onClick={prevImage}>
            <ChevronLeft size={20} />
          </button>
        )}
        
        <img
          src={currentImage.image}
          alt={currentImage.label}
          className="main-image"
          onClick={() => setIsFullscreen(true)}
        />
        
        {imageOptions.length > 1 && (
          <button className="nav-btn next" onClick={nextImage}>
            <ChevronRight size={20} />
          </button>
        )}
      </div>

      <div className="image-info">
        <span>{currentImage.label}</span>
        <span>({currentIndex + 1} of {imageOptions.length})</span>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fullscreen-overlay" onClick={() => setIsFullscreen(false)}>
          <button
            className="close-btn"
            onClick={() => setIsFullscreen(false)}
          >
            <X size={24} />
          </button>
          <img
            src={currentImage.image}
            alt={currentImage.label}
            className="fullscreen-image"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
};

export default ImageViewer;
```

### Step 4: Styling

Create `frontend/src/App.css`:
```css
/* App.css - Complete styling for the story generator */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header Styles */
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  padding: 0 2rem;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.logo h1 {
  color: #2d3748;
  font-size: 2.5rem;
  font-weight: 700;
}

.sparkle {
  color: #f6ad55;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.2) rotate(180deg); }
}

.tagline {
  color: #4a5568;
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
}

/* Main Content */
.app-main {
  flex: 1;
  padding: 3rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.error-banner {
  background: #feb2b2;
  color: #c53030;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-banner button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #c53030;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: start;
}

/* Story Form Styles */
.story-form-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.form-title {
  color: #2d3748;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  text-align: center;
}

.input-toggle {
  display: flex;
  background: #edf2f7;
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  color: #2d3748;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 2rem;
}

.form-group label {
  display: block;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #667eea;
}

/* Audio Upload Styles */
.audio-upload label {
  display: block;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 0.5rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f7fafc;
}

.upload-area:hover {
  border-color: #667eea;
  background: #edf2f7;
}

.upload-hint {
  color: #718096;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.selected-file {
  background: #f7fafc;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
}

.file-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.file-name {
  font-weight: 600;
  color: #2d3748;
}

.file-size {
  color: #718096;
  font-size: 0.9rem;
}

.file-controls {
  display: flex;
  gap: 0.5rem;
}

.play-btn, .remove-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.play-btn {
  background: #667eea;
  color: white;
}

.play-btn:hover {
  background: #5a67d8;
}

.remove-btn {
  background: #e53e3e;
  color: white;
}

.remove-btn:hover {
  background: #c53030;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Loading State */
.loading-state {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.generation-steps {
  margin-top: 2rem;
  display: grid;
  gap: 1rem;
}

.generation-steps .step {
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}

/* Welcome State */
.welcome-state {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.welcome-state h3 {
  color: #2d3748;
  margin: 1rem 0;
}

/* Story Display */
.story-display {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.story-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 1rem;
}

.story-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  background: #edf2f7;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e2e8f0;
}

/* Recent Stories */
.recent-stories {
  margin-top: 3rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 1rem;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.story-card {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.story-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.story-thumbnail {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.story-preview {
  padding: 1rem;
}

.story-preview p {
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: #2d3748;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Footer */
.app-footer {
  background: rgba(255, 255, 255, 0.95);
  text-align: center;
  padding: 2rem;
  color: #718096;
  border-top: 1px solid #e2e8f0;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .logo h1 {
    font-size: 2rem;
  }
  
  .tagline {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .app-main {
    padding: 2rem 1rem;
  }
  
  .story-form-container,
  .story-display,
  .loading-state,
  .welcome-state {
    padding: 1.5rem;
  }
  
  .stories-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .input-toggle {
    flex-direction: column;
  }
  
  .toggle-btn {
    border-radius: 0.5rem;
    margin-bottom: 0.25rem;
  }
}

/* Animation Classes */
.animate-spin {
  animation: spin 1s linear infinite;
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## Docker Configuration

### Step 1: Backend Dockerfile

Create `docker/Dockerfile.backend`:
```dockerfile
# Multi-stage Dockerfile for Django backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libsndfile1-dev \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

# Development stage
FROM base as development

COPY requirements/development.txt .
RUN pip install --no-cache-dir -r development.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media/uploads/{audio,generated/{stories,images,compositions}} \
    && mkdir -p /app/logs \
    && mkdir -p /app/staticfiles

# Set permissions
RUN chmod +x manage.py

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production stage
FROM base as production

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Set ownership
RUN chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "story_generator.wsgi:application"]
```

### Step 2: Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
# Multi-stage build for React frontend
FROM node:20-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --silent

# Development stage
FROM base as development

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]

# Build stage
FROM base as build

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Copy build files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Step 3: Docker Compose Configuration

Use the previously created `docker-compose-full.yml` as your main `docker-compose.yml`.

### Step 4: Nginx Configuration

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        client_max_body_size 10M;
        
        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for React hot reload
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Django API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Django admin
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
        
        # Media files
        location /media/ {
            alias /var/www/media/;
            expires 7d;
            add_header Cache-Control "public";
        }
    }
}
```

## Environment Configuration

### Step 1: Create Environment Files

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env
```

### Step 2: Required Environment Variables

Make sure your `.env` file contains:

```bash
# Database
DB_NAME=story_generator
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=postgres
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=your-super-secret-django-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Services (Free Tier)
HUGGINGFACE_API_KEY=your-huggingface-token
# GOOGLE_SPEECH_API_KEY=your-google-key  # Optional

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80

# Development
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true
```

### Step 3: VS Code Dev Container Setup

Create `.devcontainer/devcontainer.json`:
```json
{
  "name": "Django LangChain Story Generator",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "backend",
  "workspaceFolder": "/app",
  "shutdownAction": "stopCompose",
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.pylint",
        "ms-python.black-formatter",
        "ms-vscode.vscode-typescript-next",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-docker",
        "ms-vscode.vscode-json"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.organizeImports": true
        }
      }
    }
  },

  "forwardPorts": [8000, 3000, 5432, 6379, 80],
  "portsAttributes": {
    "8000": {"label": "Django Backend"},
    "3000": {"label": "React Frontend"},
    "80": {"label": "Nginx Proxy"}
  },

  "postCreateCommand": "pip install -r requirements/development.txt && python manage.py migrate",
  
  "remoteUser": "root"
}
```

## AI Services Integration

### Step 1: HuggingFace Setup

1. **Create Account**: Visit https://huggingface.co/join
2. **Generate Token**: Go to https://huggingface.co/settings/tokens
3. **Add to Environment**: Update your `.env` file
4. **Test Connection**:
   ```python
   from apps.stories.ai_services.huggingface_client import HuggingFaceClient
   
   client = HuggingFaceClient()
   result = client.generate_text("Test prompt")
   print(result)
   ```

### Step 2: Free Models Configuration

Add to Django settings:
```python
# AI Model Configuration
AI_MODELS = {
    'text_generation': [
        'microsoft/DialoGPT-medium',
        'gpt2',
        'distilgpt2',
    ],
    'image_generation': [
        'runwayml/stable-diffusion-v1-5',
        'CompVis/stable-diffusion-v1-4',
        'stabilityai/stable-diffusion-2-1',
    ],
}

# Rate Limiting
AI_RATE_LIMITS = {
    'huggingface_free': 1000,  # requests per hour
    'requests_per_minute': 10,
}
```

### Step 3: Error Handling and Fallbacks

Implement robust error handling in your AI services:
```python
# In your AI service clients
class AIServiceError(Exception):
    pass

def with_retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise AIServiceError(f"Failed after {max_attempts} attempts: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return wrapper
        return decorator
```

## Testing and Debugging

### Step 1: Run Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps
```

### Step 2: Database Setup

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data.json
```

### Step 3: Test API Endpoints

```bash
# Health check
curl http://localhost/api/stories/health_check/

# Test story generation
curl -X POST http://localhost/api/stories/generate/ \
  -F "user_prompt=A magical adventure in an enchanted forest"
```

### Step 4: Frontend Testing

```bash
# Install dependencies
cd frontend
npm install

# Run tests
npm test

# Build for production
npm run build
```

### Step 5: Common Debugging Steps

1. **Database Connection Issues**:
   ```bash
   docker-compose exec backend python manage.py dbshell
   ```

2. **AI Service Issues**:
   ```bash
   # Check API keys
   docker-compose exec backend python manage.py shell
   >>> from apps.stories.ai_services.huggingface_client import HuggingFaceClient
   >>> client = HuggingFaceClient()
   >>> client.check_model_status('gpt2')
   ```

3. **File Upload Issues**:
   ```bash
   # Check media directory permissions
   docker-compose exec backend ls -la media/uploads/
   ```

## Production Deployment

### Step 1: Production Settings

Create `story_generator/settings/production.py`:
```python
from .base import *

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'OPTIONS': {
        'server_side_binding': True,
    },
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Static files
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/media'

# Logging
LOGGING['handlers']['file']['filename'] = '/app/logs/production.log'
LOGGING['root']['level'] = 'WARNING'
```

### Step 2: Production Docker Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      target: production
    environment:
      - DJANGO_SETTINGS_MODULE=story_generator.settings.production
      - DEBUG=False
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate &&
             gunicorn --bind 0.0.0.0:8000 --workers 4 story_generator.wsgi:application"
    
  frontend:
    build:
      target: production
    
  nginx:
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro

  postgres:
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

volumes:
  postgres_prod_data:
    driver: local
```

### Step 3: Deploy to Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

## API Documentation

### Core Endpoints

#### POST `/api/stories/generate/`
Generate a new story with images.

**Request:**
```bash
curl -X POST http://localhost/api/stories/generate/ \
  -F "user_prompt=A brave knight discovers a magical forest" \
  -F "audio_file=@recording.wav"
```

**Response:**
```json
{
  "success": true,
  "story": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_prompt": "A brave knight discovers a magical forest",
    "story_text": "Sir Galahad ventured into the enchanted woods...",
    "character_description": "A noble knight in shining armor...",
    "character_image": "/media/generated/images/characters/character_123.jpg",
    "background_image": "/media/generated/images/backgrounds/background_123.jpg",
    "composed_image": "/media/generated/compositions/composed_123.jpg",
    "processing_time": 45.2,
    "created_at": "2025-08-28T10:30:00Z"
  }
}
```

#### GET `/api/stories/`
List all stories.

#### GET `/api/stories/{id}/`
Get specific story details.

#### GET `/api/stories/{id}/generation_logs/`
Get generation logs for debugging.

#### GET `/api/stories/health_check/`
Health check endpoint.

## Troubleshooting

### Common Issues and Solutions

1. **AI Service Rate Limits**
   ```python
   # Add rate limiting
   from django.core.cache import cache
   
   def rate_limit_check(service_name, limit_per_hour=1000):
       key = f"rate_limit_{service_name}_{datetime.now().hour}"
       current = cache.get(key, 0)
       if current >= limit_per_hour:
           raise AIServiceError("Rate limit exceeded")
       cache.set(key, current + 1, 3600)
   ```

2. **Image Generation Failures**
   - Check model availability: `client.check_model_status(model)`
   - Implement fallback models
   - Add retry logic with exponential backoff

3. **Audio Processing Issues**
   - Verify ffmpeg installation: `docker-compose exec backend ffmpeg -version`
   - Check supported formats: WAV, MP3, OGG, M4A
   - Validate file size limits (10MB default)

4. **Database Connection Issues**
   ```bash
   # Check database connection
   docker-compose exec postgres pg_isready -U postgres -d story_generator
   
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres
   docker-compose exec backend python manage.py migrate
   ```

5. **Frontend Issues**
   ```bash
   # Clear node_modules and reinstall
   docker-compose exec frontend rm -rf node_modules
   docker-compose exec frontend npm install
   
   # Check API connectivity
   docker-compose exec frontend curl http://backend:8000/api/stories/health_check/
   ```

### Performance Optimization

1. **Enable Caching**
   ```python
   # Add to settings
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://redis:6379/1',
       }
   }
   ```

2. **Optimize Database Queries**
   ```python
   # Use select_related and prefetch_related
   stories = Story.objects.select_related('user').prefetch_related('logs')
   ```

3. **Async Processing**
   ```python
   # Add Celery for background tasks
   @shared_task
   def generate_story_async(story_id):
       # Process story generation
       pass
   ```

### Monitoring and Logging

1. **Add Health Checks**
   ```python
   # Custom health check
   def detailed_health_check():
       checks = {
           'database': check_database(),
           'redis': check_redis(),
           'ai_services': check_ai_services(),
           'file_storage': check_file_storage(),
       }
       return checks
   ```

2. **Implement Metrics**
   ```python
   # Add metrics collection
   import time
   from django.db import models
   
   class GenerationMetrics(models.Model):
       timestamp = models.DateTimeField(auto_now_add=True)
       service_used = models.CharField(max_length=100)
       processing_time = models.FloatField()
       success = models.BooleanField()
   ```

This comprehensive guide provides everything you need to build, deploy, and maintain your Django LangChain Story Generator application. The implementation uses only free and open-source AI services while providing a professional, scalable architecture.