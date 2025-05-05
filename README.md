# DPDKBotAI

DPDKBotAI is an AI-powered bot that leverages OpenAI's capabilities to provide intelligent responses and assistance. This project is designed to help users interact with an AI system in a structured and efficient manner.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DPDKBotAI.git
cd DPDKBotAI
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Rename `.env_bck` to `.env`
   - Open the `.env` file and replace the placeholder OpenAI API key with your own key
   - You can obtain an API key by signing up at [OpenAI's platform](https://platform.openai.com)

## Usage

### Basic

To run the DPDKBot simply run:
```bash
python Bot.py
```
This will start a chat with the bot. To exit the chat simply type exit.
As a default the Bot is configured in the following way:
  1. System prompt - defines the way the model will act and the messages format (SystemMsg)
  2. Developer prompt - simulate a developer prompt to map the user request to one of the predefined values (DeveloperMsg)
  3. RTE Flow context - holds the RTE Flow template api context to be used by the AI (TemplateAPICTX)
  4. The Bot - holds the main logic of the application.

### Adding new context

1. Add a new file with the relevant context
2. attach this new context to the request context field

## Project Structure

```
DPDKBotAI/
├── src/               # Source code directory
├── .env              # Environment variables (rename from .env_bck)
├── .env_bck          # Environment variables backup
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

## Support

If you encounter any issues or have questions, please open an issue in the repository.
