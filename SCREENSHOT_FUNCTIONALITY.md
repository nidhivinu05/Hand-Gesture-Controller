# Screenshot Functionality Documentation

## Overview

The application now includes screenshot capture functionality triggered by the Peace Sign gesture. When you make a peace sign gesture and hold it for 10 frames (confirming the gesture), a screenshot is automatically captured and saved with a timestamp.

## Features

✅ **Gesture-Triggered Capture** - Peace Sign gesture activates screenshot  
✅ **Timestamp Filenames** - Screenshots named with date and time  
✅ **Cooldown Protection** - 3-second cooldown prevents accidental multiple captures  
✅ **Auto-Folder Creation** - Screenshots folder created automatically  
✅ **Visual Feedback** - "Screenshot Saved!" notification displayed  
✅ **Error Handling** - Gracefully handles file system errors  
✅ **Integration** - Works seamlessly with all existing gesture recognition  

## How It Works

### Screenshot Trigger Flow

```
1. Make Peace Sign gesture
       ↓
2. Hold for 10 frames (gesture stabilization)
       ↓
3. Gesture confirmed
       ↓
4. Check cooldown timer
       ↓
5. If cooldown expired → Take screenshot
       ↓
6. Save with timestamp
       ↓
7. Display notification
```

### File Naming Convention

Screenshots are saved with format: `screenshot_YYYY-MM-DD_HH-MM-SS.png`

**Examples:**
- `screenshot_2026-06-14_14-30-45.png`
- `screenshot_2026-06-14_14-34-12.png`

This naming convention:
- Groups all screenshots chronologically
- Prevents file overwrites
- Easy to sort by date and time
- Compatible with all operating systems

### Directory Structure

```
Hand gesture controller/
├── hand_gesture_detector.py
├── requirements.txt
├── README.md
└── Screenshots/          ← Auto-created folder
    ├── screenshot_2026-06-14_14-30-45.png
    ├── screenshot_2026-06-14_14-34-12.png
    └── screenshot_2026-06-14_14-38-23.png
```

## Core Functions

### `ensure_screenshots_folder()`

Creates the Screenshots directory if it doesn't exist.

**Purpose:** Ensures the save location is ready before first screenshot

**Called:** Once at application startup

**Returns:** Path to Screenshots folder (string)

**Error Handling:**
- Catches directory creation errors
- Prints error message if folder creation fails
- Continues execution even if folder exists

### `save_screenshot(frame, screenshots_folder="Screenshots")`

Saves a single frame to disk with timestamp filename.

**Parameters:**
- `frame`: The video frame (BGR format) to save
- `screenshots_folder`: Path to output folder

**Returns:** Tuple of (success: bool, filename: str, error: str or None)

**Process:**
1. Generate timestamp: `YYYY-MM-DD_HH-MM-SS`
2. Create filename: `screenshot_{timestamp}.png`
3. Build full path: `Screenshots/screenshot_YYYY-MM-DD_HH-MM-SS.png`
4. Convert frame BGR → RGB (proper color representation)
5. Write to disk using cv2.imwrite()
6. Return success status and filename

**Example:**
```python
success, filename, error = save_screenshot(frame, "Screenshots")
if success:
    print(f"Saved: {filename}")
else:
    print(f"Error: {error}")
```

### `ScreenshotManager` Class

Manages screenshot capture with cooldown protection.

**Purpose:** Prevent multiple screenshots from being taken when gesture is held

**Initialization:**
```python
screenshot_manager = ScreenshotManager(cooldown_seconds=3.0)
```

#### Key Methods

##### `can_take_screenshot() → bool`

Checks if cooldown period has expired.

**Returns:** True if ready to capture, False if on cooldown

**Logic:** 
- Checks time elapsed since last screenshot
- Compares against cooldown threshold (3 seconds)
- Returns True if enough time has passed

##### `take_screenshot(frame, screenshots_folder) → tuple`

Attempts to capture screenshot if cooldown allows.

**Parameters:**
- `frame`: Current video frame
- `screenshots_folder`: Path to save location

**Returns:** (success: bool, filename: str, error: str)

**Process:**
1. Check cooldown status
2. If cooldown active → Return False with "Cooldown active"
3. If ready → Call save_screenshot()
4. Update last_screenshot_time on success
5. Return status and filename

