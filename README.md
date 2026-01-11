# ChatMoonVLM

ChatMoonVLM is a web-based Visual Question Answering (VQA) application powered by the Moondream model. It allows users to upload images and ask natural language questions about them through an interactive chat interface.

## Usage

The application is containerized using Docker and the image is published on Docker Hub. 

You can run the application using the following command after pulling the image from [Docker Hub](https://hub.docker.com/r/okanberhoglu/chat_moon_vlm):

```bash
docker run -p 8501:8501 okanberhoglu/chat_moon_vlm:latest
```

This will expose the application on `http://localhost:8501`.

## Detailed Information

For comprehensive details regarding the methodology, architecture, and implementation, please refer to the project[report](docs/berhoglu_okan_project_report.pdf).
