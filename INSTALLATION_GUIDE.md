# Installation and Quick Start Guide

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python hand_gesture_detector.py
```

### Step 3: Use Volume Control
- **Thumbs Up** ⬆️ (hand pointing up) → Volume increases by 5%
- **Thumbs Down** ⬇️ (hand pointing down) → Volume decreases by 5%
- **Peace Sign** ✌️ → Takes a screenshot

### Step 4: Exit
Press `q` to quit the application

---

## Detailed Installation

### Requirements

- **Windows 7** or later
- **Python 3.7** or later
- **Webcam** (built-in or USB)
- **Administrator access** (may be needed for volume control on some systems)

### Option 1: Fresh Installation

#### 1.1 Clone or Download Project
```bash
# If using git
git clone <repository-url>
cd hand_gesture_controller

# Or download ZIP and extract
```

#### 1.2 Install All Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `opencv-python==4.8.1.78` - Computer vision
- `mediapipe==0.10.8` - Hand detection
- `pyautogui==0.9.53` - Screenshot capture
- `Pillow==10.0.1` - Image processing
- `win10toast==0.9` - Desktop notifications
- `pycaw==20240126` - **Volume control (NEW)**

#### 1.3 Run the Application
```bash
python hand_gesture_detector.py
```

### Option 2: Upgrading Existing Installation

If you already have the application installed:

#### 2.1 Update requirements.txt
Ensure file has:
```
pycaw==20240126
```

#### 2.2 Install New Dependency
```bash
pip install pycaw==20240126
```

#### 2.3 Replace hand_gesture_detector.py
Update your main Python file with the new version containing volume control.

#### 2.4 Run Updated Application
```bash
python hand_gesture_detector.py
```

### Option 3: Manual Installation of Individual Packages

If pip install fails:

```bash
# Install each package individually
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.8
pip install pyautogui==0.9.53
pip install Pillow==10.0.1
pip install win10toast==0.9
pip install pycaw==20240126
```

---

## Verification

### Step 1: Check Python Version
```bash
python --version
```
Should show Python 3.7 or higher

### Step 2: Check Dependencies
```bash
python -c "import cv2; print('OpenCV OK')"
python -c "import mediapipe; print('MediaPipe OK')"
python -c "import pyautogui; print('PyAutoGUI OK')"
python -c "from PIL import Image; print('Pillow OK')"
python -c "from win10toast import ToastNotifier; print('win10toast OK')"
python -c "from pycaw.pycaw import AudioUtilities; print('pycaw OK')"
```

### Step 3: Check Webcam Access
```python
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("Webcam accessible")
    cap.release()
else:
    print("Webcam not accessible")
```

### Step 4: Run Application
```bash
python hand_gesture_detector.py
```

You should see:
- OpenCV window titled "GestureOS"
- Live webcam feed with hand landmarks
- FPS counter in top-left
- Volume control ready (test with Thumbs Up/Down)

---

## Troubleshooting Installation

### Error: "ModuleNotFoundError: No module named 'pycaw'"

**Solution 1**: Install pycaw
```bash
pip install pycaw==20240126
```

**Solution 2**: Check Python path
```bash
python -m pip install pycaw==20240126
```

**Solution 3**: Use explicit Python 3
```bash
python3 -m pip install pycaw==20240126
```

### Error: "No module named 'cv2' (OpenCV)"

**Solution**: Install OpenCV
```bash
pip install opencv-python==4.8.1.78
```

### Error: "No module named 'mediapipe'"

**Solution**: Install MediaPipe
```bash
pip install mediapipe==0.10.8
```

### Error: "Cannot open webcam"

**Solutions**:
1. Check if another app is using the webcam
2. Disconnect and reconnect the webcam
3. Check Windows Device Manager for camera device
4. Grant camera permissions in Windows Settings

### Error: "pycaw: Permission denied"

**Solution**: Run as Administrator
```bash
# Windows: Right-click command prompt and select "Run as Administrator"
python hand_gesture_detector.py
```

### Error: "Volume control support unavailable"

**Solutions**:
1. Application still works - feature just disabled
2. Ensure Windows 7 or later
3. Try updating: `pip install --upgrade pycaw==20240126`
4. Check Windows audio device is connected

---

## Using Volume Control

### Basic Usage

1. **Start the app**
   ```bash
   python hand_gesture_detector.py
   ```

2. **Make Thumbs Up gesture**
   - Raise only thumb, keep other fingers folded
   - Point hand upward
   - Hold steady for ~1 second
   - Desktop notification: "Volume Increased - Volume: XX%"
   - Volume increases by 5%

3. **Make Thumbs Down gesture**
   - Raise only thumb, keep other fingers folded
   - Point hand downward
   - Hold steady for ~1 second
   - Desktop notification: "Volume Decreased - Volume: XX%"
   - Volume decreases by 5%

4. **Wait between gestures**
   - 1 second cooldown prevents rapid changes
   - Steady, controlled volume adjustment

### Customization

#### Change Volume Step Size

Edit line 1028 in `hand_gesture_detector.py`:

```python
# For 2% steps (more granular)
volume_manager = VolumeManager(cooldown_seconds=1.0, volume_step=0.02)

