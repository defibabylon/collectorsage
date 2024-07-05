# Collectorsage

Collectorsage is a comprehensive web application designed to analyze comic book prices. It leverages various APIs and services to fetch and process data, providing users with detailed reports on comic book values.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Available Scripts](#available-scripts)
- [Environment Variables](#environment-variables)
- [Endpoints](#endpoints)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Node.js
- npm or yarn
- Python
- pip

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/defibabylon/collectorsage.git
   cd collectorsage
   ```

2. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:

   ```bash
   cd ..
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file in the root directory and add the necessary environment variables. Refer to the [Environment Variables](#environment-variables) section for details.

### Running the Application

1. Start the backend server:

   ```bash
   python main_v2.py
   ```

2. Start the frontend development server:

   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`.

## Project Structure

```plaintext
collectorsage/
├── databases/
│   ├── 30thcenturycomics-1.json
│   └── SilverAcre-1.json
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .gitignore
│   ├── package.json
│   └── README.md
├── .gitignore
├── config.py
├── main_v2.py
├── requirements.txt
└── README.md
```

## Available Scripts

### Frontend

In the `frontend` directory, you can run:

- `npm start`: Runs the app in development mode.
- `npm test`: Launches the test runner in interactive watch mode.
- `npm run build`: Builds the app for production.
- `npm run eject`: Ejects the app, giving you full control over the configuration.

### Backend

In the root directory, you can run:

- `python main_v2.py`: Starts the backend server.

## Environment Variables

Create a `.env` file in the root directory and add the following variables:

```plaintext
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_google_credentials.json
CLIENT_ID=your_ebay_client_id
CLIENT_SECRET=your_ebay_client_secret
REDIRECT_URI=your_redirect_uri
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name
PINECONE_ENVIRONMENT=your_pinecone_environment
```

## Endpoints

### Root Endpoint

- `GET /`: Returns a welcome message.

### Test Endpoint

- `GET /test`: Returns a test message.

### Process Image

- `POST /process_image`: Processes an uploaded comic book image and returns a detailed report.

### List Routes

- `GET /routes`: Lists all available routes in the application.

Refer to the backend code for more details on the endpoints and their implementations.

## Technologies Used

- **Frontend**: React, Create React App
- **Backend**: Flask, Flask-CORS
- **Database**: JSON files
- **APIs**: eBay API, Anthropic API, Google Cloud API
- **Other**: Pinecone, Redis, TQDM, Pillow

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.