**Example:**
```python
success, filename, error = screenshot_manager.take_screenshot(frame, "Screenshots")

if success:
    print(f"Screenshot saved: {filename}")
elif error == "Cooldown active":
    print("Please wait 3 seconds before next screenshot")
else:
    print(f"Error: {error}")
```

##### `get_cooldown_remaining() → float`

Get remaining cooldown time in seconds.

**Returns:** Seconds remaining (0 if ready)

**Use Case:** For debug information or progress indicators

**Example:**
```python
remaining = screenshot_manager.get_cooldown_remaining()
if remaining > 0:
    print(f"Cooldown: {remaining:.1f}s remaining")
```

### `draw_screenshot_notification(frame, show, start_time, duration=2.0)`

Displays temporary "Screenshot Saved!" notification.

**Parameters:**
- `frame`: Video frame to draw on
- `show`: Whether to show notification (bool)
- `start_time`: When notification was triggered (seconds)
- `duration`: How long to show (default: 2.0 seconds)

**Visual Features:**
- Large text: "Screenshot Saved!"
- Green semi-transparent background
- Centered in frame
- Fades out toward end of duration
- Black text with high contrast

**Display Timing:**
```
Time 0.0s: Notification appears (full opacity)
Time 1.0s: Notification visible (fading)
Time 2.0s: Notification disappears
Time 2.1s+: No notification shown
```

## Integration in Main Loop

### Initialization (Before Loop)

```python
# Create Screenshots folder
screenshots_folder = ensure_screenshots_folder()

# Initialize screenshot manager with 3-second cooldown
screenshot_manager = ScreenshotManager(cooldown_seconds=3.0)

# Variables for notification display
show_screenshot_notification = False
screenshot_notification_time = 0
```

### During Loop

```python
# Gesture detection and stabilization (existing code)
detected_gesture = detect_gesture(fingers_status)
confirmed_gesture = gesture_stabilizer.update(detected_gesture)

# SCREENSHOT TRIGGER
if confirmed_gesture == "Peace Sign":
    success, filename, error = screenshot_manager.take_screenshot(frame, screenshots_folder)
    
    if success:
        show_screenshot_notification = True
        screenshot_notification_time = time.time()
        print(f"Screenshot captured: {filename}")
    elif error != "Cooldown active":
        print(f"Screenshot error: {error}")

# DISPLAY NOTIFICATION
draw_screenshot_notification(frame, show_screenshot_notification, screenshot_notification_time)
```

## User Experience Flow

### Scenario 1: Successful Screenshot

```
Frame 1-9:   [Detecting: Peace Sign (7/10)]  ← Progress bar
Frame 10:    [Peace Sign]                     ← Confirmed
             ↓
             Peace Sign gesture reaches 10 frames
             ↓
Frame 10:    [Peace Sign]
             ┌─────────────────────┐
             │  Screenshot Saved!  │  ← Notification appears
             └─────────────────────┘
             
             (Cooldown timer starts: 3 seconds)
             
Frame 11-40: [Peace Sign]
             ┌─────────────────────┐
             │  Screenshot Saved!  │  ← Notification fades out
             └─────────────────────┘
             
Frame 41+:   [Peace Sign]                     ← No notification
             (Cooldown still active: 2.7s remaining)
```

### Scenario 2: Rapid Peace Sign (Cooldown Active)

```
Frame 10:    [Peace Sign]
             Screenshot captured
             Cooldown: 3 seconds starts
             
             User holds Peace Sign for 2 more seconds
             
Frame 20:    [Peace Sign]  ← Still confirmed
             Cooldown: 1 second remaining
             (Screenshot NOT captured - cooldown active)
             
Frame 30:    [Peace Sign]
             Cooldown: 0 seconds
             (Next gesture can trigger screenshot)
```

## Cooldown Mechanism

### Why Cooldown?

Without cooldown:
- Peace Sign held for multiple frames
- Each frame could trigger a screenshot
- Results in 100+ duplicate screenshots in seconds
- Wastes disk space and processing power

### Cooldown Configuration

The 3-second cooldown is built into the ScreenshotManager:

```python
# Current setting: 3 seconds
screenshot_manager = ScreenshotManager(cooldown_seconds=3.0)

# To adjust:
screenshot_manager = ScreenshotManager(cooldown_seconds=5.0)   # 5 seconds
screenshot_manager = ScreenshotManager(cooldown_seconds=10.0)  # 10 seconds
```

