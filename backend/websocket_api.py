import asyncio
import io
import logging
import threading
from collections import deque

import soundfile as sf
import torch
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils import BatchedInferenceWithThreshold, id2label

# Use the same logger as FastAPI
logger = logging.getLogger("uvicorn")

app = FastAPI()

MODEL_NAME = "7wolf/wav2vec2-base-gender-classification"

# Load configuration from YAML file
with open("config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Loading configuration
CHUNK_SIZE = config["inference"]["chunk_size"]  # Process 50ms chunks
SAMPLE_RATE = config["inference"]["sample_rate"]  # 16kHz sample rate (common for speech processing)
WINDOW_SIZE = config["inference"]["window_size"]  # Seconds
OVERLAP_RATIO = config["inference"]["overlap_ratio"]
THRESHOLD = config["model"]["rms_threshold"]

# Inferred configuration
WINDOW_SIZE_IN_CHUNKS = int(WINDOW_SIZE / CHUNK_SIZE)

logger.info(f"Each chunk of audio will be {CHUNK_SIZE} seconds long.")
logger.info(f"The window size is {WINDOW_SIZE} seconds, which is {WINDOW_SIZE_IN_CHUNKS} chunks.")

# Load the model
logger.info(f"Loading model {MODEL_NAME} with threshold {THRESHOLD}...")
model = BatchedInferenceWithThreshold(MODEL_NAME, threshold=THRESHOLD)

# === CONFIGURATION ===

# === DEQUE FOR PROCESSING (used as our audio queue) ===
audio_queue = deque(maxlen=100)

def process_audio(websocket, loop):
    """
    Background thread for processing audio chunks.

    This function continuously processes audio chunks from the audio queue.
    When enough chunks are available, it forms a window of audio data, 
    performs inference using the model, and sends the predicted class 
    back to the client via the websocket.

    Args:
        websocket (WebSocket): The websocket connection to the client.
        loop (asyncio.AbstractEventLoop): The event loop for running asynchronous tasks.
    """
    while True:
        if len(audio_queue) > WINDOW_SIZE_IN_CHUNKS:
            audio_window = torch.stack(list(audio_queue)[:WINDOW_SIZE_IN_CHUNKS], dim=0)
            for _ in range(int(WINDOW_SIZE_IN_CHUNKS * OVERLAP_RATIO)):
                audio_queue.popleft()
        else:
            continue

        with torch.no_grad():
            predicted_class = model(audio_window)
            asyncio.run_coroutine_threadsafe(
                websocket.send_json(
                    {
                        "class": id2label(predicted_class),
                    }
                ),
                loop,
            )

@app.websocket("/audio")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles real-time audio streaming from clients.

    This endpoint accepts a websocket connection from a client, starts a 
    background thread to process incoming audio data, and continuously 
    receives audio bytes from the client. The audio data is decoded and 
    added to the processing queue.

    Args:
        websocket (WebSocket): The websocket connection to the client.
    """
    await websocket.accept()
    loop = asyncio.get_running_loop()

    # Start processing thread with the websocket and current event loop.
    processing_thread = threading.Thread(target=process_audio, args=(websocket, loop), daemon=True)
    processing_thread.start()

    try:
        while True:
            message = await websocket.receive_bytes()

            try:
                # Decode the audio stream into a numpy array.
                audio_array, _ = sf.read(io.BytesIO(message), dtype="float32")

            except sf.LibsndfileError as e:
                logger.error(f"Error decoding audio stream: {e}")
                continue

            # Append the decoded audio array into the processing deque.
            audio_queue.append(torch.from_numpy(audio_array))

    except WebSocketDisconnect:
        logger.info("Client disconnected.")

@app.get("/healthcheck")
async def healthcheck():
    """
    Healthcheck endpoint to verify the service is running.

    Returns:
        dict: A dictionary with the status of the service.
    """
    return {"status": "ok"}
