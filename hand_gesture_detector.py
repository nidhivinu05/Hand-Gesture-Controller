"""
Hand Gesture Detection using OpenCV and MediaPipe
This application detects and visualizes hand landmarks in real-time from webcam feed.
"""

import cv2
import mediapipe as mp
import time
import os
from datetime import datetime
import pyautogui

try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    NOTIFICATION_AVAILABLE = True
except Exception as e:
    toaster = None
    NOTIFICATION_AVAILABLE = False
    print(f"Desktop notification support unavailable: {e}")
# ============================================================================
# FINGER DETECTION LOGIC
# ============================================================================
# Hand landmarks reference:
# - Finger tip indices: [4, 8, 12, 16, 20] for thumb, index, middle, ring, pinky
# - Finger PIP (middle) joint indices: [3, 6, 10, 14, 18]
# - These are used to determine if a finger is raised or folded

def is_finger_raised(landmarks, tip_index, pip_index):
    """
    Determine if a finger is raised or folded based on landmark positions.
    
    A finger is considered raised if its tip is above (lower y-value) its PIP joint.
    In image coordinates, y increases downward, so smaller y = higher on screen.
    
    Args:
        landmarks: Hand landmarks from MediaPipe
        tip_index: Index of the fingertip landmark
        pip_index: Index of the PIP (middle) joint landmark
    
    Returns:
        bool: True if finger is raised, False if folded
    """
    # Get the y-coordinates of the tip and PIP joint
    tip_y = landmarks[tip_index].y
    pip_y = landmarks[pip_index].y
    
    # If tip is above PIP (smaller y value), finger is raised
    return tip_y < pip_y


def is_thumb_raised(landmarks):
    """
    Determine if the thumb is raised or folded.
    
    The thumb is detected differently from other fingers because it can move
    horizontally, vertically, or diagonally depending on wrist rotation. This
    uses multiple thumb and palm landmarks instead of one x-coordinate check.
    
    Args:
        landmarks: Hand landmarks from MediaPipe
    
    Returns:
        bool: True if thumb is raised, False if folded
    """
    def distance(point_a, point_b):
        return ((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2) ** 0.5

    wrist = landmarks[0]
    thumb_mcp = landmarks[2]
    thumb_ip = landmarks[3]
    thumb_tip = landmarks[4]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]
    pinky_mcp = landmarks[17]

    palm_center = type("Point", (), {
        "x": (wrist.x + index_mcp.x + pinky_mcp.x) / 3,
        "y": (wrist.y + index_mcp.y + pinky_mcp.y) / 3
    })()
    hand_scale = max(distance(wrist, middle_mcp), 0.001)

    tip_to_palm = distance(thumb_tip, palm_center)
    ip_to_palm = distance(thumb_ip, palm_center)
    tip_to_wrist = distance(thumb_tip, wrist)
    ip_to_wrist = distance(thumb_ip, wrist)
    tip_to_index = distance(thumb_tip, index_mcp)
    ip_to_index = distance(thumb_ip, index_mcp)
    thumb_extension = distance(thumb_tip, thumb_mcp)

    tucked_thumb = (tip_to_index < 0.45 * hand_scale and
                    tip_to_palm < ip_to_palm + 0.04 * hand_scale)

    extension_score = 0
    if tip_to_palm > ip_to_palm + 0.10 * hand_scale:
        extension_score += 1
    if tip_to_wrist > ip_to_wrist + 0.08 * hand_scale:
        extension_score += 1
    if tip_to_index > ip_to_index + 0.06 * hand_scale:
        extension_score += 1
    if thumb_extension > 0.35 * hand_scale:
        extension_score += 1

    return extension_score >= 3 and not tucked_thumb


