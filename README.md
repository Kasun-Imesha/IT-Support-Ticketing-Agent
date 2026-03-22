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
