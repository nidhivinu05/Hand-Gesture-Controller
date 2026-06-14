# Hand Gesture Detection Application

A real-time hand gesture detection application using OpenCV and MediaPipe that detects and visualizes hand landmarks from your webcam.

## Features

✅ Real-time hand detection using MediaPipe Hands  
✅ Draws all 21 hand landmarks with connections  
✅ Displays FPS (frames per second) in real-time  
✅ Mirror-like view (horizontally flipped)  
✅ Clean, well-commented code  
✅ Easy exit with 'q' key press  

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- A working webcam

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install opencv-python mediapipe
```

### 2. Run the Application

```bash
python hand_gesture_detector.py
```

## Usage

1. **Start the Application**: Run the Python script
2. **Point Your Hand at the Webcam**: The application will automatically detect your hand
3. **View the Output**: 
   - See your hand landmarks (21 points) connected with lines
   - Monitor real-time FPS in the top-left corner
4. **Exit**: Press the **'q'** key to close the application

## Hand Landmarks

The application detects 21 hand landmarks:

- **0**: Wrist
- **1-4**: Thumb (base to tip)
- **5-8**: Index finger (base to tip)
- **9-12**: Middle finger (base to tip)
- **13-16**: Ring finger (base to tip)
- **17-20**: Pinky finger (base to tip)

These landmarks are connected with lines showing the hand's structure and joints.

## Code Structure

The application is organized into clear sections with detailed comments:

1. **MediaPipe Initialization**: Sets up hand detection
2. **Webcam Initialization**: Opens the default camera
3. **Main Processing Loop**: Captures frames, detects hands, and displays results
4. **Landmark Drawing**: Visualizes hand points and connections
5. **FPS Calculation**: Tracks real-time performance
6. **Cleanup**: Properly releases resources

## Troubleshooting

**Issue**: Application doesn't detect hands
- Ensure adequate lighting in your environment
- Keep your hand fully visible in the frame
- Try adjusting the `min_detection_confidence` parameter (range: 0.0-1.0)

**Issue**: Low FPS performance
- Reduce camera resolution
- Change `model_complexity` to 0 for faster processing (less accurate)
- Close other applications using system resources

**Issue**: Cannot open webcam
- Check that no other application is using your webcam
- Verify your webcam is properly connected
- Check camera permissions in your OS settings

## Performance Tips

- The application uses MediaPipe's optimized hand tracking for smooth performance
- FPS typically ranges from 25-60+ depending on your hardware
- Single-hand detection for optimal performance

## License

This project is provided as-is for educational purposes.
