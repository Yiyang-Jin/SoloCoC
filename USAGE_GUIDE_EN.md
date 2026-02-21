# CoC Keeper Assistant · Usage Guide

This document explains how to use the CoC Keeper Assistant in detail. For installation and setup, see [README_EN.md](README_EN.md).

---

## 1. Interface Overview

The interface has a **sidebar** (left) and a **main area** (right).

### Sidebar

- **Header:** App title, EN/中 language toggle, Settings button ⚙
- **Characters:** Character list, New/Generate, Import
- **Dice:** Manual dice input (e.g. `1d100`, `3d6×5`) and Roll button
- **KP Prompt:** Customize the Keeper’s system prompt
- **Scripts:** Uploaded script list, Upload PDF Script
- **Maps:** Uploaded map images, Upload Map Images

### Main Area

- **KP Mode:** Chat mode, character selection, input box, and chat with the AI KP
- **Action Log:** Records chat, dice rolls, skill checks; supports Refresh, Export, New Session
- **Character Detail:** Shown when you click a character in the sidebar (can edit)

---

## 2. First-Time Flow

1. **Open Settings:** Click the gear ⚙, configure LLM provider and API Key (see “Settings” below)
2. **Upload Script:** In the sidebar under “Scripts”, click “Upload PDF Script” and select a CoC scenario PDF
3. **Prepare Character:** Create or import a character sheet
4. **Start Chat:** Select the script and mode, type an action or question, click **Send**

---

## 3. Settings

Click **⚙ Settings** to open the settings modal.

**Recommended:** Alibaba Bailian's **qwen3.5-plus** model gives the best CoC experience. Other LLMs may vary.

| Item | Description |
|------|-------------|
| **LLM Provider** | Choose AI provider (Bailian, DeepSeek, Kimi, Zhipu, etc.) or Ollama/LM Studio (local) |
| **API URL** | Shown only when “Custom” is selected; enter an OpenAI-compatible API base URL |
| **Model** | Model name (e.g. qwen3.5-plus, deepseek-chat) |
| **API Key** | Required for most cloud providers; leave empty for Ollama or LM Studio |
| **Language** | UI language: Chinese / English |

Settings are saved to `data/api_config.json` and take effect immediately.

---

## 4. Script Management

### Upload Script

1. Click **Upload PDF Script**
2. Select a CoC scenario or module PDF
3. After upload, the script appears in the list with its character count

### Select Script

- Click a script in the list to highlight it
- Chat will not work without a selected script; you will see “Please upload a script first”

### Role of Scripts

Uploaded scripts are parsed and indexed. The KP retrieves relevant passages during chat to guide the story and rulings.

---

## 5. Character Management

### New Character

1. Click **+ New/Generate**
2. Fill in the form (basic info, attributes, skills, combat, persona)
3. **Roll Attributes:** Click “Roll” to auto-roll 3D6 for STR, CON, etc.
4. **AI Suggest Skills:** Select an occupation, then click “AI Suggest” for occupation-based skills
5. **AI Generate Persona:** After filling name, age, occupation, nationality, click “AI Generate”
6. Click **Save**

### Import Character

- Click **Import**. Supports: PDF, JSON, TXT, MD, HTML, DOCX
- Imported characters appear in the list

### Edit Character

- Click a character in the sidebar to show details
- Click **Edit** to open the form, then save changes

### Delete Character

- Click the **Del** button next to a character in the list
- Confirm to delete

---

## 6. Maps

Upload map images (PNG/JPG/WEBP/BMP); use standard filenames (e.g. "1-museum-gate.png"). On each turn: 1) **All map filenames** are injected into the prompt; KP judges applicability; 2) If the context (player input + script) matches a map filename, and the LLM supports vision, that map image is passed; 3) **Forces the KP to start the reply by**:

1. **Deciding if any map applies** — if so, state “Applicable map: filename”; if not, “No applicable map”
2. **Paraphrasing the player/character’s request**
3. **Noting ambiguities or questions**

Suited for long scenarios like "The Mask of Nyarlathotep" with many standard-named maps.

---

## 7. KP Mode and Chat

### Chat Modes

| Mode | Description |
|------|-------------|
| **Character action** | Act as the selected character; the KP uses character sheet info in replies |
| **Player ask KP** | Ask the KP as a player (rules, plot, etc.), without a character |

### Sending Messages

1. Ensure a script is selected (highlighted in the list)
2. Choose mode: Character action or Player ask KP
3. For Character action, select a character from the dropdown
4. Type your action or question and click **Send** or press Enter (Shift+Enter for newline)

### AI Infer Action

- In Character action mode, after selecting a character, click **AI Infer Action**
- The AI suggests an action based on the story and character; you can paste it into the input or edit it

---

## 8. Dice System

### Automatic Rolls in Chat

The KP can use special tags in replies; the system will roll and replace them with results:

| Tag | Description | Example |
|-----|-------------|---------|
| `[ROLL:skill\|value]` | Skill check (D100) | `[ROLL:Spot Hidden|60]` |
| `[DICE:expr]` | Any dice expression | `[DICE:1d100]`, `[DICE:3d6×5]` |

- skill and value are separated by `|`
- Supported: `1d100`, `3d6`, `2d6+6`, `3d6×5`, etc.

### Manual Rolls (Sidebar)

- For Luck, damage, or other non-skill rolls
- Enter an expression (e.g. `1d100`, `3d6×5`) in the Dice field and click **Roll**
- The result appears below and is logged in the Action Log

---

## 9. Action Log

- **Refresh:** Reload the current session log
- **Export TXT:** Export the log as a text file for records or review
- **New Session:** Clear the current session and start a new one (clears chat history; characters and scripts remain)

The log includes: player/character messages, KP replies, dice results, skill checks and outcomes.

---

## 10. KP Prompt Settings

Click **KP Prompt** to customize the Keeper’s system prompt.

- Use it to set KP style, rule preferences, how scripts are used, etc.
- You can mention `[ROLL]` and `[DICE]` usage in the prompt
- Click **Reset Default** to restore the built-in default prompt

---

## 11. Typical Session Flow

1. Open the app and ensure API Key is set in Settings
2. Upload the scenario PDF you are running
3. Create or import investigator character(s)
4. Select the script, choose “Character action”, and select a character
5. Type the investigator’s action (e.g. “I examine the letters on the desk”) and send
6. The KP replies with the story; when a check is needed, it uses `[ROLL:skill|value]` in the reply
7. The system rolls automatically and the KP’s reply shows the result
8. Continue the conversation; use “New Session” when starting a new scenario

---

## 12. Quick Tips

- **Cannot send messages:** Check that a script is selected
- **API error:** Verify API Key and model in Settings
- **Dice not working:** Ensure the KP uses correct `[ROLL:...]` or `[DICE:...]` format
- **Change language:** Click EN/中 or go to Settings → Language
