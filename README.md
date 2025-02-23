# Audio Streaming App

This project is a web-based audio streaming application built with React for the frontend and a WebSocket server for the backend. The application captures audio from the user's microphone, streams it to the backend server for processing, and displays the inference results in real-time.

**Disclaimer**: The frontend of this application is entirely AI-generated and may be rough around the edges. Please be aware that it might not meet all production standards and could require further refinement.

## Features
- Real-time audio streaming from the browser to the server
- WebSocket communication for low-latency data transfer
- Dockerized setup for easy deployment
- Environment variable configuration for flexible deployment

## Prerequisites
- Docker and Docker Compose installed on your machine
- Node.js and npm (for local development)

## Setup and Installation

## Configuration
The application offers several configuration options to customize its behavior:

- **WebSocket URL**: The WebSocket URL is configured using the `REACT_APP_WS_URL` environment variable. This can be set in the Dockerfile or passed as a build argument.
- **Model Configuration**: The backend uses a configuration file (`config/config.yaml`) to set parameters for audio processing and inference:
  - **chunk_size**: Defines the duration of each audio chunk received from the client.
  - **sample_rate**: Specifies the number of audio samples per second. A common value for speech processing is 16kHz.
  - **window_size**: Sets the length of the audio window used for inference, measured in seconds.
  - **overlap_ratio**: Determines the fraction of overlap between consecutive audio windows, allowing for smoother transitions and more accurate predictions.
  - **rms_threshold**: Establishes the root mean square (RMS) threshold for audio classification, helping to filter out low-intensity noise.

### Docker Deployment
1. **Build Docker Compose images**:
   ```bash
   make build
   ```
   This command will build the Docker images for the frontend and backend services as defined in the `docker-compose.yml` file.

2. **Run Docker Compose services**:
   ```bash
   make run
   ```
   This will start the frontend and backend services. Please wait for all services to be healthy and running before accessing the application, as the backend requires some time to load the model.

3. **Access the application**:
   - Frontend: `http://localhost:8001`
   - Backend WebSocket: `ws://localhost:8000/audio`

4. **Stop Docker Compose services**:
   ```bash
   make stop
   ```
   This will stop the running frontend and backend services.

## Batched Inference and Circular Buffer
The backend server uses a batched inference approach with a circular buffer to efficiently process audio data:

- **Batched Inference**: The server processes audio data in batches using a pre-trained model (`7wolf/wav2vec2-base-gender-classification`). This allows for efficient and accurate inference by leveraging the model's capabilities to handle multiple audio chunks simultaneously. The audio stream is classified into three categories: ambient noise, male, or female.

- **Circular Buffer**: A deque is used as a circular buffer to store incoming audio chunks. The buffer has a maximum length, ensuring that only the most recent audio data is retained. This approach allows for continuous processing of audio streams without running out of memory.

- **Audio Processing**: The server processes audio chunks in a separate thread, ensuring that the main WebSocket connection remains responsive. The audio data is decoded, converted to a tensor, and passed to the model for inference. The predicted class is then sent back to the client via the WebSocket connection.

## Makefile Usage
The project includes a Makefile with several useful commands:

- **format**: Format code using black and isort
  ```bash
  make format
  ```
- **lint**: Run linting checks
  ```bash
  make lint
  ```
- **clean**: Remove Python cache files
  ```bash
  make clean
  ```
- **build**: Build Docker Compose images
  ```bash
  make build
  ```
- **run**: Run Docker Compose services
  ```bash
  make run
  ```
- **stop**: Stop Docker Compose services
  ```bash
  make stop
  ```

## File Structure
- `frontend/`: Contains the React frontend application.
  - `src/`: Source code for the React app.
  - `Dockerfile.frontend`: Dockerfile for building the frontend.
- `backend/`: Contains the backend WebSocket server code.
- `docker-compose.yml`: Docker Compose configuration file.
- `notebooks/`: Contains related Jupyter notebooks for additional analysis and experimentation.

## Troubleshooting
- **WebSocket Connection Issues**: Ensure the backend service is running and accessible on the specified port. Check network configurations and firewall settings.
- **Docker Networking**: Ensure that Docker services are on the same network and can communicate using service names.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or support, please contact Junaid Malik at [hafizjunaidmalik@gmail.com].