def detect_raised_fingers(hand_landmarks):
    """
    Detect which fingers are raised in the given hand.
    
    Args:
        hand_landmarks: Hand landmarks from MediaPipe results
    
    Returns:
        dict: Dictionary containing status of each finger
              Keys: 'thumb', 'index', 'middle', 'ring', 'pinky'
              Values: True if raised, False if folded
    """
    if not hand_landmarks:
        return None
    
    fingers_status = {
        'thumb': is_thumb_raised(hand_landmarks.landmark),
        'index': is_finger_raised(hand_landmarks.landmark, 8, 6),    # tip=8, pip=6
        'middle': is_finger_raised(hand_landmarks.landmark, 12, 10),  # tip=12, pip=10
        'ring': is_finger_raised(hand_landmarks.landmark, 16, 14),    # tip=16, pip=14
        'pinky': is_finger_raised(hand_landmarks.landmark, 20, 18)    # tip=20, pip=18
    }
    
    return fingers_status


def count_raised_fingers(fingers_status):
    """
    Count the total number of raised fingers.
    
    Args:
        fingers_status: Dictionary containing status of each finger
    
    Returns:
        int: Total number of raised fingers
    """
    if not fingers_status:
        return 0
    
    return sum(1 for finger_raised in fingers_status.values() if finger_raised)


def draw_finger_status(frame, fingers_status, raised_count):
    """
    Display finger status and raised finger count on the frame.
    
    Args:
        frame: The video frame to draw on
        fingers_status: Dictionary containing status of each finger
        raised_count: Total number of raised fingers
    """
    if not fingers_status:
        return
    
    # Y-coordinate for starting text display (below FPS counter)
    y_offset = 70
    line_height = 25
    
    # Display each finger's status
    for finger_name, is_raised in fingers_status.items():
        status_text = "RAISED" if is_raised else "FOLDED"
        color = (0, 255, 0) if is_raised else (0, 0, 255)  # Green if raised, Red if folded
        
        # Format: "Thumb: RAISED" or "Index: FOLDED"
        text = f"{finger_name.capitalize()}: {status_text}"
        cv2.putText(
            frame,
            text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )
        y_offset += line_height
    
    # Display total raised fingers count at the bottom of finger status
    y_offset += 10
    total_text = f"Total Raised: {raised_count}"
    cv2.putText(
        frame,
        total_text,
        (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),  # Cyan color for emphasis
        2
    )


# ============================================================================
# GESTURE RECOGNITION LOGIC
# ============================================================================
# The gesture recognition system uses finger status to identify hand gestures.
# Each gesture has a unique combination of raised and folded fingers.

def is_open_palm(fingers_status):
    """
    Detect Open Palm gesture: All five fingers raised.
    
    Pattern: All fingers are in raised position
    Use case: Stop signal, greeting
    
    Args:
        fingers_status: Dictionary containing finger statuses
    
    Returns:
        bool: True if open palm detected, False otherwise
    """
    if not fingers_status:
        return False
    
    return (fingers_status['thumb'] and
            fingers_status['index'] and
            fingers_status['middle'] and
            fingers_status['ring'] and
            fingers_status['pinky'])


def is_fist(fingers_status):
    """
    Detect Fist gesture: No fingers raised.
    
    Pattern: All fingers are folded
    Use case: Closed fist, agreement signal
    
    Args:
        fingers_status: Dictionary containing finger statuses
    
    Returns:
        bool: True if fist detected, False otherwise
    """
    if not fingers_status:
        return False
    
    return (not fingers_status['thumb'] and
            not fingers_status['index'] and
            not fingers_status['middle'] and
            not fingers_status['ring'] and
            not fingers_status['pinky'])


def is_thumbs_up(fingers_status):
    """
    Detect Thumbs Up gesture: Only thumb raised.
    
    Pattern: Thumb raised, all other fingers folded
    Use case: Approval, positive acknowledgment
    
    Args:
        fingers_status: Dictionary containing finger statuses
    
    Returns:
        bool: True if thumbs up detected, False otherwise
    """
    if not fingers_status:
        return False
    
    return (fingers_status['thumb'] and
            not fingers_status['index'] and
            not fingers_status['middle'] and
            not fingers_status['ring'] and
            not fingers_status['pinky'])


