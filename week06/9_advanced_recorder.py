"""
Advanced Audio Recorder
Records audio with real-time visualization and multiple format support
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import wave
import threading
import queue
import time
import os
from datetime import datetime
from scipy.io.wavfile import write as wav_write
import json

class AdvancedAudioRecorder:
    def __init__(self):
        # Audio parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2  # Stereo recording
        self.RATE = 44100
        self.CHUNK = 1024
        self.RECORD_SECONDS = None  # Unlimited until stopped
        
        # Recording state
        self.is_recording = False
        self.is_paused = False
        self.recorded_frames = []
        self.current_recording = []
        self.recording_start_time = None
        self.total_recorded_time = 0
        
        # Visualization buffers
        self.BUFFER_SIZE = 4 * self.RATE  # 4 seconds for visualization
        self.left_buffer = np.zeros(self.BUFFER_SIZE, dtype=np.int16)
        self.right_buffer = np.zeros(self.BUFFER_SIZE, dtype=np.int16)
        
        # Audio processing
        self.audio_queue = queue.Queue(maxsize=100)
        
        # Recording metadata
        self.recording_sessions = []
        self.current_session = None
        
        # Output settings
        self.output_dir = "recordings"
        self.create_output_directory()
        
        # Setup
        self.setup_audio()
        self.setup_visualization()
        
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
    
    def setup_audio(self):
        """Initialize audio input"""
        self.p = pyaudio.PyAudio()
        
        # Find suitable input device
        input_device = None
        print("Available audio devices:")
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            print(f"  {i}: {device_info['name']} (In: {device_info['maxInputChannels']}, Out: {device_info['maxOutputChannels']})")
            
            if device_info['maxInputChannels'] >= 2 and input_device is None:
                input_device = i
        
        # Fallback to mono if no stereo device found
        if input_device is None:
            for i in range(self.p.get_device_count()):
                device_info = self.p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] >= 1:
                    input_device = i
                    self.CHANNELS = 1
                    print("Falling back to mono recording")
                    break
        
        if input_device is None:
            print("No suitable input device found!")
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
            
            device_info = self.p.get_device_info_by_index(input_device)
            print(f"Using device: {device_info['name']}")
            print(f"Recording format: {self.CHANNELS} channel(s), {self.RATE} Hz, 16-bit")
            
            self.stream.start_stream()
            
        except Exception as e:
            print(f"Error setting up audio: {e}")
            self.stream = None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio input callback"""
        try:
            self.audio_queue.put((in_data, time.time()), block=False)
        except queue.Full:
            # Remove oldest item if queue is full
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put((in_data, time.time()), block=False)
            except queue.Empty:
                pass
        return (None, pyaudio.paContinue)
    
    def setup_visualization(self):
        """Setup the visualization interface"""
        self.fig = plt.figure(figsize=(16, 10))
        
        # Create layout
        gs = self.fig.add_gridspec(4, 2, height_ratios=[2, 1, 1, 0.5])
        
        # Stereo waveform displays
        if self.CHANNELS == 2:
            self.ax_left = self.fig.add_subplot(gs[0, 0])
            self.ax_right = self.fig.add_subplot(gs[0, 1])
            
            self.ax_left.set_title('Left Channel')
            self.ax_right.set_title('Right Channel')
            
            self.line_left, = self.ax_left.plot([], [], 'cyan', linewidth=0.8)
            self.line_right, = self.ax_right.plot([], [], 'magenta', linewidth=0.8)
            
            for ax in [self.ax_left, self.ax_right]:
                ax.set_ylim(-32768, 32767)
                ax.set_ylabel('Amplitude')
                ax.grid(True, alpha=0.3)
        else:
            # Mono display
            self.ax_mono = self.fig.add_subplot(gs[0, :])
            self.ax_mono.set_title('Audio Input (Mono)')
            self.line_mono, = self.ax_mono.plot([], [], 'cyan', linewidth=0.8)
            self.ax_mono.set_ylim(-32768, 32767)
            self.ax_mono.set_ylabel('Amplitude')
            self.ax_mono.grid(True, alpha=0.3)
        
        # Level meters
        self.ax_levels = self.fig.add_subplot(gs[1, :])
        self.ax_levels.set_title('Audio Levels')
        self.ax_levels.set_xlim(0, 10)
        self.ax_levels.set_ylim(-60, 0)
        self.ax_levels.set_ylabel('dB')
        self.ax_levels.grid(True, alpha=0.3)
        
        # Recording timeline
        self.ax_timeline = self.fig.add_subplot(gs[2, :])
        self.ax_timeline.set_title('Recording Timeline')
        self.ax_timeline.set_ylabel('Session')
        self.ax_timeline.grid(True, alpha=0.3)
        
        # Control buttons area
        self.ax_controls = self.fig.add_subplot(gs[3, :])
        self.ax_controls.axis('off')
        
        # Create buttons
        self.create_control_buttons()
        
        # Status text
        self.status_text = self.fig.text(0.02, 0.02, '', fontsize=10,
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_width = 0.08
        button_height = 0.04
        button_y = 0.05
        
        # Record button
        self.ax_record = plt.axes([0.1, button_y, button_width, button_height])
        self.btn_record = Button(self.ax_record, 'Record')
        self.btn_record.on_clicked(self.toggle_recording)
        
        # Pause button
        self.ax_pause = plt.axes([0.2, button_y, button_width, button_height])
        self.btn_pause = Button(self.ax_pause, 'Pause')
        self.btn_pause.on_clicked(self.toggle_pause)
        
        # Stop button
        self.ax_stop = plt.axes([0.3, button_y, button_width, button_height])
        self.btn_stop = Button(self.ax_stop, 'Stop')
        self.btn_stop.on_clicked(self.stop_recording)
        
        # Save button
        self.ax_save = plt.axes([0.4, button_y, button_width, button_height])
        self.btn_save = Button(self.ax_save, 'Save WAV')
        self.btn_save.on_clicked(self.save_recording)
        
        # Play button (for last recording)
        self.ax_play = plt.axes([0.5, button_y, button_width, button_height])
        self.btn_play = Button(self.ax_play, 'Play Last')
        self.btn_play.on_clicked(self.play_last_recording)
        
        # Clear button
        self.ax_clear = plt.axes([0.6, button_y, button_width, button_height])
        self.btn_clear = Button(self.ax_clear, 'Clear All')
        self.btn_clear.on_clicked(self.clear_recordings)
    
    def toggle_recording(self, event):
        """Toggle recording state"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording(event)
    
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.is_paused = False
        self.recording_start_time = time.time()
        self.current_recording = []
        
        # Create new session
        self.current_session = {
            'start_time': self.recording_start_time,
            'duration': 0,
            'frames': [],
            'peak_level': 0,
            'filename': None
        }
        
        print("Recording started...")
        self.btn_record.label.set_text('Recording...')
        self.btn_record.color = 'red'
    
    def toggle_pause(self, event):
        """Toggle pause state"""
        if self.is_recording:
            self.is_paused = not self.is_paused
            if self.is_paused:
                print("Recording paused")
                self.btn_pause.label.set_text('Resume')
                self.btn_pause.color = 'orange'
            else:
                print("Recording resumed")
                self.btn_pause.label.set_text('Pause')
                self.btn_pause.color = 'lightblue'
    
    def stop_recording(self, event):
        """Stop recording"""  
        if self.is_recording:
            self.is_recording = False
            self.is_paused = False
            
            # Finalize current session
            if self.current_session:
                self.current_session['duration'] = time.time() - self.current_session['start_time']
                self.current_session['frames'] = self.current_recording.copy()
                self.recording_sessions.append(self.current_session)
            
            print(f"Recording stopped. Duration: {self.current_session['duration']:.2f} seconds")
            
            # Reset button states
            self.btn_record.label.set_text('Record')
            self.btn_record.color = 'lightblue'
            self.btn_pause.label.set_text('Pause')
            self.btn_pause.color = 'lightblue'
    
    def save_recording(self, event):
        """Save the last recording to WAV file"""
        if not self.recording_sessions:
            print("No recordings to save!")
            return
        
        last_session = self.recording_sessions[-1]
        if not last_session['frames']:
            print("No audio data to save!")
            return
        
        # Generate filename
        timestamp = datetime.fromtimestamp(last_session['start_time'])
        filename = f"recording_{timestamp.strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Convert frames to numpy array
            audio_data = np.concatenate(last_session['frames'])
            
            # Save as WAV file
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data.tobytes())
            
            last_session['filename'] = filename
            print(f"Recording saved as: {filepath}")
            
            # Save session metadata
            metadata_file = os.path.join(self.output_dir, "recording_metadata.json")
            metadata = {
                'sessions': [
                    {
                        'filename': s.get('filename'),
                        'start_time': s['start_time'],
                        'duration': s['duration'],
                        'peak_level': s['peak_level'],
                        'channels': self.CHANNELS,
                        'sample_rate': self.RATE
                    } for s in self.recording_sessions if s.get('filename')
                ]
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            print(f"Error saving recording: {e}")
    
    def play_last_recording(self, event):
        """Play the last recording (basic implementation)"""
        if not self.recording_sessions:
            print("No recordings to play!")
            return
        
        last_session = self.recording_sessions[-1]
        if not last_session['frames']:
            print("No audio data to play!")
            return
        
        print("Playing last recording...")
        
        try:
            # Create playback stream
            playback_stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True
            )
            
            # Play audio data
            for frame in last_session['frames']:
                if hasattr(frame, 'tobytes'):
                    playback_stream.write(frame.tobytes())
                else:
                    playback_stream.write(frame)
            
            playback_stream.stop_stream()
            playback_stream.close()
            print("Playback finished")
            
        except Exception as e:
            print(f"Error during playback: {e}")
    
    def clear_recordings(self, event):
        """Clear all recordings"""
        self.recording_sessions = []
        self.current_recording = []
        print("All recordings cleared")
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'r':
            self.toggle_recording(None)
        elif event.key == 'p':
            self.toggle_pause(None)
        elif event.key == 's':
            self.stop_recording(None)
        elif event.key == 'w':
            self.save_recording(None)
        elif event.key == 'space':
            self.play_last_recording(None)
        elif event.key == 'c':
            self.clear_recordings(None)
    
    def process_audio(self):
        """Main audio processing loop"""
        while True:
            if not self.audio_queue.empty():
                try:
                    audio_data, timestamp = self.audio_queue.get_nowait()
                    
                    # Convert to numpy array
                    if self.CHANNELS == 2:
                        # Stereo: interleaved data
                        samples = np.frombuffer(audio_data, dtype=np.int16)
                        left_samples = samples[0::2]
                        right_samples = samples[1::2]
                        
                        # Update visualization buffers
                        self.left_buffer = np.roll(self.left_buffer, -len(left_samples))
                        self.left_buffer[-len(left_samples):] = left_samples
                        
                        self.right_buffer = np.roll(self.right_buffer, -len(right_samples))
                        self.right_buffer[-len(right_samples):] = right_samples
                    else:
                        # Mono
                        samples = np.frombuffer(audio_data, dtype=np.int16)
                        self.left_buffer = np.roll(self.left_buffer, -len(samples))
                        self.left_buffer[-len(samples):] = samples
                    
                    # Record if active and not paused
                    if self.is_recording and not self.is_paused:
                        self.current_recording.append(np.frombuffer(audio_data, dtype=np.int16))
                        
                        # Update peak level
                        if self.current_session:
                            current_peak = np.max(np.abs(samples))
                            self.current_session['peak_level'] = max(
                                self.current_session['peak_level'], 
                                current_peak
                            )
                    
                except queue.Empty:
                    pass
            else:
                time.sleep(0.001)
    
    def update_visualization(self, frame):
        """Update the visualization"""
        current_time = time.time()
        
        # Update waveforms
        if self.CHANNELS == 2:
            # Update stereo waveforms
            time_axis = np.linspace(0, len(self.left_buffer) / self.RATE, len(self.left_buffer))
            self.line_left.set_data(time_axis, self.left_buffer)
            self.line_right.set_data(time_axis, self.right_buffer)
            
            for ax in [self.ax_left, self.ax_right]:
                ax.set_xlim(0, len(self.left_buffer) / self.RATE)
            
            # Calculate levels
            left_level = 20 * np.log10(max(np.sqrt(np.mean(self.left_buffer.astype(np.float32)**2)), 1)) - 90
            right_level = 20 * np.log10(max(np.sqrt(np.mean(self.right_buffer.astype(np.float32)**2)), 1)) - 90
            
        else:
            # Update mono waveform
            time_axis = np.linspace(0, len(self.left_buffer) / self.RATE, len(self.left_buffer))
            self.line_mono.set_data(time_axis, self.left_buffer)
            self.ax_mono.set_xlim(0, len(self.left_buffer) / self.RATE)
            
            # Calculate level
            left_level = 20 * np.log10(max(np.sqrt(np.mean(self.left_buffer.astype(np.float32)**2)), 1)) - 90
            right_level = left_level
        
        # Update level meters
        self.ax_levels.clear()
        self.ax_levels.set_xlim(0, 10)
        self.ax_levels.set_ylim(-60, 0)
        self.ax_levels.set_ylabel('dB')
        self.ax_levels.set_title('Audio Levels')
        self.ax_levels.grid(True, alpha=0.3)
        
        # Draw level bars
        left_color = 'red' if left_level > -6 else 'orange' if left_level > -20 else 'green'
        right_color = 'red' if right_level > -6 else 'orange' if right_level > -20 else 'green'
        
        self.ax_levels.bar([2], [max(left_level, -60)], width=1.5, bottom=-60, 
                          color=left_color, alpha=0.7, label='Left')
        if self.CHANNELS == 2:
            self.ax_levels.bar([6], [max(right_level, -60)], width=1.5, bottom=-60, 
                              color=right_color, alpha=0.7, label='Right')
        
        self.ax_levels.axhline(y=-6, color='red', linestyle='--', alpha=0.5, label='Peak')
        self.ax_levels.axhline(y=-20, color='orange', linestyle='--', alpha=0.5, label='High')
        self.ax_levels.legend()
        
        # Update timeline
        self.ax_timeline.clear()
        self.ax_timeline.set_title('Recording Timeline')
        self.ax_timeline.set_ylabel('Session')
        
        if self.recording_sessions:
            for i, session in enumerate(self.recording_sessions):
                start_time = session['start_time']
                duration = session['duration']
                
                self.ax_timeline.barh(i, duration, left=0, height=0.8,
                                    color='blue', alpha=0.6)
                self.ax_timeline.text(duration/2, i, f"{duration:.1f}s", 
                                    ha='center', va='center', fontsize=8)
        
        # Show current recording
        if self.is_recording and self.current_session:
            current_duration = current_time - self.current_session['start_time']
            session_idx = len(self.recording_sessions)
            
            color = 'red' if not self.is_paused else 'orange'
            self.ax_timeline.barh(session_idx, current_duration, left=0, height=0.8,
                                color=color, alpha=0.8)
            self.ax_timeline.text(current_duration/2, session_idx, 
                                f"{'PAUSED' if self.is_paused else 'REC'} {current_duration:.1f}s", 
                                ha='center', va='center', fontsize=8, color='white')
        
        if self.recording_sessions or self.is_recording:
            max_duration = max([s['duration'] for s in self.recording_sessions] + 
                             [current_time - self.current_session['start_time'] if self.is_recording else 0])
            self.ax_timeline.set_xlim(0, max_duration * 1.1)
            self.ax_timeline.set_ylim(-0.5, len(self.recording_sessions) + 0.5 + (1 if self.is_recording else 0))
        
        self.ax_timeline.grid(True, alpha=0.3)
        
        # Update status
        status = f"Advanced Audio Recorder Status\n"
        status += f"Device: {self.CHANNELS} channel(s), {self.RATE} Hz\n"
        status += f"Recording: {'YES' if self.is_recording else 'NO'}"
        if self.is_recording:
            status += f" ({'PAUSED' if self.is_paused else 'ACTIVE'})"
        status += f"\nSessions: {len(self.recording_sessions)}\n"
        
        if self.is_recording and self.current_session:
            current_duration = current_time - self.current_session['start_time']
            status += f"Current: {current_duration:.1f}s\n"
        
        total_duration = sum(s['duration'] for s in self.recording_sessions)
        status += f"Total Recorded: {total_duration:.1f}s\n"
        status += f"Audio Level: L={left_level:.1f}dB"
        if self.CHANNELS == 2:
            status += f", R={right_level:.1f}dB"
        
        status += f"\n\nControls: R=Record, P=Pause, S=Stop, W=Save, Space=Play, C=Clear"
        
        self.status_text.set_text(status)
        
        return []
    
    def run(self):
        """Start the audio recorder"""
        print("Starting Advanced Audio Recorder...")
        print("Controls:")
        print("  R: Start/Stop Recording")
        print("  P: Pause/Resume")
        print("  S: Stop Recording")
        print("  W: Save as WAV")
        print("  Space: Play Last Recording")
        print("  C: Clear All Recordings")
        print(f"\nRecordings will be saved to: {os.path.abspath(self.output_dir)}")
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=self.process_audio, daemon=True)
        audio_thread.start()
        
        try:
            # Start visualization
            ani = animation.FuncAnimation(
                self.fig,
                self.update_visualization,
                interval=50,  # 20 FPS
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
        recorder = AdvancedAudioRecorder()
        recorder.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()