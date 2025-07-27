# Todo Web

This directory contains the React frontend for the Todo application.

## Development

### 1. Install Dependencies

Navigate to the `todoWeb` directory and install the necessary dependencies.

```bash
npm install
```

### 2. Environment Variables

This project uses environment variables to configure the API endpoint. Create a `.env` file in the `todoWeb` directory by copying the example file:

```bash
cp .env.example .env
```

Modify the `.env` file to match your API's URL. For local development, the default value should work correctly with the Vite proxy.

- `VITE_API_URL`: The base URL for the Todo API.

### 3. Run the Development Server

Once the dependencies are installed and the environment variables are configured, you can start the Vite development server.

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or another port if 5173 is in use).

## Building for Production

To create a production build of the application, run the following command:

```bash
npm run build
```

The optimized and minified files will be placed in the `dist` directory.