def is_thumb_only_pose(fingers_status, landmarks=None):
    """
    Detect whether the hand is making a thumb-only pose.

    This reuses the existing finger-status architecture and adds an optional
    landmark distance check so Thumbs Down can be detected even when the thumb
    is pointing vertically instead of horizontally.
    """
    if not fingers_status:
        return False

    other_fingers_folded = (not fingers_status['index'] and
                            not fingers_status['middle'] and
                            not fingers_status['ring'] and
                            not fingers_status['pinky'])

    if not other_fingers_folded:
        return False

    if landmarks is None:
        return fingers_status['thumb']

    wrist = landmarks[0]
    thumb_mcp = landmarks[2]
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]

    tip_distance = ((thumb_tip.x - wrist.x) ** 2 + (thumb_tip.y - wrist.y) ** 2) ** 0.5
    ip_distance = ((thumb_ip.x - wrist.x) ** 2 + (thumb_ip.y - wrist.y) ** 2) ** 0.5
    thumb_extension = ((thumb_tip.x - thumb_mcp.x) ** 2 + (thumb_tip.y - thumb_mcp.y) ** 2) ** 0.5

    return fingers_status['thumb'] or (tip_distance > ip_distance + 0.02 and
                                       thumb_extension > 0.08)


def is_thumbs_down(fingers_status, landmarks=None):
    """
    Detect Thumbs Down gesture: Thumb-only pose with thumb pointing down.

    Pattern: Thumb extended downward, all other fingers folded
    Use case: Negative acknowledgment

    Args:
        fingers_status: Dictionary containing finger statuses
        landmarks: Optional MediaPipe hand landmarks for thumb direction

    Returns:
        bool: True if thumbs down detected, False otherwise
    """
    if not is_thumb_only_pose(fingers_status, landmarks):
        return False

    if landmarks is None:
        return False

    thumb_cmc = landmarks[1]
    thumb_mcp = landmarks[2]
    thumb_ip = landmarks[3]
    thumb_tip = landmarks[4]

    thumb_down_score = 0

    if thumb_tip.y > thumb_ip.y + 0.02:
        thumb_down_score += 1
    if thumb_tip.y > thumb_mcp.y + 0.04:
        thumb_down_score += 1
    if thumb_tip.y > thumb_cmc.y + 0.03:
        thumb_down_score += 1
    if thumb_ip.y > thumb_mcp.y - 0.02:
        thumb_down_score += 1

    thumb_vector_y = thumb_tip.y - thumb_mcp.y
    thumb_vector_x = abs(thumb_tip.x - thumb_mcp.x)
    allows_moderate_rotation = thumb_vector_y > 0.035 and thumb_vector_y > thumb_vector_x * 0.25

    if allows_moderate_rotation:
        thumb_down_score += 1

    return thumb_down_score >= 4


def is_peace_sign(fingers_status):
    """
    Detect Peace Sign gesture: Index and middle fingers raised.
    
    Pattern: Index and middle fingers raised, others folded
    Use case: Victory signal, peace gesture
    
    Args:
        fingers_status: Dictionary containing finger statuses
    
    Returns:
        bool: True if peace sign detected, False otherwise
    """
    if not fingers_status:
        return False
    
    return (not fingers_status['thumb'] and
            fingers_status['index'] and
            fingers_status['middle'] and
            not fingers_status['ring'] and
            not fingers_status['pinky'])


def is_rock_sign(fingers_status):
    """
    Detect Rock Sign gesture: Index and pinky fingers raised.
    
    Pattern: Index and pinky fingers raised, others folded
    Use case: Rock and roll gesture, devil horns
    
    Args:
        fingers_status: Dictionary containing finger statuses
    
    Returns:
        bool: True if rock sign detected, False otherwise
    """
    if not fingers_status:
        return False
    
    return (not fingers_status['thumb'] and
            fingers_status['index'] and
            not fingers_status['middle'] and
            not fingers_status['ring'] and
            fingers_status['pinky'])


