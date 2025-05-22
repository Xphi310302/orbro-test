from pathlib import Path
from typing import List, Tuple
import shutil
import asyncio
from PIL import Image, ImageDraw

# Mock classes for testing
TARGET_CLASSES = {2: "car", 5: "bus", 7: "truck"}


def detect_vehicles(model, image_path: str | Path) -> Tuple[int, List[List[int]], Image.Image]:
    """
    Detect vehicles in an image using YOLOv8n.

    Args:
        model: YOLO model instance
        image_path: Path to the image file

    Returns:
        Tuple containing:
        - Total count of detected vehicles
        - List of bounding boxes [x1, y1, x2, y2]
        - Annotated image as numpy array
    """
    # Read image
    try:
        image = Image.open(str(image_path))
    except Exception as e:
        raise ValueError(f"Could not read image at {image_path}: {e}")

    # Run inference
    results = model(image, conf=0.25)[0]  # Confidence threshold of 0.25

    total_count = 0
    boxes = []

    # Process detections
    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, class_id = r

        # Check if detected class is one we're interested in
        if int(class_id) in TARGET_CLASSES:
            total_count += 1
            boxes.append([int(x1), int(y1), int(x2), int(y2)])

            # Draw bounding box
            draw = ImageDraw.Draw(image)
            draw.rectangle(
                [(int(x1), int(y1)), (int(x2), int(y2))],
                outline=(0, 255, 0),  # Green color
                width=2,  # Line thickness
            )

            # Add label
            label = f"{TARGET_CLASSES[int(class_id)]} {conf:.2f}"
            draw.text(
                (int(x1), int(y1 - 10)),
                label,
                fill=(0, 255, 0),  # Green color
            )

    return total_count, boxes, image


async def process_image_mock(
    input_path: str | Path, output_path: str | Path
) -> Tuple[int, List[List[int]]]:
    """
    Mock version of process_image for testing.
    Simulates detection by copying the input image and returning mock data.
    """
    # Simulate processing time
    await asyncio.sleep(2)

    # Copy the original image as the result
    shutil.copy(str(input_path), str(output_path))

    # Return mock data
    mock_count = 3  # Pretend we found 3 vehicles
    mock_boxes = [
        [100, 100, 200, 200],  # Pretend car
        [300, 300, 400, 400],  # Pretend bus
        [500, 500, 600, 600],  # Pretend truck
    ]

    return mock_count, mock_boxes


# Set this to True to use real detection, False to use mock
USE_REAL_DETECTION = False


async def process_image(
    input_path: str | Path, output_path: str | Path
) -> Tuple[int, List[List[int]]]:
    """
    Process an image and save the annotated version.
    Uses either real or mock detection based on USE_REAL_DETECTION flag.
    """
    if USE_REAL_DETECTION:
        # Import YOLO only if we're using real detection
        from ultralytics import YOLO

        model = YOLO("yolov8n.pt")
        count, boxes, annotated_image = detect_vehicles(model, input_path)
        annotated_image.save(str(output_path))
        return count, boxes
    else:
        return await process_image_mock(input_path, output_path)
