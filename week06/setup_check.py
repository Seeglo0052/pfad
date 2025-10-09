#!/usr/bin/env python3
"""
Setup and Installation Script for Audio Processing Project
Checks dependencies and provides installation guidance
"""

import sys
import importlib
import subprocess
import platform

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("? Python 3.6 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"? Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"? {package_name} - OK")
        return True
    except ImportError:
        print(f"? {package_name} - NOT FOUND")
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"? {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"? Failed to install {package_name}")
        return False

def main():
    print("?? Audio Processing Project Setup ??")
    print("=" * 50)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if not check_python_version():
        return
    
    # Define required packages
    basic_packages = [
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("scipy", "scipy"),
        ("pyaudio", "pyaudio"),
    ]
    
    optional_packages = [
        ("pygame", "pygame"),
        ("pyo", "pyo"),
    ]
    
    ai_packages = [
        ("torch", "torch"),
        ("diffusers", "diffusers"),
        ("transformers", "transformers"),
        ("accelerate", "accelerate"),
    ]
    
    # Check basic packages
    print("\n2. Checking basic packages...")
    missing_basic = []
    for package_name, import_name in basic_packages:
        if not check_package(package_name, import_name):
            missing_basic.append(package_name)
    
    # Check optional packages
    print("\n3. Checking optional packages...")
    missing_optional = []
    for package_name, import_name in optional_packages:
        if not check_package(package_name, import_name):
            missing_optional.append(package_name)
    
    # Check AI packages
    print("\n4. Checking AI packages (optional)...")
    missing_ai = []
    for package_name, import_name in ai_packages:
        if not check_package(package_name, import_name):
            missing_ai.append(package_name)
    
    # System-specific checks
    print("\n5. System information...")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Provide installation instructions
    print("\n" + "=" * 50)
    print("INSTALLATION SUMMARY")
    print("=" * 50)
    
    if missing_basic:
        print("\n? REQUIRED packages missing:")
        for package in missing_basic:
            print(f"   - {package}")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing_basic)}")
        print("\nOr use the requirements file:")
        print("   pip install -r requirements.txt")
    
    if missing_optional:
        print("\n??  OPTIONAL packages missing:")
        for package in missing_optional:
            print(f"   - {package}")
        print("\nSome features will be unavailable:")
        if "pygame" in missing_optional:
            print("   - 6a_spectrogram_pygame.py won't work")
        if "pyo" in missing_optional:
            print("   - 3_synth_audio.py won't work")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing_optional)}")
    
    if missing_ai:
        print("\n?? AI packages missing:")
        for package in missing_ai:
            print(f"   - {package}")
        print("\nAI audio generation (2_gen_audio.py) won't work")
        print("These packages are large and require CUDA for GPU acceleration")
        print("\nInstall with:")
        print("   pip install -r torch_requirements.txt")
        print("   pip install diffusers transformers accelerate")
    
    # Audio system checks
    print("\n" + "=" * 50)
    print("AUDIO SYSTEM CHECKS")
    print("=" * 50)
    
    if check_package("pyaudio", "pyaudio"):
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            print(f"\n?? Audio system information:")
            print(f"   Host APIs: {p.get_host_api_count()}")
            print(f"   Audio devices: {p.get_device_count()}")
            
            # List input devices
            input_devices = []
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    input_devices.append((i, device_info['name'], device_info['maxInputChannels']))
            
            if input_devices:
                print(f"\n???  Input devices found ({len(input_devices)}):")
                for idx, name, channels in input_devices[:5]:  # Show first 5
                    print(f"   [{idx}] {name} ({channels} channels)")
                if len(input_devices) > 5:
                    print(f"   ... and {len(input_devices) - 5} more")
            else:
                print("\n? No input devices found!")
                print("   Make sure your microphone is connected and enabled")
            
            p.terminate()
            
        except Exception as e:
            print(f"\n? Audio system error: {e}")
    
    # Final recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)
    
    if not missing_basic:
        print("\n? All basic packages installed! You can run:")
        print("   - All visualization programs (5_*.py, 6_*.py)")
        print("   - Audio loopback programs (4_*.py)")
        print("   - New creative features (7_*.py, 8_*.py, 9_*.py)")
    
    print("\n?? To get started:")
    print("   1. Run 'python list_devices.py' to see your audio devices")
    print("   2. Try 'python 5_waveform.py' for basic audio visualization")
    print("   3. Test 'python 7_interactive_effects.py' for interactive effects")
    print("   4. Use 'python 8_beat_detector.py' with music for beat detection")
    print("   5. Try 'python 9_advanced_recorder.py' for recording")
    
    print("\n?? Tips:")
    print("   - Use headphones to avoid audio feedback")
    print("   - Adjust microphone levels for best results")
    print("   - Close other audio applications while testing")
    print("   - See README.md for detailed usage instructions")
    
    if platform.system() == "Windows":
        print("\n?? Windows users:")
        print("   - PyAudio installation might need Visual C++ redistributables")
        print("   - Consider using conda instead of pip for easier installation")
    
    print("\n?? Happy audio processing! ??")

if __name__ == "__main__":
    main()