def detect_gesture(fingers_status, landmarks=None):
    """
    Detect hand gesture from finger configuration.
    
    This function checks the finger status against known gesture patterns
    and returns the name of the recognized gesture. If no pattern matches,
    it returns "Unknown Gesture".
    
    Gesture Priority (checked in order):
    1. Open Palm - all five fingers raised
    2. Thumbs Down - thumb-only pose pointing down
    3. Fist - all fingers folded
    4. Thumbs Up - only thumb raised
    5. Peace Sign - index and middle raised
    6. Rock Sign - index and pinky raised
    
    Args:
        fingers_status: Dictionary containing finger statuses
        landmarks: Optional MediaPipe hand landmarks for orientation-aware gestures
    
    Returns:
        str: Name of the detected gesture or "Unknown Gesture"
    """
    if not fingers_status:
        return "Unknown Gesture"
    
    # Check gestures in priority order
    if is_open_palm(fingers_status):
        return "Open Palm"
    elif is_thumbs_down(fingers_status, landmarks):
        return "Thumbs Down"
    elif is_fist(fingers_status):
        return "Fist"
    elif is_thumbs_up(fingers_status):
        return "Thumbs Up"
    elif is_peace_sign(fingers_status):
        return "Peace Sign"
    elif is_rock_sign(fingers_status):
        return "Rock Sign"
    else:
        return "Unknown Gesture"


def draw_gesture_display(frame, gesture_name):
    """
    Display the detected gesture prominently on the frame.
    
    The gesture name is displayed in the top-right corner with a large font
    and a colored background for visibility.
    
    Args:
        frame: The video frame to draw on
        gesture_name: Name of the detected gesture
    """
    if not gesture_name:
        return
    
    # Define color based on gesture (for visual feedback)
    gesture_colors = {
        'Open Palm': (0, 255, 255),      # Cyan - stop/greeting
        'Fist': (0, 0, 255),              # Red - closed hand
        'Thumbs Up': (0, 255, 0),         # Green - positive
        'Thumbs Down': (0, 165, 255),      # Orange - negative
        'Peace Sign': (255, 0, 255),      # Magenta - victory
        'Rock Sign': (255, 0, 0),         # Blue - rock on
        'Unknown Gesture': (128, 128, 128) # Gray - unrecognized
    }
    
    color = gesture_colors.get(gesture_name, (128, 128, 128))
    
    # Position in top-right corner
    # Get text size to center it properly
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 3
    text_size = cv2.getTextSize(gesture_name, font, font_scale, thickness)[0]
    
    # Calculate position (top-right corner with padding)
    frame_height, frame_width = frame.shape[:2]
    x = frame_width - text_size[0] - 20
    y = 50
    
    # Draw a filled rectangle behind the text for better visibility
    cv2.rectangle(
        frame,
        (x - 10, y - 30),
        (frame_width - 10, y + 10),
        color,
        -1  # Filled rectangle
    )
    
    # Draw the gesture text
    cv2.putText(
        frame,
        gesture_name,
        (x, y),
        font,
        font_scale,
        (0, 0, 0),  # Black text
        thickness
    )


# ============================================================================
# GESTURE STABILITY AND CONFIRMATION LOGIC
# ============================================================================
# This section implements gesture stability to prevent rapid switching between
# gesture labels. A gesture is only confirmed when detected consistently for
# a minimum number of consecutive frames (default: 10 frames).

