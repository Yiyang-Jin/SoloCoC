# CoC Keeper Assistant

A Call of Cthulhu 7th Edition tabletop RPG helper. An AI acts as the Keeper (KP). Supports multiple LLM providers via OpenAI-compatible API.

**Full usage guide: [USAGE_GUIDE_EN.md](USAGE_GUIDE_EN.md)**

---

## Step-by-Step Setup Guide

This guide assumes you have basic computer skills but are not familiar with GitHub, terminals, or network settings. Follow the steps in order.

---

### Step 0: What You Need Before Starting

- A Windows, Mac, or Linux computer  
- An internet connection  
- A web browser (Chrome, Edge, Firefox, etc.)  

---

### Step 1: Install Python

Python is the programming language this app runs on.

1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the yellow button **"Download Python 3.x.x"**
3. Run the installer.

   **On Windows:**  
   - Check the box **"Add Python to PATH"** at the bottom (very important).  
   - Click **"Install Now"**.  
   - When it finishes, click **"Close"**.

4. Check that Python is installed:
   - **Windows:** Press `Win + R`, type `cmd`, press Enter. In the black window, type:
     ```
     python --version
     ```
   - **Mac/Linux:** Open "Terminal" (search for it in applications), type:
     ```
     python3 --version
     ```
   - You should see something like `Python 3.10.0` or similar. If you see "not found" or an error, repeat the installation and make sure "Add to PATH" was checked on Windows.

---

### Step 2: Get the Project Files

You need the project folder on your computer. Typical ways:

- **If you downloaded a ZIP file:**
  1. Find the downloaded ZIP (e.g. `SimpleCoC.zip`).
  2. Right‑click it → **Extract All** (Windows) or double‑click to open (Mac).
  3. Choose a folder (e.g. `Desktop` or `Documents`).
  4. After extraction, you should see a folder named `SimpleCoC` with files like `main.py`, `config.py`, `requirements.txt`, etc.

- **If someone gave you a folder:**  
  Copy the whole `SimpleCoC` folder to a place you can find (e.g. Desktop).

---

### Step 3: Open a Terminal in the Project Folder

You need to run commands inside the `SimpleCoC` folder.

**Windows:**

1. Open File Explorer and go to the `SimpleCoC` folder.
2. Click the address bar at the top (where the path is shown).
3. Type `cmd` and press Enter. A black command window will open, already in that folder.

**Mac:**

1. Open Finder and go to the `SimpleCoC` folder.
2. Right‑click the folder (or hold Control and click).
3. Select **"New Terminal at Folder"** (or **"Services" → "New Terminal at Folder"**).

**Alternative (any system):**

1. Open Terminal (Mac/Linux) or Command Prompt (Windows).
2. Type `cd` followed by a space, then drag the `SimpleCoC` folder into the window and press Enter.
   - Example: `cd C:\Users\YourName\Desktop\SimpleCoC`
   - Or: `cd /Users/YourName/Desktop/SimpleCoC`

---

### Step 4: Create a Virtual Environment (Recommended)

A virtual environment keeps this project’s libraries separate from other programs.

1. In the terminal, with the `SimpleCoC` folder as the current directory, run:
   - **Windows:**
     ```
     python -m venv venv
     ```
   - **Mac/Linux:**
     ```
     python3 -m venv venv
     ```
2. Activate it:
   - **Windows:**
     ```
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```
     source venv/bin/activate
     ```
3. You should see `(venv)` at the start of the line. That means the virtual environment is active.

---

### Step 5: Install Dependencies

The app needs several Python libraries. Install them with:

- **Windows (with venv active):**
  ```
  pip install -r requirements.txt
  ```
- **Mac/Linux (with venv active):**
  ```
  pip3 install -r requirements.txt
  ```

Wait until all packages finish installing. You may see a lot of text; that’s normal. When it’s done, you’ll get your prompt back.

If you see errors like "pip not found", try:
- **Windows:** `python -m pip install -r requirements.txt`
- **Mac/Linux:** `python3 -m pip install -r requirements.txt`

---

### Step 6: Get an API Key (or Use a Local LLM)

**Recommended:** Alibaba Bailian's **qwen3.5-plus** model gives the best CoC experience (default). Other LLMs may vary.

The app supports many AI providers. Most need an API key; Ollama and LM Studio (local) do not.

1. Open the app settings and select an LLM Provider.
2. For Alibaba Bailian (default), open your browser and go to:
   - **International:** https://modelstudio.console.alibabacloud.com/ (Singapore)
   - **China:** https://bailian.console.aliyun.com/
3. Sign up or log in, then create an API key (usually starts with `sk-`).
4. Copy the key and keep it safe. **Don’t share it.**

5. For Ollama or LM Studio: install and run locally first; no API key needed.

---

### Step 7: Start the Application

1. Make sure your terminal is:
   - In the `SimpleCoC` folder.
   - Has the virtual environment activated (you see `(venv)` if you used Step 4).

2. Run:
   - **Windows:**
     ```
     python main.py
     ```
   - **Mac/Linux:**
     ```
     python3 main.py
     ```

3. You should see something like:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:29147
   ```
