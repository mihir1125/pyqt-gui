import cv2
import numpy as np
import tensorflow as tf
from official.projects.movinet.modeling import movinet
from official.projects.movinet.modeling import movinet_model
from tensorflow.keras.models import load_model

# Load your trained model
# model = load_model('/mnt/c/Users/mihir/Desktop/temp/movie_net_model-20240305T054146Z-001/movie_net_model/')
model = load_model('movie_net_model')

print("Warming up model")
model.predict(np.zeros(shape=(1, 60, 224, 224, 3)))
print("Warmed up")

def format_frames(frame, output_size):
    """
    Pad, resize, and normalize an image from a video.

    Args:
        frame: Image that needs to be resized, padded, and normalized.
        output_size: Pixel size of the output frame image.

    Return:
        Formatted and normalized frame with padding of specified output size.
    """
    # Convert the image to float32 format
    frame = tf.image.convert_image_dtype(frame, tf.float32)
    
    # Resize the image with padding to the specified output size
    frame = tf.image.resize_with_pad(frame, *output_size)
    
    # Normalize the pixel values to be in the range [0, 1]
    frame = frame / 255.0
    
    return frame

def frames_from_video_file(video_path, n_frames, output_size = (224,224), frame_step = 15):
    """
    Creates frames from each video file present for each category.

    Args:
        video_path: File path to the video.
        n_frames: Number of frames to be created per video file.
        output_size: Pixel size of the output frame image.

    Return:
        An NumPy array of frames in the shape of (n_frames, height, width, channels).
    """
    # Read each video frame by frame
    result = []
    src = cv2.VideoCapture(str(video_path))

    video_length = src.get(cv2.CAP_PROP_FRAME_COUNT)

    need_length = 1 + (n_frames - 1) * frame_step

    if need_length > video_length:
        start = 0
    else:
        max_start = video_length - need_length
        start = random.randint(0, max_start + 1)

    src.set(cv2.CAP_PROP_POS_FRAMES, start)
    # ret is a boolean indicating whether read was successful, frame is the image itself
    ret, frame = src.read()
    result.append(format_frames(frame, output_size))

    for _ in range(n_frames - 1):
        for _ in range(frame_step):
            ret, frame = src.read()
        if ret:
            frame = format_frames(frame, output_size)
            result.append(frame)
        else:
            result.append(np.zeros_like(result[0]))
    src.release()
    result = np.array(result)[..., [2, 1, 0]]

    return result

def process(path):
    frames=frames_from_video_file(path,60)
    x=np.expand_dims(frames,axis=0)
    return x

def processBatch(batch):
    frame_step = 15
    
    processed_batch = [batch[i] for i in range(0, len(batch), frame_step)]    
    return model.predict(np.expand_dims(processed_batch, axis=0))