class GestureStabilizer:
    """
    Manages gesture detection stability and confirmation.
    
    Prevents rapid gesture label switching by requiring consistent detection
    over multiple frames. Only displays a gesture after it has been detected
    for a minimum consecutive frame count.
    """
    
    def __init__(self, confidence_frames=10, gesture_confidence_frames=None):
        """
        Initialize the gesture stabilizer.
        
        Args:
            confidence_frames: Number of consecutive frames required for gesture confirmation
            gesture_confidence_frames: Optional per-gesture confirmation thresholds
        """
        self.confidence_frames = confidence_frames
        self.gesture_confidence_frames = gesture_confidence_frames or {}
        self.current_gesture = "Unknown Gesture"
        self.confirmed_gesture = "Unknown Gesture"
        self.frame_count = 0

    def get_required_frames(self, gesture_name):
        """Get the confirmation threshold for the given gesture."""
        return self.gesture_confidence_frames.get(gesture_name, self.confidence_frames)
    
    def update(self, detected_gesture):
        """
        Update gesture stability counter based on new detection.
        
        If the detected gesture matches the current tracked gesture, increment
        the frame counter. If a different gesture is detected, reset the counter
        and start tracking the new gesture.
        
        When frame counter reaches confidence threshold, confirm the gesture.
        
        Args:
            detected_gesture: The gesture detected in current frame
        
        Returns:
            str: Confirmed gesture to display (or "Unknown Gesture" if not yet confirmed)
        """
        # Check if detected gesture is the same as current tracked gesture
        required_frames = self.get_required_frames(detected_gesture)
        if detected_gesture == self.current_gesture:
            # Increment frame counter for consistent detection
            self.frame_count += 1
            
            # Once we reach confidence threshold, confirm the gesture
            if self.frame_count >= required_frames:
                self.confirmed_gesture = detected_gesture
        else:
            # Gesture changed, reset tracking to new gesture
            self.current_gesture = detected_gesture
            self.frame_count = 1  # Start counting from 1 (current frame)
            required_frames = self.get_required_frames(self.current_gesture)
            
            # Only update confirmed gesture if we were detecting something stable
            # Otherwise keep the previous confirmed gesture for 1-2 frames of stability
            if self.frame_count < required_frames:
                # Gesture is in transition, potentially keep showing previous gesture
                # or show "Detecting..." - decided to keep previous for smooth UX
                pass
        
        return self.confirmed_gesture
    
    def get_confirmation_status(self):
        """
        Get the current confirmation status of the detected gesture.
        
        Useful for debugging or showing progress indicator.
        
        Returns:
            tuple: (confirmed_gesture, current_frame_count, progress_percentage)
        """
        required_frames = self.get_required_frames(self.current_gesture)
        progress = min(100, (self.frame_count / required_frames) * 100)
        return self.confirmed_gesture, self.frame_count, int(progress)
    
    def reset(self):
        """Reset the stabilizer to initial state."""
        self.current_gesture = "Unknown Gesture"
        self.confirmed_gesture = "Unknown Gesture"
        self.frame_count = 0


def draw_gesture_progress(frame, gesture_stabilizer):
    """
    Display gesture confirmation progress indicator on the frame.
    
    Shows the current detected gesture and a progress bar indicating
    how many frames have been accumulated toward confirmation (10 frames).
    Useful for user feedback during gesture detection.
    
    Args:
        frame: The video frame to draw on
        gesture_stabilizer: GestureStabilizer instance
    """
    confirmed, frame_count, progress = gesture_stabilizer.get_confirmation_status()
    current = gesture_stabilizer.current_gesture
    required_frames = gesture_stabilizer.get_required_frames(current)
    
    # Only show progress if we're not at a confirmed gesture or if we're detecting something new
    if current != "Unknown Gesture" and current != confirmed:
        # Position below gesture display
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        
        frame_height, frame_width = frame.shape[:2]
        x = frame_width - 250
        y = 80
        
        # Draw detecting text
        detecting_text = f"Detecting: {current} ({frame_count}/{required_frames})"
        cv2.putText(
            frame,
            detecting_text,
            (x, y),
            font,
            font_scale,
            (255, 255, 0),  # Cyan text
            thickness
        )
        
        # Draw progress bar
        bar_width = 150
        bar_height = 8
        bar_x = x
        bar_y = y + 15
        
        # Background bar (gray)
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (100, 100, 100),
            -1
        )
        
        # Progress fill (green)
        fill_width = int((progress / 100) * bar_width)
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + fill_width, bar_y + bar_height),
            (0, 255, 0),
            -1
        )


# ============================================================================
# SCREENSHOT FUNCTIONALITY
# ============================================================================
# Screenshot capture triggered by Peace Sign gesture with cooldown protection

