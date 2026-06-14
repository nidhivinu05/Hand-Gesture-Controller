# Screenshot Functionality - Quick Reference

## How to Take Screenshots

### Step-by-Step

1. **Start the application**
   ```bash
   python hand_gesture_detector.py
   ```

2. **Make the Peace Sign**
   - Raise index and middle fingers
   - Fold thumb, ring, and pinky

3. **Hold the gesture for 1 second** (10 frames at ~30 FPS)
   - Wait for gesture to be confirmed
   - You'll see: `[Peace Sign]` in top-right corner

4. **Screenshot is captured automatically**
   - File saved to: `Screenshots/` folder
   - Filename: `screenshot_YYYY-MM-DD_HH-MM-SS.png`
   - Notification: "Screenshot Saved!" appears on screen

5. **Wait 3 seconds before next screenshot**
   - Cooldown prevents accidental duplicates
   - After 3 seconds, you can take another screenshot

## What You'll See

### During Gesture Detection
```
FPS: 30.45
Thumb: FOLDED
Index: RAISED
Middle: RAISED
Ring: FOLDED
Pinky: FOLDED
Total Raised: 2

Detecting: Peace Sign (7/10)
[=======        ] 70%
```

### After 10 Frames (Confirmed)
```
FPS: 30.45
Thumb: FOLDED
Index: RAISED
Middle: RAISED
Ring: FOLDED
Pinky: FOLDED
Total Raised: 2
                    [Peace Sign]  ← Gesture confirmed
```

### Screenshot Captured
```
FPS: 30.45
                    [Peace Sign]
                ┌─────────────────────┐
                │  Screenshot Saved!  │  ← Notification
                └─────────────────────┘

# File saved: Screenshots/screenshot_2026-06-14_14-30-45.png
```

## File Locations

### Screenshots Folder
- **Path**: `Hand gesture controller/Screenshots/`
- **Auto-created**: Yes (first time you take a screenshot)
- **Contains**: All captured screenshots with timestamps

### Example Files
```
Screenshots/
├── screenshot_2026-06-14_14-30-45.png
├── screenshot_2026-06-14_14-34-12.png
├── screenshot_2026-06-14_14-38-23.png
└── screenshot_2026-06-14_15-42-10.png
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit application |
| Any other | Ignored |

## Troubleshooting

### Screenshot Not Saving

**Check 1:** Is the gesture confirmed?
- Look for `[Peace Sign]` in top-right corner
- Must hold for full 10 frames to confirm

**Check 2:** Is cooldown active?
- You must wait 3 seconds between screenshots
- Try again after the cooldown

**Check 3:** Does Screenshots folder exist?
- Check: `Hand gesture controller/Screenshots/`
- If missing, it will be created on first capture
- Check folder permissions if creation fails

**Check 4:** Is there disk space?
- Ensure your drive has enough free space
- Each screenshot is typically 100-500 KB

### Notification Not Showing

**Normal behavior**: Notification appears for 2 seconds then fades
- If you miss it, check console output
- File will be saved regardless of notification

### Too Many Screenshots

**Problem**: Hundreds of duplicate files

**Solutions:**
1. You're re-triggering gesture quickly - wait for cooldown
2. Delete old screenshots manually:
   - Open `Screenshots/` folder
   - Delete old `screenshot_*.png` files
3. Increase cooldown time in code (if desired)

## All Gesture Shortcuts (Reminder)

| Gesture | Fingers | Effect |
|---------|---------|--------|
| Open Palm | All 5 raised | Displays "Open Palm" |
| Fist | All folded | Displays "Fist" |
| Thumbs Up | Thumb only | Displays "Thumbs Up" |
| Peace Sign | Index + Middle | **Takes screenshot** ✓ |
| Rock Sign | Index + Pinky | Displays "Rock Sign" |

## Complete Session Example

```
$ python hand_gesture_detector.py

