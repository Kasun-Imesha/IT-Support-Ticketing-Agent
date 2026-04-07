# IT Support AI Assist 🤖

**Get instant help for your IT problems—no waiting for the support desk!**

IT Support AI Assist is an intelligent AI chatbot that helps you resolve common IT issues quickly. Just describe your problem, and our AI team of specialized agents will work together to find the best solution for you.

---

## What Can It Help With?

This AI assistant can help with a wide range of IT support issues:

- 🔗 **Network Issues** — VPN connections, WiFi problems, connectivity errors
- 💻 **Hardware Issues** — Device problems, printer troubles, connection issues
- 🐛 **Software Bugs** — Application crashes, performance problems, error messages
- 🔐 **Access Requests** — Permission issues, account access problems
- 🔑 **Password Resets** — Getting back into your accounts
- ❓ **General IT Help** — And much more!

---

## How to Use

### Getting Started

1. **Open the application** in your web browser
2. **Describe your problem** in the text area as clearly as possible
3. **Click "Resolve Now"** and wait for the AI to process your issue

### Tips for Best Results

- **Be specific**: Instead of "my computer is broken," try "I can't connect to the company VPN"
- **Include error messages**: If you see an error message, copy and paste it into the description
- **Mention what you've already tried**: Help the AI understand what's already been attempted
- **Include relevant details**: What application, device, or system are you having trouble with?

---

## What Happens Next

When you submit your issue, here's how our AI team works together to help you:

1. **Classification** — The AI analyzes your problem and categorizes it
2. **Knowledge Search** — It searches our IT knowledge base for matching solutions
3. **Solution** — You'll receive a recommended solution or next steps
4. **Escalation** — If needed, complex issues are escalated to the IT support team via email

---

## Policy Enforcement

The IT Support AI Assist integrates a three-stage policy enforcement system to protect user privacy and ensure response quality:

### 1. **Input Enforcement** (Before Processing)

Every user submission is scanned for security and privacy risks:

#### PII & Sensitive Data Detection
- **Email Addresses** — Blocks messages containing email addresses
- **Phone Numbers** — Detects and blocks phone numbers (international and local formats)
- **Credit Card Numbers** — Prevents submission of payment card information
- **Social Security Numbers** — Blocks US SSN patterns
- **Passwords** — Warns when plaintext passwords are detected

#### Content Safety Checks
- **Length Validation** — Rejects trivially short (<10 chars) or excessively long (>2000 chars) inputs
- **Prompt Injection Detection** — Identifies common prompt-injection attack patterns
- **Offensive Language** — Flags abusive or offensive language (warning only)
- **IT Relevance Check** — Warns if the message appears unrelated to IT support

**What happens if a policy is violated?**
- **Block (Blocking)**: Prevents submission entirely and displays error reasons
- **Warn (Warning)**: Allows submission but alerts the user to potential issues

### 2. **Main Processing Pipeline**

If input enforcement passes, your message goes through the AI agents:

1. **Classifier Agent** — Categorizes your IT issue
2. **Knowledge Base Agent** — Searches the IT knowledge base for solutions
3. **Notification Agent** — Escalates complex issues to the support team via email

### 3. **Output Enforcement** (After AI Processing)

Before returning the AI's response, the system checks for data leakage and quality issues:

#### PII Leakage Prevention
- **Email Redaction** — Masks any email addresses that appear in the AI response as `[EMAIL REDACTED]`
- **Phone Redaction** — Masks any phone numbers in the response as `[PHONE REDACTED]`

#### Response Quality Checks
- **Minimum Length** — Warns if the AI provides an unusually short response
- **Hallucination Detection** — Appends a disclaimer when the AI uses speculative language ("I think," "might be," etc.)
- **Harmful Advice Blocking** — Blocks any responses suggesting destructive or dangerous commands

### Customizing Policy Settings

You can adjust policy enforcement by editing [policies/policy_config.py](policies/policy_config.py):

