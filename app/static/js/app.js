// Public Speaking Coach - Client-side JavaScript

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Simple waveform visualization (placeholder for future enhancement)
function drawSimpleWaveform(canvas, audioData) {
    if (!canvas || !audioData) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Set styles
    ctx.strokeStyle = '#405DE6';
    ctx.lineWidth = 2;
    
    // Draw waveform
    ctx.beginPath();
    const sliceWidth = width / audioData.length;
    let x = 0;
    
    for (let i = 0; i < audioData.length; i++) {
        const v = audioData[i] * height / 2;
        const y = height / 2 + v;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        x += sliceWidth;
    }
    
    ctx.stroke();
}

// Auto-save functionality for notes
let saveTimeout;
function autoSaveNote(videoId, promptId, content) {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        if (content && content.trim() !== '') {
            saveNote(videoId, promptId, content);
        }
    }, 1000); // Save after 1 second of inactivity
}

async function saveNote(videoId, promptId, content) {
    try {
        const formData = new FormData();
        formData.append('video_id', videoId);
        formData.append('prompt_id', promptId);
        formData.append('content', content);
        
        const response = await fetch('/save_note', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showNotification('Note saved!', 'success');
        } else {
            showNotification('Error saving note', 'error');
        }
    } catch (error) {
        console.error('Error saving note:', error);
        showNotification('Error saving note', 'error');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg text-white z-50 transition-all duration-300`;
    
    // Set color based on type
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500');
            break;
        case 'error':
            notification.classList.add('bg-red-500');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500');
            break;
        default:
            notification.classList.add('bg-blue-500');
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize any video elements
    const videos = document.querySelectorAll('video');
    videos.forEach(video => {
        // Add video ID data attribute if missing
        if (!video.dataset.videoId && video.id === 'mainVideo') {
            const videoId = new URLSearchParams(window.location.search).get('videoId') ||
                          video.src.split('/').pop().split('.')[0];
            video.dataset.videoId = videoId;
        }

        // Track video events
        video.addEventListener('loadedmetadata', function() {
            console.log('Video loaded:', this.duration, 'seconds');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'video_ready', {
                    'video_id': this.dataset.videoId,
                    'duration': this.duration
                });
            }
        });
        
        video.addEventListener('play', function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'video_play', {
                    'video_id': this.dataset.videoId,
                    'duration': this.duration
                });
            }
        });

        // Track progress at 25%, 50%, 75%, 100%
        const progressPoints = [0.25, 0.5, 0.75, 1];
        const trackedPoints = new Set();
        
        video.addEventListener('timeupdate', function() {
            const progress = this.currentTime / this.duration;
            progressPoints.forEach(point => {
                if (progress >= point && !trackedPoints.has(point)) {
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'video_progress', {
                            'video_id': this.dataset.videoId,
                            'progress': `${point * 100}%`,
                            'current_time': this.currentTime
                        });
                    }
                    trackedPoints.add(point);
                }
            });
        });

        video.addEventListener('ended', function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'video_complete', {
                    'video_id': this.dataset.videoId
                });
            }
        });
        
        video.addEventListener('error', function() {
            showNotification('Error loading video', 'error');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'video_error', {
                    'video_id': this.dataset.videoId
                });
            }
        });
    });
    
    // Initialize any audio elements
    const audios = document.querySelectorAll('audio');
    audios.forEach(audio => {
        audio.addEventListener('loadedmetadata', function() {
            console.log('Audio loaded:', this.duration, 'seconds');
        });
        
        audio.addEventListener('error', function() {
            showNotification('Error loading audio', 'error');
        });
    });
});

// Export functions for global use
window.formatFileSize = formatFileSize;
window.formatDuration = formatDuration;
window.showNotification = showNotification;
window.autoSaveNote = autoSaveNote;
window.saveNote = saveNote;