def ensure_screenshots_folder():
    """
    Create the Screenshots folder if it doesn't exist.
    
    This function checks if a "Screenshots" directory exists in the current
    working directory. If not, it creates one. This is called once at startup.
    
    Returns:
        str: Path to the Screenshots folder
    """
    screenshots_folder = "Screenshots"
    
    try:
        # Check if folder exists, if not create it
        if not os.path.exists(screenshots_folder):
            os.makedirs(screenshots_folder)
            print(f"Created '{screenshots_folder}' folder")
    except Exception as e:
        print(f"Error creating Screenshots folder: {e}")
    
    return screenshots_folder


def save_screenshot(frame, screenshots_folder="Screenshots"):
    """
    Save a screenshot frame with timestamp in the filename.
    
    The screenshot is saved with a filename format: screenshot_YYYY-MM-DD_HH-MM-SS.png
    This allows multiple screenshots to be organized chronologically.
    
    Args:
        frame: The video frame to save
        screenshots_folder: Path to the folder where screenshots will be saved
    
    Returns:
        tuple: (success: bool, filename: str, error_message: str or None)
    """
    try:
        # Generate filename with current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_folder, filename)

        # Use PyAutoGUI to capture the full desktop screen at native resolution
        screenshot = pyautogui.screenshot()

        # Ensure folder exists
        if not os.path.exists(screenshots_folder):
            os.makedirs(screenshots_folder)

        # Save as lossless PNG with maximum quality (Pillow handles PNG lossless)
        screenshot.save(filepath, format='PNG')

        print(f"Screenshot saved: {filepath}")
        return True, filename, None

    except Exception as e:
        error_msg = f"Screenshot error: {str(e)}"
        print(error_msg)
        return False, "", error_msg


class ScreenshotManager:
    """
    Manages screenshot capture with cooldown to prevent accidental multiple captures.
    
    Implements a cooldown mechanism that prevents taking multiple screenshots
    within a short time period (default: 3 seconds). Useful for gesture-based
    triggering where the gesture might be held for multiple frames.
    """
    
    def __init__(self, cooldown_seconds=3.0):
        """
        Initialize the screenshot manager.
        
        Args:
            cooldown_seconds: Minimum time between screenshots (default: 3.0 seconds)
        """
        self.cooldown_seconds = cooldown_seconds
        self.last_screenshot_time = 0
        self.screenshot_taken_this_frame = False
    
    def can_take_screenshot(self):
        """
        Check if enough time has passed since the last screenshot.
        
        Returns:
            bool: True if cooldown has expired and screenshot can be taken
        """
        current_time = time.time()
        time_since_last = current_time - self.last_screenshot_time
        
        return time_since_last >= self.cooldown_seconds
    
    def take_screenshot(self, frame, screenshots_folder="Screenshots"):
        """
        Attempt to take a screenshot if cooldown allows.
        
        Args:
            frame: The video frame to save
            screenshots_folder: Path to the screenshots folder
        
        Returns:
            tuple: (screenshot_taken: bool, filename: str, error: str or None)
        """
        if not self.can_take_screenshot():
            # Cooldown still active
            return False, "", "Cooldown active"
        
        # Take the screenshot
        success, filename, error = save_screenshot(frame, screenshots_folder)
        
        if success:
            # Update last screenshot time
            self.last_screenshot_time = time.time()
            self.screenshot_taken_this_frame = True
        
        return success, filename, error
    
    def get_cooldown_remaining(self):
        """
        Get remaining cooldown time in seconds.
        
        Returns:
            float: Remaining cooldown time (0 if ready)
        """
        current_time = time.time()
        time_since_last = current_time - self.last_screenshot_time
        remaining = max(0, self.cooldown_seconds - time_since_last)
        return remaining