4. **Leave this window open.** Closing it will stop the app.

---

### Step 8: Open the App in Your Browser

1. Open your web browser (Chrome, Edge, Firefox, etc.).
2. In the address bar, type:
   ```
   http://localhost:29147
   ```
3. Press Enter.
4. You should see the CoC Keeper Assistant interface.

---

### Step 9: Configure API Key in the Web UI

1. In the app, click the gear icon in the top-right, or the **"Settings"** button.
2. In the **API Key** field, paste the key you copied in Step 6.
3. Choose your preferred language (e.g. English).
4. Click **Save**.
5. You can close the settings window and start using the app.

---

### Step 10: Basic Usage

1. **Scripts:** Upload a PDF scenario script (e.g. a pre-written CoC scenario).
2. **Characters:** Create or import character sheets (PDF, JSON, TXT, etc.).
3. **Chat:** Choose a character or “Player ask KP” mode, then type actions or questions.
4. **Dice:** The KP’s replies can include automatic rolls when using `[ROLL:skill|value]` or `[DICE:1d6]` in the prompt.

> For interface overview, workflows, and dice syntax, see **[USAGE_GUIDE_EN.md](USAGE_GUIDE_EN.md)**.

---

## Supported LLM Providers

Choose a provider in Settings. All use the OpenAI-compatible API:

| Provider | Get Key | Default Model |
|----------|---------|---------------|
| Alibaba Bailian | [Console](https://modelstudio.console.alibabacloud.com/) | qwen3.5-plus |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | deepseek-chat |
| Moonshot Kimi | [platform.moonshot.ai](https://platform.moonshot.ai/) | moonshot-v1-8k |
| Zhipu GLM | [open.bigmodel.cn](https://open.bigmodel.cn/) | glm-4-plus |
| Groq | [console.groq.com](https://console.groq.com/) | llama-3.1-70b-versatile |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | gpt-4o-mini |
| OpenRouter | [openrouter.ai](https://openrouter.ai/) | Multi-provider |
| Together.ai | [api.together.xyz](https://api.together.xyz/) | Open-source inference |
| Ollama (local) | No key | qwen2.5 |
| LM Studio (local) | No key | Your choice |
| Custom | Your base_url | Your model |

---

## Features

- **Multi-LLM:** Alibaba Bailian, DeepSeek, Kimi, Zhipu, Groq, OpenAI, OpenRouter, Ollama, etc.
- **Bilingual:** Chinese / English. Switch via the EN/中 button; preference is saved.
- **Web API Key:** Configure your API key in Settings; it’s stored in `data/api_config.json`.
- **Character management:** Create, edit, import (PDF/JSON/TXT/MD/HTML/DOCX), or generate with AI.
- **Script RAG:** Upload PDF scripts; the app retrieves relevant sections for the KP.
- **KP chat:** Talk to the AI KP, either as a character or as a player asking questions.
- **Dice:** D100, 3D6, skill checks. KP responses use `[ROLL:skill|value]` and `[DICE:expr]` for automatic rolls.
- **Action log:** Records chat, dice, and checks; can be exported.

---

## Troubleshooting

**"Python is not recognized" or "command not found"**

- Reinstall Python and ensure “Add Python to PATH” is checked (Windows).
- Restart the terminal or the computer after installation.

**"pip is not recognized"**

- Use: `python -m pip install -r requirements.txt` (or `python3 -m pip` on Mac/Linux).

**"Port 29147 is already in use"**

- Another program is using that port. Close other instances of this app, or change the port in `main.py` at the bottom (e.g. to `29148`).

**"API error" or "Please set API Key"**

- Go to Settings in the web UI and paste a valid Bailian API key. Make sure it starts with `sk-` and has no extra spaces.

**"This site can’t be reached" or "Connection refused"**

- Make sure the app is running (Step 7) and the terminal window is still open.
- Confirm you’re using `http://localhost:29147` (not https, and no trailing slash if it causes issues).

---

## Folder Structure

```
SimpleCoC/
├── main.py           # Application entry point
├── config.py         # Configuration
├── api_config.py     # API key storage (from web UI)
├── coc_*.py          # CoC modules
├── settings_store.py # Generation parameters
├── defaults/         # Default KP prompt
├── static/           # Web frontend
└── data/             # Local data (characters, scripts, sessions; not in git)
```

---

## Stopping the Application

- In the terminal where the app is running, press `Ctrl + C`.
- Or simply close the terminal window.
