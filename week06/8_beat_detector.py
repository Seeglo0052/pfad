"""
Beat Detection and Rhythm Visualization
Detects beats in real-time audio and creates visual rhythm patterns
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import threading
import queue
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import time
import colorsys

class BeatDetector:
    def __init__(self):
        # Audio parameters
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.BUFFER_SIZE = 4 * self.RATE  # 4 seconds
        
        # Beat detection parameters
        self.MIN_BPM = 60
        self.MAX_BPM = 180
        self.BEAT_THRESHOLD = 0.3
        self.ONSET_THRESHOLD = 0.1
        
        # Buffers
        self.audio_buffer = np.zeros(self.BUFFER_SIZE, dtype=np.float32)
        self.onset_buffer = np.zeros(200, dtype=np.float32)  # Store onset strength history
        self.beat_times = []  # Store beat timestamps
        self.tempo_history = []
        
        # Audio queue
        self.audio_queue = queue.Queue(maxsize=50)
        
        # Beat detection state
        self.last_beat_time = 0
        self.current_tempo = 120  # BPM
        self.beat_confidence = 0
        
        # Visualization state
        self.beat_circles = []
        self.color_phase = 0
        self.beat_flash = 0
        
        # Setup
        self.setup_audio()
        self.setup_visualization()
        
    def setup_audio(self):
        """Initialize audio input"""
        self.p = pyaudio.PyAudio()
        
        # Find input device
        input_device = None
        print("Available audio devices:")
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  {i}: {device_info['name']}")
                if input_device is None:
                    input_device = i
        
        if input_device is None:
            print("No input device found!")
            return
        
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=input_device,
                stream_callback=self.audio_callback
            )
            
            print(f"Using device: {self.p.get_device_info_by_index(input_device)['name']}")
            self.stream.start_stream()
            
        except Exception as e:
            print(f"Error setting up audio: {e}")
            self.stream = None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback function"""
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        try:
            self.audio_queue.put((audio_data, time.time()), block=False)
        except queue.Full:
            pass
        return (None, pyaudio.paContinue)
    
    def compute_onset_strength(self, audio_chunk):
        """Compute onset strength using spectral flux"""
        # Compute spectrogram
        window_size = 1024
        hop_size = 512
        
        if len(audio_chunk) < window_size:
            return 0
        
        # Compute short-time Fourier transform
        freqs, times, stft = signal.spectrogram(
            audio_chunk,
            fs=self.RATE,
            window='hann',
            nperseg=window_size,
            noverlap=window_size - hop_size
        )
        
        # Compute magnitude spectrum
        magnitude = np.abs(stft)
        
        # Compute spectral flux (difference between consecutive frames)
        if magnitude.shape[1] > 1:
            flux = np.sum(np.maximum(magnitude[:, 1:] - magnitude[:, :-1], 0), axis=0)
            return np.mean(flux) if len(flux) > 0 else 0
        
        return 0
    
    def detect_beats(self, onset_strength, current_time):
        """Detect beats from onset strength"""
        # Add to onset buffer
        self.onset_buffer = np.roll(self.onset_buffer, -1)
        self.onset_buffer[-1] = onset_strength
        
        # Adaptive threshold
        recent_mean = np.mean(self.onset_buffer[-20:])
        recent_std = np.std(self.onset_buffer[-20:])
        threshold = recent_mean + self.ONSET_THRESHOLD * recent_std
        
        # Check for beat
        is_beat = False
        if (onset_strength > threshold and 
            onset_strength > self.BEAT_THRESHOLD and
            current_time - self.last_beat_time > 60.0 / self.MAX_BPM):  # Minimum interval
            
            # Additional verification: check if this is a local maximum
            if len(self.onset_buffer) >= 5:
                local_window = self.onset_buffer[-5:]
                if onset_strength == np.max(local_window):
                    is_beat = True
                    self.last_beat_time = current_time
                    self.beat_times.append(current_time)
                    
                    # Keep only recent beats for tempo calculation
                    self.beat_times = [t for t in self.beat_times if current_time - t < 10]
                    
                    # Calculate tempo
                    self.update_tempo()
                    
                    # Visual feedback
                    self.beat_flash = 1.0
                    self.add_beat_circle()
        
        return is_beat
    
    def update_tempo(self):
        """Update current tempo based on recent beats"""
        if len(self.beat_times) < 2:
            return
        
        # Calculate intervals between beats
        intervals = np.diff(self.beat_times[-10:])  # Use last 10 beats
        
        if len(intervals) > 0:
            # Remove outliers
            median_interval = np.median(intervals)
            valid_intervals = intervals[np.abs(intervals - median_interval) < median_interval * 0.5]
            
            if len(valid_intervals) > 0:
                avg_interval = np.mean(valid_intervals)
                new_tempo = 60.0 / avg_interval
                
                # Smooth tempo changes
                if self.MIN_BPM <= new_tempo <= self.MAX_BPM:
                    self.current_tempo = 0.8 * self.current_tempo + 0.2 * new_tempo
                    self.tempo_history.append(self.current_tempo)
                    
                    # Keep tempo history manageable
                    if len(self.tempo_history) > 50:
                        self.tempo_history = self.tempo_history[-50:]
    
    def add_beat_circle(self):
        """Add a visual beat circle"""
        # Generate random position and color
        angle = np.random.uniform(0, 2 * np.pi)
        radius = np.random.uniform(0.3, 0.8)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        # Color based on tempo
        hue = (self.current_tempo - self.MIN_BPM) / (self.MAX_BPM - self.MIN_BPM)
        color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        
        # Add circle with fade properties
        circle_data = {
            'x': x,
            'y': y,
            'size': 0.05,
            'color': color,
            'age': 0,
            'max_age': 30  # Frames to live
        }
        
        self.beat_circles.append(circle_data)
    
    def setup_visualization(self):
        """Setup the visualization"""
        self.fig = plt.figure(figsize=(15, 10))
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 3, height_ratios=[2, 1])
        
        # Main rhythm visualization (large circular plot)
        self.ax_rhythm = self.fig.add_subplot(gs[0, :])
        self.ax_rhythm.set_xlim(-1, 1)
        self.ax_rhythm.set_ylim(-1, 1)
        self.ax_rhythm.set_aspect('equal')
        self.ax_rhythm.set_title('Rhythm Visualization', fontsize=16)
        self.ax_rhythm.axis('off')
        
        # Add tempo circle
        self.tempo_circle = Circle((0, 0), 0.9, fill=False, color='white', linewidth=2, alpha=0.3)
        self.ax_rhythm.add_patch(self.tempo_circle)
        
        # Onset strength plot
        self.ax_onset = self.fig.add_subplot(gs[1, 0])
        self.onset_line, = self.ax_onset.plot(range(len(self.onset_buffer)), self.onset_buffer, 'lime', linewidth=2)
        self.ax_onset.set_title('Onset Strength')
        self.ax_onset.set_ylabel('Strength')
        self.ax_onset.set_ylim(0, 1)
        self.ax_onset.grid(True, alpha=0.3)
        
        # Tempo history plot
        self.ax_tempo = self.fig.add_subplot(gs[1, 1])
        self.tempo_line, = self.ax_tempo.plot([], [], 'orange', linewidth=2)
        self.ax_tempo.set_title('Tempo History')
        self.ax_tempo.set_ylabel('BPM')
        self.ax_tempo.set_ylim(self.MIN_BPM - 10, self.MAX_BPM + 10)
        self.ax_tempo.grid(True, alpha=0.3)
        
        # Audio waveform
        self.ax_wave = self.fig.add_subplot(gs[1, 2])
        self.wave_line, = self.ax_wave.plot([], [], 'cyan', linewidth=1)
        self.ax_wave.set_title('Audio Waveform')
        self.ax_wave.set_ylabel('Amplitude')
        self.ax_wave.set_ylim(-1, 1)
        self.ax_wave.grid(True, alpha=0.3)
        
        # Status text
        self.status_text = self.fig.text(0.02, 0.95, '', fontsize=12, 
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
    
    def process_audio(self):
        """Main audio processing loop"""
        while True:
            if not self.audio_queue.empty():
                try:
                    audio_chunk, timestamp = self.audio_queue.get_nowait()
                    
                    # Update audio buffer
                    self.audio_buffer = np.roll(self.audio_buffer, -len(audio_chunk))
                    self.audio_buffer[-len(audio_chunk):] = audio_chunk
                    
                    # Compute onset strength
                    onset_strength = self.compute_onset_strength(audio_chunk)
                    
                    # Detect beats
                    self.detect_beats(onset_strength, timestamp)
                    
                except queue.Empty:
                    pass
            else:
                time.sleep(0.001)
    
    def update_visualization(self, frame):
        """Update the visualization"""
        # Update beat circles
        self.ax_rhythm.clear()
        self.ax_rhythm.set_xlim(-1, 1)
        self.ax_rhythm.set_ylim(-1, 1)
        self.ax_rhythm.set_aspect('equal')
        self.ax_rhythm.axis('off')
        
        # Background circle
        bg_color = 'red' if self.beat_flash > 0.5 else 'white'
        self.tempo_circle = Circle((0, 0), 0.9, fill=False, color=bg_color, linewidth=2, alpha=0.3)
        self.ax_rhythm.add_patch(self.tempo_circle)
        
        # Draw beat circles
        for circle in self.beat_circles[:]:
            alpha = 1.0 - (circle['age'] / circle['max_age'])
            size = circle['size'] * (1 + circle['age'] * 0.02)  # Grow slightly
            
            beat_circle = Circle(
                (circle['x'], circle['y']), 
                size, 
                color=circle['color'], 
                alpha=alpha
            )
            self.ax_rhythm.add_patch(beat_circle)
            
            circle['age'] += 1
            
            # Remove old circles
            if circle['age'] >= circle['max_age']:
                self.beat_circles.remove(circle)
        
        # Fade beat flash
        self.beat_flash *= 0.9
        
        # Add tempo indicator
        if len(self.beat_times) > 1:
            # Draw tempo as rotating line
            angle = (time.time() * self.current_tempo / 60 * 2 * np.pi) % (2 * np.pi)
            x_end = 0.7 * np.cos(angle - np.pi/2)
            y_end = 0.7 * np.sin(angle - np.pi/2)
            self.ax_rhythm.plot([0, x_end], [0, y_end], 'yellow', linewidth=3, alpha=0.8)
        
        # Update onset strength plot
        self.onset_line.set_ydata(self.onset_buffer)
        
        # Update tempo history
        if len(self.tempo_history) > 0:
            self.tempo_line.set_data(range(len(self.tempo_history)), self.tempo_history)
            self.ax_tempo.set_xlim(0, max(50, len(self.tempo_history)))
        
        # Update waveform (show recent portion)
        recent_samples = min(2048, len(self.audio_buffer))
        recent_audio = self.audio_buffer[-recent_samples:]
        self.wave_line.set_data(range(len(recent_audio)), recent_audio)
        self.ax_wave.set_xlim(0, len(recent_audio))
        
        # Update status text
        current_time = time.time()
        time_since_beat = current_time - self.last_beat_time if self.last_beat_time > 0 else 0
        
        status = f"Beat Detection Status\n"
        status += f"Current Tempo: {self.current_tempo:.1f} BPM\n"
        status += f"Time Since Last Beat: {time_since_beat:.2f}s\n"
        status += f"Total Beats Detected: {len(self.beat_times)}\n"
        status += f"Onset Strength: {self.onset_buffer[-1]:.3f}\n"
        status += f"Active Circles: {len(self.beat_circles)}"
        
        self.status_text.set_text(status)
        
        # Color-changing title based on tempo
        hue = (frame * 0.01) % 1.0
        title_color = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        self.ax_rhythm.set_title('?? Rhythm Visualization ??', fontsize=16, color=title_color)
        
        return []
    
    def run(self):
        """Start the beat detector"""
        print("Starting Beat Detection and Rhythm Visualization...")
        print("Play some music with a clear beat!")
        print("The visualization will show:")
        print("  - Beat circles that appear on each detected beat")
        print("  - Tempo indicator (yellow line rotating at current BPM)")
        print("  - Real-time onset strength, tempo history, and waveform")
        print("Close the window to stop.")
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=self.process_audio, daemon=True)
        audio_thread.start()
        
        try:
            # Start visualization
            ani = animation.FuncAnimation(
                self.fig,
                self.update_visualization,
                interval=33,  # ~30 FPS
                blit=False,
                cache_frame_data=False
            )
            
            plt.show()
            
        except KeyboardInterrupt:
            print("Stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        plt.close('all')

if __name__ == "__main__":
    try:
        detector = BeatDetector()
        detector.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()