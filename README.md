# Casablanca

A YouTube transcript reader and summarizer.

## Features

- Fetches YouTube video transcripts.
- Summarizes transcripts using the Gemini API.
- Modular design for easy extension and maintenance.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/casablanca.git
    cd casablanca
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Install the package locally (optional, for development):**

    ```bash
    pip install .
    ```

## API Key Setup

This project uses the Gemini API for summarization. You need to set up your API key:

1.  Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create a file named `.env` in the root directory of the project.
3.  Add your API key to the `.env` file in the following format:

    ```
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    ```

    Replace `YOUR_API_KEY_HERE` with your actual Gemini API key.

## Usage

To run the application and summarize a YouTube video transcript:

```bash
python -m casablanca.main <youtube_video_url>
```

Example:

```bash
python -m casablanca.main https://www.youtube.com/watch?v=erI6k_hnToE
```

## Running Tests

To run the unit tests for the project, make sure you have `pytest` installed (`pip install pytest`) and then run:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
