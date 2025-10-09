# Audio Processing Project - Week 6

This project contains various audio processing applications demonstrating real-time audio capture, processing, visualization, and effects.

## Project Structure

### Original Files (Fixed/Enhanced)
- `1_random_audio.py` - Generates and plays random audio
- `2_gen_audio.py` - AI-powered audio generation using AudioLDM2
- `3_synth_audio.py` - Simple audio synthesis with pyo
- `4a_asyncio_loopback.py` - Audio loopback using asyncio
- `4b_pyaudio_loopback.py` - Simple audio loopback
- `5_spectrogram.py` - Real-time spectrogram visualization (enhanced)
- `5_waveform.py` - Real-time waveform visualization (completely rewritten and fixed)
- `6a_spectrogram_pygame.py` - Pygame-based spectrogram with smooth visualization
- `6b_spectrogram.py` - Alternative matplotlib spectrogram implementation
- `list_devices.py` - Lists available audio devices

### New Creative Features
- `7_interactive_effects.py` - **Interactive Audio Effects Processor** ???
- `8_beat_detector.py` - **Beat Detection and Rhythm Visualization** ??
- `9_advanced_recorder.py` - **Advanced Multi-Channel Audio Recorder** ???

## Requirements

Install the required packages:

```bash
# Basic requirements
pip install -r requirements.txt

# For AI audio generation (optional, requires CUDA)
pip install -r torch_requirements.txt
```

### Dependencies
- `pyaudio` - Audio I/O
- `numpy` - Numerical computing
- `matplotlib` - Plotting and visualization
- `scipy` - Signal processing
- `pygame` - Game development library (for 6a)
- `pyo` - Digital signal processing
- `diffusers` - AI audio generation (optional)
- `transformers` - AI models (optional)
- `torch` - Deep learning framework (optional)

## Usage Guide

### Basic Audio Applications

#### 1. Random Audio Generator (`1_random_audio.py`)
```bash
python 1_random_audio.py
```
Generates and plays random audio noise. Press Ctrl+C to stop.

#### 2. AI Audio Generation (`2_gen_audio.py`)
```bash
python 2_gen_audio.py
```
Uses AudioLDM2 to generate music from text descriptions. **Requires CUDA GPU**.
- Enter text descriptions like "upbeat jazz piano" or "ambient electronic music"
- Generates 60-second audio clips

#### 3. Simple Synthesis (`3_synth_audio.py`)
```bash
python 3_synth_audio.py
```
Plays a simple 440Hz sine wave for 1 second.

### Audio Loopback

#### 4a. Asyncio Loopback (`4a_asyncio_loopback.py`)
```bash
python 4a_asyncio_loopback.py
```
Advanced loopback using asyncio for better performance.

#### 4b. Simple Loopback (`4b_pyaudio_loopback.py`)
```bash
python 4b_pyaudio_loopback.py
```
Basic audio loopback - what you speak into the microphone plays through speakers.

### Real-Time Visualization

#### 5. Enhanced Spectrogram (`5_spectrogram.py`)
```bash
python 5_spectrogram.py
```
**Features:**
- Real-time spectrogram and waveform display
- Automatic signal amplification for quiet sounds
- Dynamic scaling and frequency range up to 4kHz
- RMS and peak level monitoring

#### 5. Improved Waveform (`5_waveform.py`)
```bash
python 5_waveform.py
```
**Completely rewritten with:**
- Thread-safe audio processing
- Smooth real-time waveform display
- Dynamic amplitude scaling
- Audio level statistics

#### 6a. Pygame Spectrogram (`6a_spectrogram_pygame.py`)
```bash
python 6a_spectrogram_pygame.py
```
**Advanced features:**
- High-performance real-time spectrogram
- Smooth color transitions and temporal smoothing
- Interactive controls (?/? for smoothing, R to reset)
- Dual waveform and spectrum display

#### 6b. Alternative Spectrogram (`6b_spectrogram.py`)
```bash
python 6b_spectrogram.py
```
Matplotlib-based spectrogram with forced display even for quiet signals.

## ??? NEW: Interactive Audio Effects Processor (`7_interactive_effects.py`)

**The most advanced feature!** Real-time audio effects with visual feedback.

```bash
python 7_interactive_effects.py
```

### Features:
- **Real-time audio effects processing**
- **Live input/output waveform comparison**
- **Frequency spectrum analysis**
- **Interactive keyboard controls**

### Effects Available:
1. **Reverb** - Adds spacious echo effect
2. **Echo** - Configurable delay and feedback
3. **Frequency Filter** - Low-pass, high-pass, or band-pass filtering
4. **Distortion** - Soft-clipping distortion with adjustable gain

### Controls:
- `R` - Toggle Reverb
- `E` - Toggle Echo
- `F` - Toggle Filter
- `D` - Toggle Distortion
- `1-2` - Adjust reverb decay (less/more)
- `3-4` - Adjust echo delay (shorter/longer)
- `5-6` - Adjust filter cutoff frequency (lower/higher)
- `7` - Cycle filter type (low/high/band)
- `8-9` - Adjust distortion gain (less/more)
- `Q` - Quit

