FROM python:3.10 AS main

WORKDIR /app

# Install pandoc and netcat
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    pandoc \
    netcat-openbsd \
    libgl1 \  
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Pre-download tiktoken encoder to avoid SSL issues at runtime
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')" || echo "Tiktoken download skipped"

# Download standard NLTK data, to prevent unstructured from downloading packages at runtime
RUN python -m nltk.downloader -d /app/nltk_data punkt_tab averaged_perceptron_tagger
ENV NLTK_DATA=/app/nltk_data

# Disable Unstructured analytics
ENV SCARF_NO_ANALYTICS=true

# Disable SSL verification for corporate certificates
ENV PYTHONHTTPSVERIFY=0
ENV CURL_CA_BUNDLE=""
ENV REQUESTS_CA_BUNDLE=""

COPY . .

CMD ["python", "main.py"]
