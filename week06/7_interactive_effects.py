"""
Interactive Audio Effects Processor
Real-time audio effects with keyboard controls and visual feedback
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider
import threading
import queue
from scipy import signal
import time

class AudioEffectsProcessor:
    def __init__(self):
        # Audio parameters
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1  
        self.RATE = 44100
        self.CHUNK = 512
        self.ROLLING_WINDOW = 2 * self.RATE
        
        # Effect parameters
        self.reverb_enabled = False
        self.echo_enabled = False
        self.filter_enabled = False
        self.distortion_enabled = False
        
        # Effect settings
        self.reverb_decay = 0.5
        self.echo_delay = 0.3
        self.echo_feedback = 0.4
        self.filter_cutoff = 1000
        self.filter_type = 'low'  # 'low', 'high', 'band'
        self.distortion_gain = 2.0
        
        # Buffers
        self.input_buffer = np.zeros(self.ROLLING_WINDOW, dtype=np.float32)
        self.output_buffer = np.zeros(self.ROLLING_WINDOW, dtype=np.float32)
        self.echo_buffer = np.zeros(int(self.RATE * 2), dtype=np.float32)  # 2 second delay line
        self.reverb_buffer = np.zeros(int(self.RATE * 3), dtype=np.float32)  # 3 second reverb
        
        # Queues for thread communication
        self.input_queue = queue.Queue(maxsize=50)
        self.output_queue = queue.Queue(maxsize=50)
        
        # Setup audio
        self.setup_audio()
        
        # Setup visualization
        self.setup_visualization()
        
    def setup_audio(self):
        """Initialize audio input and output streams"""
        self.p = pyaudio.PyAudio()
        
        # Find devices
        input_device = None
        output_device = None
        
        print("Available audio devices:")
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            print(f"  {i}: {device_info['name']} (In: {device_info['maxInputChannels']}, Out: {device_info['maxOutputChannels']})")
            
            if device_info['maxInputChannels'] > 0 and input_device is None:
                input_device = i
            if device_info['maxOutputChannels'] > 0 and output_device is None:
                output_device = i
        
        if input_device is None or output_device is None:
            print("Required audio devices not found!")
            return
        
        try:
            # Input stream
            self.input_stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=input_device,
                stream_callback=self.input_callback
            )
            
            # Output stream  
            self.output_stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK,
                output_device_index=output_device,
                stream_callback=self.output_callback
            )
            
            print(f"Input device: {self.p.get_device_info_by_index(input_device)['name']}")
            print(f"Output device: {self.p.get_device_info_by_index(output_device)['name']}")
            
            self.input_stream.start_stream()
            self.output_stream.start_stream()
            
        except Exception as e:
            print(f"Error setting up audio streams: {e}")
            
    def input_callback(self, in_data, frame_count, time_info, status):
        """Audio input callback"""
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        try:
            self.input_queue.put(audio_data, block=False)
        except queue.Full:
            pass
        return (None, pyaudio.paContinue)
    
    def output_callback(self, in_data, frame_count, time_info, status):
        """Audio output callback"""
        try:
            data = self.output_queue.get_nowait()
            return (data.astype(np.float32).tobytes(), pyaudio.paContinue)
        except queue.Empty:
            # Return silence if no data
            return (np.zeros(frame_count, dtype=np.float32).tobytes(), pyaudio.paContinue)
    
    def apply_reverb(self, audio_chunk):
        """Apply reverb effect"""
        if not self.reverb_enabled:
            return audio_chunk
        
        # Simple reverb using delay and feedback
        delay_samples = int(0.05 * self.RATE)  # 50ms delay
        output = audio_chunk.copy()
        
        for i, sample in enumerate(audio_chunk):
            # Add delayed signal
            if i >= delay_samples:
                output[i] += self.reverb_decay * output[i - delay_samples]
        
        return output * 0.7  # Reduce volume to prevent clipping
    
    def apply_echo(self, audio_chunk):
        """Apply echo effect"""
        if not self.echo_enabled:
            return audio_chunk
        
        delay_samples = int(self.echo_delay * self.RATE)
        output = audio_chunk.copy()
        
        # Add echo from delay buffer
        for i in range(len(audio_chunk)):
            if i < len(self.echo_buffer) - delay_samples:
                output[i] += self.echo_feedback * self.echo_buffer[i + delay_samples]
        
        # Update echo buffer
        self.echo_buffer = np.roll(self.echo_buffer, -len(audio_chunk))
        self.echo_buffer[-len(audio_chunk):] = output
        
        return output
    
    def apply_filter(self, audio_chunk):
        """Apply frequency filter"""
        if not self.filter_enabled:
            return audio_chunk
        
        # Design filter
        nyquist = self.RATE / 2
        normalized_cutoff = self.filter_cutoff / nyquist
        
        try:
            if self.filter_type == 'low':
                b, a = signal.butter(4, normalized_cutoff, btype='low')
            elif self.filter_type == 'high':
                b, a = signal.butter(4, normalized_cutoff, btype='high')
            else:  # band
                low_freq = max(normalized_cutoff - 0.1, 0.01)
                high_freq = min(normalized_cutoff + 0.1, 0.99)
                b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio_chunk)
            return filtered.astype(np.float32)
            
        except Exception as e:
            print(f"Filter error: {e}")
            return audio_chunk
    
    def apply_distortion(self, audio_chunk):
        """Apply distortion effect"""
        if not self.distortion_enabled:
            return audio_chunk
        
        # Soft clipping distortion
        amplified = audio_chunk * self.distortion_gain
        distorted = np.tanh(amplified)  # Soft clipping
        return distorted * 0.5  # Reduce volume
    
    def process_audio(self):
        """Main audio processing loop"""
        while True:
            if not self.input_queue.empty():
                try:
                    # Get input audio
                    audio_chunk = self.input_queue.get_nowait()
                    
                    # Update input buffer for visualization
                    self.input_buffer = np.roll(self.input_buffer, -len(audio_chunk))
                    self.input_buffer[-len(audio_chunk):] = audio_chunk
                    
                    # Apply effects in order
                    processed = audio_chunk.copy()
                    processed = self.apply_filter(processed)
                    processed = self.apply_distortion(processed) 
                    processed = self.apply_reverb(processed)
                    processed = self.apply_echo(processed)
                    
                    # Update output buffer for visualization
                    self.output_buffer = np.roll(self.output_buffer, -len(processed))
                    self.output_buffer[-len(processed):] = processed
                    
                    # Send to output
                    try:
                        self.output_queue.put(processed, block=False)
                    except queue.Full:
                        pass
                        
                except queue.Empty:
                    pass
            else:
                time.sleep(0.001)  # Small delay to prevent busy waiting
    
    def setup_visualization(self):
        """Setup the visualization window"""
        self.fig = plt.figure(figsize=(15, 10))
        
        # Create subplots
        gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 1, 1])
        
        # Waveform plots
        self.ax_input = self.fig.add_subplot(gs[0, :])
        self.ax_output = self.fig.add_subplot(gs[1, :])
        
        # Spectrum plots
        self.ax_input_spec = self.fig.add_subplot(gs[2, 0])
        self.ax_output_spec = self.fig.add_subplot(gs[2, 1])
        
        # Initialize plots
        self.time_axis = np.linspace(0, len(self.input_buffer) / self.RATE, len(self.input_buffer))
        
        self.line_input, = self.ax_input.plot(self.time_axis, self.input_buffer, 'cyan', linewidth=0.8)
        self.line_output, = self.ax_output.plot(self.time_axis, self.output_buffer, 'orange', linewidth=0.8)
        
        # Setup axes
        self.ax_input.set_title('Input Audio')
        self.ax_input.set_ylabel('Amplitude')
        self.ax_input.set_ylim(-1, 1)
        self.ax_input.grid(True, alpha=0.3)
        
        self.ax_output.set_title('Processed Audio')
        self.ax_output.set_ylabel('Amplitude')
        self.ax_output.set_xlabel('Time (s)')
        self.ax_output.set_ylim(-1, 1)
        self.ax_output.grid(True, alpha=0.3)
        
        # Spectrum plots setup
        self.ax_input_spec.set_title('Input Spectrum')
        self.ax_input_spec.set_xlabel('Frequency (Hz)')
        self.ax_input_spec.set_ylabel('Magnitude (dB)')
        self.ax_input_spec.set_xlim(0, 5000)
        self.ax_input_spec.set_ylim(-80, 0)
        self.ax_input_spec.grid(True, alpha=0.3)
        
        self.ax_output_spec.set_title('Output Spectrum')
        self.ax_output_spec.set_xlabel('Frequency (Hz)')
        self.ax_output_spec.set_ylabel('Magnitude (dB)')
        self.ax_output_spec.set_xlim(0, 5000)
        self.ax_output_spec.set_ylim(-80, 0)
        self.ax_output_spec.grid(True, alpha=0.3)
        
        # Add text for effects status
        self.status_text = self.fig.text(0.02, 0.02, self.get_status_text(), fontsize=10, 
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
    
    def get_status_text(self):
        """Get current effects status text"""
        status = "Effects Status:\n"
        status += f"[R] Reverb: {'ON' if self.reverb_enabled else 'OFF'} (decay: {self.reverb_decay:.2f})\n"
        status += f"[E] Echo: {'ON' if self.echo_enabled else 'OFF'} (delay: {self.echo_delay:.2f}s, feedback: {self.echo_feedback:.2f})\n"
        status += f"[F] Filter: {'ON' if self.filter_enabled else 'OFF'} ({self.filter_type}, {self.filter_cutoff}Hz)\n"
        status += f"[D] Distortion: {'ON' if self.distortion_enabled else 'OFF'} (gain: {self.distortion_gain:.1f})\n"
        status += "\nControls:\n"
        status += "R/E/F/D: Toggle effects | 1-9: Adjust parameters | Q: Quit"
        return status
    
    def on_key_press(self, event):
        """Handle keyboard input for effect control"""
        if event.key == 'r':
            self.reverb_enabled = not self.reverb_enabled
            print(f"Reverb: {'ON' if self.reverb_enabled else 'OFF'}")
        elif event.key == 'e':
            self.echo_enabled = not self.echo_enabled
            print(f"Echo: {'ON' if self.echo_enabled else 'OFF'}")
        elif event.key == 'f':
            self.filter_enabled = not self.filter_enabled
            print(f"Filter: {'ON' if self.filter_enabled else 'OFF'}")
        elif event.key == 'd':
            self.distortion_enabled = not self.distortion_enabled
            print(f"Distortion: {'ON' if self.distortion_enabled else 'OFF'}")
        elif event.key == '1':
            self.reverb_decay = max(0.1, self.reverb_decay - 0.1)
            print(f"Reverb decay: {self.reverb_decay:.2f}")
        elif event.key == '2':
            self.reverb_decay = min(0.9, self.reverb_decay + 0.1)
            print(f"Reverb decay: {self.reverb_decay:.2f}")
        elif event.key == '3':
            self.echo_delay = max(0.1, self.echo_delay - 0.1)
            print(f"Echo delay: {self.echo_delay:.2f}s")
        elif event.key == '4':
            self.echo_delay = min(1.0, self.echo_delay + 0.1)
            print(f"Echo delay: {self.echo_delay:.2f}s")
        elif event.key == '5':
            self.filter_cutoff = max(100, self.filter_cutoff - 200)
            print(f"Filter cutoff: {self.filter_cutoff}Hz")
        elif event.key == '6':
            self.filter_cutoff = min(8000, self.filter_cutoff + 200)
            print(f"Filter cutoff: {self.filter_cutoff}Hz")
        elif event.key == '7':
            filter_types = ['low', 'high', 'band']
            current_idx = filter_types.index(self.filter_type)
            self.filter_type = filter_types[(current_idx + 1) % len(filter_types)]
            print(f"Filter type: {self.filter_type}")
        elif event.key == '8':
            self.distortion_gain = max(1.0, self.distortion_gain - 0.5)
            print(f"Distortion gain: {self.distortion_gain:.1f}")
        elif event.key == '9':
            self.distortion_gain = min(5.0, self.distortion_gain + 0.5)
            print(f"Distortion gain: {self.distortion_gain:.1f}")
        elif event.key == 'q':
            plt.close('all')
        
        # Update status text
        self.status_text.set_text(self.get_status_text())
        self.fig.canvas.draw()
    
    def update_visualization(self, frame):
        """Update the visualization"""
        # Update waveforms
        self.line_input.set_ydata(self.input_buffer)
        self.line_output.set_ydata(self.output_buffer)
        
        # Update spectrums every few frames to reduce CPU load
        if frame % 5 == 0:
            # Compute and update input spectrum
            if np.any(self.input_buffer):
                freqs_in, psd_in = signal.welch(self.input_buffer, self.RATE, nperseg=1024)
                psd_db_in = 10 * np.log10(psd_in + 1e-12)
                
                self.ax_input_spec.clear()
                self.ax_input_spec.plot(freqs_in[:len(freqs_in)//4], psd_db_in[:len(psd_db_in)//4], 'cyan')
                self.ax_input_spec.set_title('Input Spectrum')
                self.ax_input_spec.set_xlabel('Frequency (Hz)')
                self.ax_input_spec.set_ylabel('Magnitude (dB)')
                self.ax_input_spec.set_xlim(0, 5000)
                self.ax_input_spec.set_ylim(-80, 0)
                self.ax_input_spec.grid(True, alpha=0.3)
            
            # Compute and update output spectrum
            if np.any(self.output_buffer):
                freqs_out, psd_out = signal.welch(self.output_buffer, self.RATE, nperseg=1024)
                psd_db_out = 10 * np.log10(psd_out + 1e-12)
                
                self.ax_output_spec.clear()
                self.ax_output_spec.plot(freqs_out[:len(freqs_out)//4], psd_db_out[:len(psd_db_out)//4], 'orange')
                self.ax_output_spec.set_title('Output Spectrum')
                self.ax_output_spec.set_xlabel('Frequency (Hz)')
                self.ax_output_spec.set_ylabel('Magnitude (dB)')
                self.ax_output_spec.set_xlim(0, 5000)
                self.ax_output_spec.set_ylim(-80, 0)
                self.ax_output_spec.grid(True, alpha=0.3)
        
        return self.line_input, self.line_output
    
    def run(self):
        """Start the audio effects processor"""
        print("Starting Interactive Audio Effects Processor...")
        print("Controls:")
        print("  R: Toggle Reverb")
        print("  E: Toggle Echo") 
        print("  F: Toggle Filter")
        print("  D: Toggle Distortion")
        print("  1-2: Adjust reverb decay")
        print("  3-4: Adjust echo delay")
        print("  5-6: Adjust filter cutoff")
        print("  7: Cycle filter type")
        print("  8-9: Adjust distortion gain")
        print("  Q: Quit")
        print("\nMake some noise and try the effects!")
        
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
        if hasattr(self, 'input_stream'):
            self.input_stream.stop_stream()
            self.input_stream.close()
        if hasattr(self, 'output_stream'):
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()
        plt.close('all')

if __name__ == "__main__":
    try:
        processor = AudioEffectsProcessor()
        processor.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()