### Visualization:
- **Input Audio** - Original signal
- **Processed Audio** - Signal after effects
- **Input Spectrum** - Frequency content of input
- **Output Spectrum** - Frequency content after processing
- **Real-time parameter display**

## ?? NEW: Beat Detection and Rhythm Visualization (`8_beat_detector.py`)

Advanced beat detection with stunning visual feedback.

```bash
python 8_beat_detector.py
```

### Features:
- **Real-time beat detection** using spectral flux analysis
- **Tempo estimation** in BPM (60-180 range)
- **Adaptive thresholding** for different music types
- **Visual rhythm patterns** with colored circles
- **Tempo indicator** with rotating line

### Visualization Components:
1. **Central Rhythm Display** - Circular visualization with beat circles
2. **Onset Strength Plot** - Shows beat detection analysis
3. **Tempo History** - BPM changes over time
4. **Audio Waveform** - Current audio input
5. **Real-time statistics** - Current tempo, beats detected, etc.

### Best Results:
- Play music with clear, consistent beats
- Electronic music, pop, rock work well
- Adjust your audio levels for optimal detection

## ??? NEW: Advanced Multi-Channel Audio Recorder (`9_advanced_recorder.py`)

Professional-grade audio recording with comprehensive features.

```bash
python 9_advanced_recorder.py
```

### Features:
- **Stereo/Mono recording** (automatically detects capabilities)
- **Real-time level monitoring** with dB meters
- **Multiple recording sessions** with timeline view
- **Pause/Resume functionality**
- **WAV file export** with metadata
- **Playback of recorded audio**
- **Visual feedback** with waveforms and levels

### Recording Controls:
- `R` - Start/Stop recording
- `P` - Pause/Resume recording
- `S` - Stop current recording
- `W` - Save last recording as WAV file
- `Space` - Play back last recording
- `C` - Clear all recordings

### Interface:
- **Stereo Waveforms** - Left and right channel display
- **Level Meters** - Real-time dB monitoring with peak indicators
- **Recording Timeline** - Visual representation of all sessions
- **Control Buttons** - Mouse-clickable interface
- **Status Display** - Complete session information

### Output:
- Files saved to `recordings/` directory
- Automatic timestamped filenames
- JSON metadata with session information
- High-quality 44.1kHz, 16-bit WAV format

## Utility

#### Device Listing (`list_devices.py`)
```bash
python list_devices.py
```
Lists all available audio input devices on your system.

## Troubleshooting

### Common Issues:

1. **"No input device found"**
   - Run `python list_devices.py` to see available devices
   - Make sure your microphone is connected and enabled
   - Try different USB ports for USB microphones

2. **Audio feedback/echo**
   - Use headphones instead of speakers for loopback applications
   - Adjust microphone and speaker volumes
   - Move microphone away from speakers

3. **Performance issues**
   - Close other audio applications
   - Reduce buffer sizes in the code if needed
   - Use a faster computer for real-time processing

4. **CUDA/GPU errors (for AI generation)**
   - Install CUDA toolkit if you have NVIDIA GPU
   - Fall back to CPU processing (much slower)
   - Skip the AI generation features if no GPU available

5. **Import errors**
   - Install missing packages: `pip install package_name`
   - Use virtual environment to avoid conflicts
   - Check Python version compatibility

### Audio Device Setup:
- **Windows**: Use WASAPI or DirectSound drivers
- **Linux**: ALSA or PulseAudio
- **macOS**: Core Audio

## Creative Possibilities

### Suggested Experiments:

1. **Live Performance Setup**
   - Use `7_interactive_effects.py` for live audio processing
   - Connect instruments or microphones
   - Create custom effect chains

2. **Music Analysis**
   - Use `8_beat_detector.py` to analyze different music genres
   - Study tempo patterns in your favorite songs
   - Create visual music experiences

3. **Recording Projects**
   - Use `9_advanced_recorder.py` for podcasts or music
   - Record multiple takes and compare them
   - Create sound libraries

4. **Educational Demonstrations**
   - Show audio concepts with real-time visualization
   - Demonstrate frequency analysis and filtering
   - Teach about audio effects and processing

5. **Creative Combinations**
   - Chain multiple applications together
   - Use virtual audio cables to route between programs
   - Create complex audio processing pipelines

## Technical Details

### Audio Parameters:
- **Sample Rate**: 44.1 kHz (CD quality)
- **Bit Depth**: 16-bit (some applications use 32-bit float)
- **Channels**: Mono or Stereo (depending on application)
- **Buffer Size**: Optimized for real-time performance

### Processing Techniques:
- **FFT-based spectrogram analysis**
- **Spectral flux for beat detection**
- **IIR filtering for audio effects**
- **Overlap-add processing for smooth effects**
- **Adaptive thresholding for robust detection**

### Performance Optimizations:
- **Multi-threading** for audio I/O separation
- **Circular buffers** for efficient data management
- **Vectorized operations** using NumPy
- **Frame-based processing** to reduce latency

## License and Credits

This project is for educational purposes. Dependencies have their own licenses:
- PyAudio: MIT License
- NumPy: BSD License
- Matplotlib: PSF License
- SciPy: BSD License
- PyGame: LGPL License

---

**Enjoy exploring the world of audio processing! ????**

For questions or issues, check the code comments or create an issue in the repository.