# For 10% steps (faster changes)
volume_manager = VolumeManager(cooldown_seconds=1.0, volume_step=0.10)
```

#### Change Cooldown Duration

Edit line 1028 in `hand_gesture_detector.py`:

```python
# For 0.5 second cooldown (faster)
volume_manager = VolumeManager(cooldown_seconds=0.5, volume_step=0.05)

# For 2 second cooldown (slower)
volume_manager = VolumeManager(cooldown_seconds=2.0, volume_step=0.05)
```

#### Disable Notifications

Comment out lines 1128-1131 and 1143-1146 in `hand_gesture_detector.py`:

```python
# notify_success, notify_error = show_desktop_notification(
#     "Volume Increased",
#     message,
#     duration=2
# )
```

---

## All Gesture Commands

### Screenshot (Peace Sign)
- **Gesture**: Index and middle fingers raised, others folded
- **Action**: Captures full desktop screenshot
- **Output**: Saved to Screenshots/ folder as PNG
- **Format**: screenshot_YYYY-MM-DD_HH-MM-SS.png
- **Notification**: "Screenshot Saved - filename"
- **Cooldown**: 3 seconds between screenshots

### Volume Up (Thumbs Up)
- **Gesture**: Only thumb raised, hand pointing upward
- **Action**: Increases system volume by 5%
- **Range**: 0% to 100%
- **Notification**: "Volume Increased - Volume: XX%"
- **Cooldown**: 1 second between changes

### Volume Down (Thumbs Down)
- **Gesture**: Only thumb raised, hand pointing downward
- **Action**: Decreases system volume by 5%
- **Range**: 0% to 100%
- **Notification**: "Volume Decreased - Volume: XX%"
- **Cooldown**: 1 second between changes

### Other Gestures (Display Only)
- **Open Palm**: All fingers raised - displays "Open Palm"
- **Fist**: All fingers folded - displays "Fist"
- **Peace Sign**: Used for screenshot (see above)
- **Rock Sign**: Index + pinky raised - displays "Rock Sign"

---

## File Organization

```
hand_gesture_controller/
├── hand_gesture_detector.py          # Main application
├── requirements.txt                  # Python dependencies
├── README.md                         # Project overview
├── IMPLEMENTATION_SUMMARY.md         # Volume control implementation details
├── VOLUME_CONTROL.md                 # Detailed volume control documentation
├── VOLUME_CONTROL_QUICK_REFERENCE.md # Quick reference for volume control
├── CODE_CHANGES_REFERENCE.md         # Exact code changes and locations
├── GESTURE_RECOGNITION.md            # Gesture recognition documentation
├── GESTURE_STABILITY.md              # Gesture stabilization documentation
├── FINGER_DETECTION.md               # Finger detection documentation
├── SCREENSHOT_FUNCTIONALITY.md       # Screenshot feature documentation
├── SCREENSHOT_QUICK_REFERENCE.md     # Screenshot quick reference
└── Screenshots/                      # Folder for saved screenshots (auto-created)
```

---

## Performance Expectations

### Hardware Requirements
- **Processor**: Any modern CPU (Intel i3+, AMD Ryzen 3+)
- **RAM**: 4GB minimum (2GB sufficient for application)
- **Webcam**: 720p+ recommended

### Performance Metrics
- **FPS**: 25-60+ depending on hardware
- **Latency**: ~100-200ms from gesture to action
- **CPU Usage**: <10% typical
- **Memory**: ~200-300MB
- **Startup Time**: 5-10 seconds

---

## Common Issues and Solutions

### Issue: "Gesture detected but volume doesn't change"

**Causes & Solutions**:
1. Volume already at max/min
   - Check Windows volume is not at 100% or 0%
2. Cooldown active
   - Wait 1 second between gestures
3. Gesture not held long enough
   - Hold gesture steady for ~1 second
4. Hand not visible
   - Ensure full hand in webcam frame

### Issue: "Notifications don't show"

**Solution**: Optional feature, not required
- Application works fine without notifications
- If desired, check Windows notification settings
- Or reinstall: `pip install --upgrade win10toast==0.9`

### Issue: "Application crashes when using volume control"

**Solutions**:
1. Run as Administrator
2. Update Windows to latest version
3. Update audio drivers
4. Reinstall pycaw: `pip install --upgrade pycaw==20240126`

### Issue: "Screenshot not working but volume works"

**Solutions**:
1. Verify PyAutoGUI installed: `pip install pyautogui==0.9.53`
2. Check Screenshots folder exists
3. Verify Peace Sign gesture is correct (index + middle raised)
4. Check disk space is available

### Issue: "Application runs but no window appears"

**Solutions**:
1. Check if window appears behind other windows
2. Alt+Tab to find "GestureOS" window
3. Check Console for error messages
4. Verify webcam is not in use by another app

---

## Getting Help

### Check Logs

The application prints to console. Look for:
- Error messages about missing dependencies
- Volume control availability status
- Gesture detection status
- Screenshot save confirmations

### Enable Verbose Output

Run application and watch console for:
```
FPS: XX.XX
Thumb: RAISED
Index: FOLDED
...
Volume increased: Volume: 45%
Screenshot captured: screenshot_...
```

### Documentation Files

- **VOLUME_CONTROL.md** - Comprehensive volume control docs
- **README.md** - Project overview
- **CODE_CHANGES_REFERENCE.md** - All code changes with line numbers

---

## Next Steps

1. **Run the application**
   ```bash
   python hand_gesture_detector.py
   ```

2. **Test volume control**
   - Make Thumbs Up → Volume increases
   - Make Thumbs Down → Volume decreases

3. **Test screenshot**
   - Make Peace Sign → Screenshot saved

4. **Customize settings** (optional)
   - Edit line 1028 for different volume steps
   - Edit line 1028 for different cooldown

5. **Read documentation**
   - VOLUME_CONTROL.md for detailed info
   - CODE_CHANGES_REFERENCE.md for technical details

---

## Support

If you encounter issues:

1. **Check console output** for error messages
2. **Verify all dependencies installed** - run verification steps
3. **Check Windows version** - must be Windows 7+
4. **Run as Administrator** - may be needed for volume API
5. **Review documentation** - check VOLUME_CONTROL.md

---

## Quick Troubleshooting Checklist

- [ ] Python 3.7+ installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Webcam working and not in use
- [ ] Application runs: `python hand_gesture_detector.py`
- [ ] Hand detected in webcam window
- [ ] Gestures displayed correctly
- [ ] Thumbs Up gesture increases volume
- [ ] Thumbs Down gesture decreases volume
- [ ] Peace Sign gesture takes screenshot

---

## Version Information

- **Application**: Hand Gesture Controller with Volume Control
- **Volume Control**: Added June 2024
- **Python**: 3.7+
- **OS**: Windows 7, 8, 10, 11
- **pycaw Version**: 20240126

---

## Ready to Use!

You're all set! Start with:

```bash
python hand_gesture_detector.py
```

Enjoy gesture-based volume control! 🎚️