- Set `"enabled": False` to disable a specific policy check
- Change `"severity"` from `"block"` to `"warn"` (or vice versa) to adjust how strict a policy is
- Modify threshold values (e.g., `min_chars`, `max_chars`) to fit your needs

Example: To allow email addresses in input but still redact them from output, disable `detect_email_pii` in the INPUT_POLICIES section.

---

## System Requirements

To run this application, you'll need:

- Python 3.10 or higher
- An active internet connection
- A valid OpenAI API key (for AI processing power)

---

## Installation & Setup

### Step 1: Get the Files

Clone or download this project to your computer.

### Step 2: Install Dependencies

Open your terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

### Step 3: Add Your API Key

1. Create a file named `.env` in the project folder (copy from `.env-template`)
2. Add your OpenAI API key and other environment variables:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
3. Save the file

### Step 4: Build the db
- Build the knowledge batabase using the following command.
- You can find the sample knowledge base file at [knowledge_base.json](./data/knowledge_base.json) - feel free to add more data and make the Assistant more knowledgeable


```bash
cd misc/
python build_db.py
```
### Step 4: Run the Application

In your terminal, type:

```bash
streamlit run app.py --server.port <PORT>
```

This will start the application in your web browser. It usually opens automatically at `http://localhost:<PORT>` (specify the PORT in the command)

---

## Docker Setup

### Using Docker Compose (Recommended)

Docker Compose simplifies running the application with all dependencies pre-configured.

#### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed

#### Quick Start

1. **Create a `.env` file** in the project root:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   STREAMLIT_PORT=8501
   STREAMLIT_ADDRESS=0.0.0.0
   ```

2. **Start the application**:
   ```bash
   docker-compose up
   ```
   The application will be available at `http://localhost:8501`

3. **Stop the application**:
   ```bash
   docker-compose down
   ```

#### Customization

You can modify the port and other settings in the `.env` file:
- `STREAMLIT_PORT` — Change the port (default: 8501)
- `STREAMLIT_ADDRESS` — Change the bind address (default: 0.0.0.0)
- `OPENAI_API_KEY` — Your OpenAI API key

#### Data Persistence

The Docker setup automatically mounts:
- `./vector_store` — Chroma vector store (for traditional embeddings)
- `./vector_store_faiss` — FAISS index (for fast similarity search)
- `./data` — Knowledge base files

These directories persist between container restarts.

### Using Docker Directly

If you prefer to build and run the Docker image manually:

1. **Build the image**:
   ```bash
   docker build -t it-support-ai:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 \
     -e OPENAI_API_KEY=your_actual_api_key_here \
     -v $(pwd)/vector_store:/app/vector_store \
     -v $(pwd)/vector_store_faiss:/app/vector_store_faiss \
     -v $(pwd)/data:/app/data \
     it-support-ai:latest
   ```

3. **Access the application** at `http://localhost:8501`

#### Volume Mounting

Make sure to mount the necessary directories for data persistence:
- `-v $(pwd)/vector_store:/app/vector_store` — Vector store persistence
- `-v $(pwd)/vector_store_faiss:/app/vector_store_faiss` — FAISS index persistence
- `-v $(pwd)/data:/app/data` — Knowledge base persistence

---

## Troubleshooting

### "API key error" message
- Make sure you've created the `.env` file in the correct location
- Verify your OpenAI API key is valid and has available credits
- Don't share your API key with anyone

### "Application won't start"
- Make sure all dependencies are installed (`pip install -r requirements.txt`)
- Try restarting your terminal
- Ensure Python 3.10+ is installed on your system

### "No solution found"
- Try rephrasing your issue more clearly
- Include more specific details about the problem
- If the issue is very specific, escalation to the IT team may be necessary

---

## Privacy & Data

- Your issue descriptions are processed by the AI to find solutions
- Complex issues may be escalated to human support staff
- Keep sensitive information (passwords, phone numbers) out of your descriptions

---

## Need More Help?

If the AI can't resolve your issue, it will escalate it to the IT support team. You'll be notified of the escalation and next steps.

---

Enjoy faster IT support! 🚀