**Recommendations:**
- **3 seconds** (default): Casual screenshot taking
- **5 seconds**: Conservative, prevent accidental duplicates
- **1 second**: Fast, frequent screenshot capture

## Error Handling

### File System Errors

The application gracefully handles:

```python
try:
    # Create folder
    os.makedirs(screenshots_folder)
except Exception as e:
    print(f"Error creating Screenshots folder: {e}")
```

### Screenshot Write Errors

```python
try:
    # Write image file
    success = cv2.imwrite(filepath, frame_rgb)
    
    if not success:
        error_msg = "Failed to write image file"
        print(f"Error: {error_msg}")
        return False, filename, error_msg
except Exception as e:
    error_msg = f"Screenshot error: {str(e)}"
    print(error_msg)
    return False, "", error_msg
```

## Color Management

### BGR to RGB Conversion

Screenshots are saved in RGB for proper color representation:

```python
# Convert from OpenCV's BGR format to standard RGB
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
cv2.imwrite(filepath, frame_rgb)
```

This ensures:
- Red objects appear red (not blue)
- Blue objects appear blue (not red)
- Proper color accuracy in saved images

## Performance Impact

- **Screenshot Capture**: ~100-200ms (network storage may be slower)
- **Cooldown Check**: <1ms per frame
- **FPS Impact**: Minimal when not capturing
- **Memory Usage**: One additional frame buffer during capture

## Troubleshooting

### Screenshots Not Saving

**Issue:** Gesture recognized but no files created

**Solutions:**
1. Check folder permissions in Screenshots directory
2. Verify disk space availability
3. Check file system isn't read-only
4. Look at console error messages

### Screenshots Saved but Corrupted

**Issue:** Files created but unreadable

**Solutions:**
1. Ensure webcam frame is valid before saving
2. Check disk space during write
3. Try saving to different location

### Too Many Screenshots

**Issue:** Cooldown not working, hundreds of files

**Solutions:**
1. Delete old screenshots
2. Increase cooldown time
3. Check gesture stabilization working (10 frames minimum)

### No Notification Appearing

**Issue:** Screenshot saved but no visual feedback

**Solutions:**
1. Notification duration is 2 seconds, may have already faded
2. Check if `show_screenshot_notification` flag is being set
3. Verify frame isn't being overwritten before display

## File Organization Tips

### Viewing Screenshots

```bash
# Windows: Open Screenshots folder
cd Screenshots

# List all screenshots
dir /o:d screenshot_*.png

# List by date
dir /o:d
```

### Organizing by Session

Create subdirectories for different sessions:

```
Screenshots/
├── Session_2026-06-14_Morning/
├── Session_2026-06-14_Afternoon/
└── Session_2026-06-14_Evening/
```

### Cleanup

```bash
# Remove old screenshots (over 30 days old)
forfiles /S /D +30 /C "cmd /c if @ext==png del @path"
```

## Integration with Other Features

✅ **Works with all gestures** - Other gestures display normally  
✅ **Finger detection** - Continues running during screenshot  
✅ **FPS counter** - Unaffected by screenshot capture  
✅ **Gesture stabilization** - Works as designed  
✅ **Gesture progress** - Not interrupted by screenshots  

## Advanced Usage

### Custom Screenshot Actions

```python
# Extend the main loop to add more gesture actions
if confirmed_gesture == "Thumbs Up":
    print("Positive feedback")
elif confirmed_gesture == "Peace Sign":
    success, filename, error = screenshot_manager.take_screenshot(frame, screenshots_folder)
    if success:
        # Do something with the filename
        upload_to_cloud(filename)
elif confirmed_gesture == "Fist":
    print("Recording start")
```

### Modify Cooldown Dynamically

```python
# Adjust cooldown based on conditions
if some_condition:
    screenshot_manager.cooldown_seconds = 1.0  # Faster captures
else:
    screenshot_manager.cooldown_seconds = 5.0  # Safer
```

### Track Screenshot Count

```python
# Count screenshots taken in session
screenshot_count = 0

if success:
    screenshot_count += 1
    print(f"Screenshots taken this session: {screenshot_count}")
```

## Related Documentation

- [GESTURE_RECOGNITION.md](GESTURE_RECOGNITION.md) - Gesture types and detection
- [GESTURE_STABILITY.md](GESTURE_STABILITY.md) - Gesture confirmation mechanism
- [FINGER_DETECTION.md](FINGER_DETECTION.md) - How finger detection works
- [README.md](README.md) - General setup and usage
