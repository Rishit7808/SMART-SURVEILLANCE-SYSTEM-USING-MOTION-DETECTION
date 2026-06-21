import cv2
import datetime
import os
import winsound

# ==========================================
#       SMART SURVEILLANCE SYSTEM
# ==========================================

# --- Configuration ---
MOTION_THRESHOLD = 25        # Sensitivity for motion detection
MIN_CONTOUR_AREA = 3000      # Minimum area to count as motion
RECORD_ON_MOTION = True      # Record video when motion is detected
SAVE_SCREENSHOTS = True      # Save screenshots when motion is detected
ALERT_SOUND = True           # Play beep sound on motion detection
COOLDOWN_SECONDS = 3         # Seconds between alerts to avoid spam

# --- Setup directories ---
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "surveillance_output")
recordings_dir = os.path.join(output_dir, "recordings")
screenshots_dir = os.path.join(output_dir, "screenshots")
log_file = os.path.join(output_dir, "motion_log.txt")

os.makedirs(recordings_dir, exist_ok=True)
os.makedirs(screenshots_dir, exist_ok=True)

# --- Start webcam ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20

print("=" * 50)
print("   SMART SURVEILLANCE SYSTEM - ACTIVE")
print("=" * 50)
print(f"  Resolution : {frame_width}x{frame_height}")
print(f"  Motion Threshold : {MOTION_THRESHOLD}")
print(f"  Recording : {'ON' if RECORD_ON_MOTION else 'OFF'}")
print(f"  Screenshots : {'ON' if SAVE_SCREENSHOTS else 'OFF'}")
print(f"  Alert Sound : {'ON' if ALERT_SOUND else 'OFF'}")
print("=" * 50)
print("  Press 'q' to quit")
print("  Press 'r' to toggle recording")
print("  Press 's' to take manual screenshot")
print("=" * 50)

# --- State variables ---
ret, frame1 = cap.read()
ret, frame2 = cap.read()

motion_detected = False
recording = False
video_writer = None
last_alert_time = datetime.datetime.now() - datetime.timedelta(seconds=COOLDOWN_SECONDS + 1)
motion_count = 0
start_time = datetime.datetime.now()


def log_motion_event(event_type, details=""):
    """Log motion events to a text file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event_type}: {details}\n"
    with open(log_file, "a") as f:
        f.write(log_entry)
    print(f"  LOG: {log_entry.strip()}")


def start_recording():
    """Start recording video to a file."""
    global video_writer, recording
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(recordings_dir, f"recording_{timestamp}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
    recording = True
    log_motion_event("RECORDING STARTED", filename)
    return filename


def stop_recording():
    """Stop the current recording."""
    global video_writer, recording
    if video_writer is not None:
        video_writer.release()
        video_writer = None
    recording = False
    log_motion_event("RECORDING STOPPED")


def save_screenshot(frame):
    """Save a screenshot of the current frame."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(screenshots_dir, f"motion_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    log_motion_event("SCREENSHOT SAVED", filename)


def draw_dashboard(frame, motion_detected, motion_count, recording):
    """Draw an information dashboard overlay on the frame."""
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    uptime = str(now - start_time).split('.')[0]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame_width, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Title and timestamp
    cv2.putText(frame, "SMART SURVEILLANCE SYSTEM", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, timestamp_str, (frame_width - 260, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Status indicators
    cv2.putText(frame, f"Uptime: {uptime}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(frame, f"Motions: {motion_count}", (250, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Recording indicator
    if recording:
        cv2.circle(frame, (frame_width - 30, 55), 8, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (frame_width - 70, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Motion status bar at bottom
    if motion_detected:
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (0, frame_height - 40), (frame_width, frame_height), (0, 0, 200), -1)
        cv2.addWeighted(overlay2, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "!! MOTION DETECTED !!", (frame_width // 2 - 150, frame_height - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    else:
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (0, frame_height - 40), (frame_width, frame_height), (0, 120, 0), -1)
        cv2.addWeighted(overlay2, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "All Clear - Monitoring...", (frame_width // 2 - 140, frame_height - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    return frame


# --- Log system start ---
log_motion_event("SYSTEM STARTED", f"Resolution: {frame_width}x{frame_height}")

# ==========================================
#            MAIN LOOP
# ==========================================
while cap.isOpened():
    # Calculate difference between consecutive frames
    diff = cv2.absdiff(frame1, frame2)

    # Convert to grayscale
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply threshold to get binary image
    _, thresh = cv2.threshold(blur, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)

    # Dilate the threshold image to fill in gaps
    dilated = cv2.dilate(thresh, None, iterations=3)

    # Find contours (areas of motion)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    motion_in_frame = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_CONTOUR_AREA:
            continue

        motion_in_frame = True

        # Draw bounding rectangle around motion
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Label the motion area with its size
        cv2.putText(frame1, f"Motion ({area})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Handle motion events
    now = datetime.datetime.now()
    if motion_in_frame:
        motion_detected = True
        time_since_last_alert = (now - last_alert_time).total_seconds()

        if time_since_last_alert > COOLDOWN_SECONDS:
            motion_count += 1
            last_alert_time = now
            log_motion_event("MOTION DETECTED", f"Event #{motion_count}")

            # Play alert sound
            if ALERT_SOUND:
                try:
                    winsound.Beep(1000, 200)
                except:
                    pass

            # Save screenshot
            if SAVE_SCREENSHOTS:
                save_screenshot(frame1)

            # Start recording if enabled and not already recording
            if RECORD_ON_MOTION and not recording:
                start_recording()
    else:
        motion_detected = False
        # Stop recording after motion stops
        if recording:
            stop_recording()

    # Draw dashboard overlay
    display_frame = draw_dashboard(frame1.copy(), motion_detected, motion_count, recording)

    # Write frame to video if recording
    if recording and video_writer is not None:
        video_writer.write(frame1)

    # Show the surveillance feed
    cv2.imshow("Smart Surveillance System", display_frame)

    # Show the motion detection mask (optional debug view)
    cv2.imshow("Motion Mask", dilated)

    # Update frames
    frame1 = frame2
    ret, frame2 = cap.read()

    if not ret:
        print("Error: Lost connection to webcam.")
        break

    # Keyboard controls
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif key == ord('r'):  # Toggle recording
        if recording:
            stop_recording()
        else:
            start_recording()
    elif key == ord('s'):  # Manual screenshot
        save_screenshot(frame1)

# ==========================================
#            CLEANUP
# ==========================================
if recording:
    stop_recording()

log_motion_event("SYSTEM STOPPED", f"Total motions detected: {motion_count}")

cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 50)
print("   SURVEILLANCE SYSTEM - SHUT DOWN")
print(f"   Total motion events: {motion_count}")
print(f"   Logs saved to: {log_file}")
print(f"   Recordings: {recordings_dir}")
print(f"   Screenshots: {screenshots_dir}")
print("=" * 50)