# Application starts, webcam opens
# Screenshot folder created: "Screenshots"

# User makes Peace Sign and holds it
# [Frame 1-9] Detecting: Peace Sign (1/10) ... (9/10)
# [Frame 10] [Peace Sign] ← Confirmed

# Screenshot captured
# File: Screenshots/screenshot_2026-06-14_14-30-45.png

# Wait 3 seconds...

# Make Peace Sign again
# [Frames 1-10] Detecting: Peace Sign → [Peace Sign]
# Screenshot captured
# File: Screenshots/screenshot_2026-06-14_14-34-12.png

# Press 'q' to exit
# Application closed successfully

# Navigate to Screenshots folder
# See 2 screenshot files saved with timestamps
```

## Tips & Tricks

### Maximize Success

1. **Good Lighting** - Ensure clear hand visibility
2. **Steady Hand** - Minimize movement while holding gesture
3. **Full Frame** - Keep hand fully visible in camera
4. **Proper Gesture** - Make sure index + middle are clearly raised

### Multiple Screenshots Quickly

You need to wait 3 seconds between screenshots. For faster capture:

**Method 1:** Perform different gestures (if you add more actions later)

**Method 2:** Modify cooldown in code
```python
# Edit line in hand_gesture_detector.py:
screenshot_manager = ScreenshotManager(cooldown_seconds=1.0)  # 1 second instead of 3
```

### View Screenshots

**Windows Explorer:**
1. Open: `C:\Users\[YourUsername]\OneDrive\Desktop\Hand gesture controller\Screenshots`
2. Files sorted by name (which is chronological due to timestamp format)

**Command Line:**
```bash
cd Screenshots
dir /o:d        # List files by date
```

## Performance Notes

- **FPS**: Screenshot capture doesn't significantly impact FPS
- **Latency**: Gesture to file save: ~500ms to 1 second
- **File Size**: ~100-500 KB per screenshot (depends on resolution)
- **Disk Space**: ~100 screenshots = 20-50 MB

## File Naming Breakdown

Example: `screenshot_2026-06-14_14-30-45.png`

```
screenshot_      ← Fixed prefix
2026             ← Year
-06              ← Month (06 = June)
-14              ← Day
_14              ← Hour (24-hour format)
-30              ← Minute
-45              ← Second
.png             ← File extension
```

### Why This Format?

✓ **Chronological**: Files sort by date naturally  
✓ **Unique**: No filename collisions (unless same second)  
✓ **Readable**: Easy to find screenshots from specific times  
✓ **Universal**: Works on Windows, Mac, Linux  

## Error Messages (Console)

### Created 'Screenshots' folder
- **Meaning**: First-time setup, folder was created successfully
- **Action**: None needed, normal operation

### Screenshot saved: screenshot_2026-06-14_14-30-45.png
- **Meaning**: File successfully written
- **Action**: Check Screenshots folder for the file

### Screenshot error: [error message]
- **Meaning**: Failed to save screenshot
- **Action**: Check console for details, verify disk space

### Cooldown active
- **Meaning**: Too soon since last screenshot (less than 3 seconds)
- **Action**: Wait before attempting next screenshot

## Next Steps

1. ✓ Take some screenshots with Peace Sign
2. ✓ Check the Screenshots folder for files
3. ✓ Review captured images
4. Consider: Adding more gesture-triggered actions
5. Consider: Modifying cooldown time for your use case

## Feature Requests / Enhancements

Could be added in future:
- [ ] Capture other gestures (screenshot on Fist, etc.)
- [ ] Add custom metadata to screenshots
- [ ] Auto-upload screenshots to cloud
- [ ] Video recording
- [ ] Multiple screenshot formats (JPG, BMP, etc.)
- [ ] Adjustable notification duration

---

**For detailed documentation**, see: [SCREENSHOT_FUNCTIONALITY.md](SCREENSHOT_FUNCTIONALITY.md)