def show_desktop_notification(title, message, duration=3):
    """
    Display a Windows toast notification using win10toast.

    Args:
        title: Notification title string
        message: Notification message string
        duration: How long the notification stays visible in seconds

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if not NOTIFICATION_AVAILABLE:
        return False, "Notifications unavailable"

    try:
        toaster.show_toast(
            title=title,
            msg=message,
            duration=duration,
            threaded=True
        )
        return True, None
    except Exception as e:
        error_msg = f"Notification error: {e}"
        print(error_msg)
        return False, error_msg


# ============================================================================
# WINDOWS SYSTEM VOLUME CONTROL
# ============================================================================
# Uses Windows media volume keys so the native Windows volume flyout appears.

def increase_volume():
    """Increase the actual Windows system volume."""
    previous_failsafe = pyautogui.FAILSAFE
    try:
        pyautogui.FAILSAFE = False
        pyautogui.press("volumeup")
    finally:
        pyautogui.FAILSAFE = previous_failsafe


def decrease_volume():
    """Decrease the actual Windows system volume."""
    previous_failsafe = pyautogui.FAILSAFE
    try:
        pyautogui.FAILSAFE = False
        pyautogui.press("volumedown")
    finally:
        pyautogui.FAILSAFE = previous_failsafe


def toggle_play_pause():
    """Toggle playback for media apps that support Windows media controls."""
    previous_failsafe = pyautogui.FAILSAFE
    try:
        pyautogui.FAILSAFE = False
        pyautogui.press("playpause")
    finally:
        pyautogui.FAILSAFE = previous_failsafe


# ============================================================================
# MEDIAPIPE INITIALIZATION
# ============================================================================
# Initialize MediaPipe Hands solution for hand detection and landmark tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Create a Hands object for hand detection
# max_num_hands: Detect only 1 hand
# model_complexity: 1 for better accuracy, 0 for better performance
# min_detection_confidence: Minimum confidence threshold for detection
# min_tracking_confidence: Minimum confidence threshold for tracking
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================================
# WEBCAM INITIALIZATION
# ============================================================================
# Open the default webcam (0 is typically the default camera)
cap = cv2.VideoCapture(0)

# Verify that the webcam opened successfully
if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

# Get webcam properties for optimal display
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# ============================================================================
# MAIN PROCESSING LOOP
# ============================================================================
# Variables for FPS calculation
prev_time = 0
current_time = 0

# Initialize gesture stabilizer to require consistent detection for 10 frames
gesture_stabilizer = GestureStabilizer(
    confidence_frames=10,
    gesture_confidence_frames={"Thumbs Down": 5}
)

# ============================================================================
# SCREENSHOT AND GESTURE ACTION SETUP
# ============================================================================
# Create Screenshots folder and initialize screenshot manager
screenshots_folder = ensure_screenshots_folder()
screenshot_manager = ScreenshotManager(cooldown_seconds=3.0)

# Volume gesture cooldown setup
volume_cooldown_seconds = 0.3
last_volume_change_time = 0

# Media play/pause cooldown setup
media_cooldown_seconds = 2.0
last_media_toggle_time = 0

while True:
    # Read frame from webcam
    success, frame = cap.read()
    
    # Check if frame was captured successfully
    if not success:
        print("Error: Failed to read from webcam")
        break
    
    # Flip the frame horizontally for a mirror-like view
    frame = cv2.flip(frame, 1)
    
    # Get frame height and width for later use
    h, w, c = frame.shape
    
    # Convert BGR frame to RGB (MediaPipe requires RGB format)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame to detect hand landmarks
    # This returns results containing hand landmarks and handedness information
    results = hands.process(frame_rgb)
    
    # ========================================================================
    # DRAW HAND LANDMARKS AND CONNECTIONS
    # ========================================================================
    fingers_status = None
    raised_count = 0
    detected_gesture = "Unknown Gesture"
    
    if results.multi_hand_landmarks:
        # Iterate through each detected hand (we detect max 1 hand)
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw all 21 hand landmarks on the frame
            # This draws circles at each landmark position
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # ================================================================
            # DETECT FINGER STATUS
            # ================================================================
            # Use our finger detection functions to determine which fingers are raised
            fingers_status = detect_raised_fingers(hand_landmarks)
            raised_count = count_raised_fingers(fingers_status)
            
            # ================================================================
            # RECOGNIZE GESTURE
            # ================================================================
            # Use finger status to identify the hand gesture
            detected_gesture = detect_gesture(fingers_status, hand_landmarks.landmark)
    
    # ========================================================================
    # STABILIZE GESTURE DETECTION
    # ========================================================================
    # Use the gesture stabilizer to confirm gestures only after consistent
    # detection across multiple frames (default: 10 frames)
    # This prevents rapid switching between different gesture labels
    confirmed_gesture = gesture_stabilizer.update(detected_gesture)
    
    # ========================================================================
    # GESTURE-BASED ACTIONS - SCREENSHOT TRIGGER
    # ========================================================================
    # Check if Peace Sign gesture is detected and confirmed
    # If so, attempt to take a screenshot (with cooldown protection)
    if confirmed_gesture == "Peace Sign":
        success, filename, error = screenshot_manager.take_screenshot(frame, screenshots_folder)

        if success:
            notification_title = "Screenshot Saved"
            notification_message = filename if filename else "Screenshot saved successfully."
            notify_success, notify_error = show_desktop_notification(
                notification_title,
                notification_message,
                duration=3
            )
            if not notify_success:
                print(f"Notification error: {notify_error}")
            print(f"Screenshot captured: {filename}")
        elif error != "Cooldown active":
            # Some other error occurred (not just cooldown)
            print(f"Screenshot error: {error}")

    # ========================================================================
    # GESTURE-BASED ACTIONS - VOLUME CONTROL
    # ========================================================================
    # Thumbs Up and Thumbs Down send native Windows volume key events.
    if confirmed_gesture in ("Thumbs Up", "Thumbs Down"):
        current_time_for_volume = time.time()
        if current_time_for_volume - last_volume_change_time >= volume_cooldown_seconds:
            if confirmed_gesture == "Thumbs Up":
                increase_volume()
                print("Volume increased")
            elif confirmed_gesture == "Thumbs Down":
                decrease_volume()
                print("Volume decreased")
            last_volume_change_time = current_time_for_volume

    # ========================================================================
    # GESTURE-BASED ACTIONS - MEDIA PLAY/PAUSE
    # ========================================================================
    # Fist sends the native Windows Play/Pause media key event.
    if confirmed_gesture == "Fist":
        current_time_for_media = time.time()
        if current_time_for_media - last_media_toggle_time >= media_cooldown_seconds:
            toggle_play_pause()
            print("Media play/pause toggled")
            last_media_toggle_time = current_time_for_media
    
    # ========================================================================
    # CALCULATE AND DISPLAY FPS
    # ========================================================================
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
    prev_time = current_time
    
    # Display FPS in the top-left corner
    # Font: cv2.FONT_HERSHEY_SIMPLEX
    # Font scale: 0.7
    # Color: Green (0, 255, 0) in BGR format
    # Thickness: 2
    cv2.putText(
        frame,
        f"FPS: {fps:.2f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
    # ========================================================================
    # DISPLAY FINGER STATUS
    # ========================================================================
    # Show the status of each finger and total raised fingers
    draw_finger_status(frame, fingers_status, raised_count)
    
    # ========================================================================
    # DISPLAY RECOGNIZED GESTURE
    # ========================================================================
    # Show the confirmed (stabilized) gesture in a prominent position
    # Only displays after consistent detection for 10+ frames
    draw_gesture_display(frame, confirmed_gesture)
    
    # Display gesture confirmation progress for user feedback
    draw_gesture_progress(frame, gesture_stabilizer)
    
    # ========================================================================
    # DISPLAY FRAME AND HANDLE USER INPUT
    # ========================================================================
    # Display the frame in a window titled "GestureOS"
    cv2.imshow("GestureOS", frame)
    
    # Wait for 1ms and check if 'q' key is pressed
    # If 'q' is pressed, exit the loop and close the application
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Exiting application...")
        break


# ============================================================================
# CLEANUP AND RELEASE RESOURCES
# ============================================================================
# Release the webcam
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()

# Release MediaPipe resources
hands.close()

print("Application closed successfully")
