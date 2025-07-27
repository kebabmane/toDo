# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml first to leverage Docker cache
COPY pyproject.toml .

# Install Python dependencies using uv
RUN uv pip install --system --no-cache -e .

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Create directory for SQLite database and set permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Set environment variables for production
ENV FLASK_ENV=production
ENV SECRET_KEY=your-secret-key-change-me
ENV JWT_SECRET_KEY=your-jwt-secret-key-change-me
ENV DATABASE_URL=sqlite:///data/todo.db
ENV PORT=5001

# Expose port
EXPOSE 5001

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001')" || exit 1

# Run the application
CMD ["python", "app.py"]
