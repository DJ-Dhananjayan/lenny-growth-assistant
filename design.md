# UI/UX Design System & Layout Guidelines
## Project Name: The Lenny Growth Assistant

---

### 1. Design Aesthetics & Visual Identity
* **Theme**: Modern Dark / Glassmorphism workspace theme tailored for high-focus strategy and writing.
* **Palette**:
  - Primary Accent: Deep Indigo / Violet (`hsl(250, 84%, 60%)`)
  - Background: Obsidian Dark (`hsl(224, 25%, 8%)`)
  - Panel Background: Translucent Slate (`hsl(222, 20%, 12%)` with subtle border `hsl(217, 16%, 20%)`)
  - Text Primary: Crisp Silver (`hsl(210, 40%, 98%)`)
  - Text Muted: Slate Grey (`hsl(215, 20%, 65%)`)
* **Typography**:
  - Primary Font: Inter / System UI Stack (Sans-serif)
  - Code & Artifact Source Font: JetBrains Mono / Fira Code (Monospace)

---

### 2. Information Architecture & Layout Structure

The application features a 3-column responsive grid layout:

```
+----------------+-----------------------------------+-----------------------------------+
|  Sidebar       |  Central Chat Workspace           |  Artifact Side Panel              |
|  (Session Nav) |  - Header (Provider Selector)     |  (Markdown & Safe HTML)           |
|                |  - Message List (With Citations)  |  - Header (Title, Actions, Toggle)|
|  - New Chat    |  - Input Field & Prompt Shortcuts |  - Preview / Code Tab             |
|  - Recent      |                                   |  - Sandboxed HTML / MD Viewer     |
|    Sessions    |                                   |                                   |
+----------------+-----------------------------------+-----------------------------------+
```

---

### 3. Key Components & Interaction States

#### A. Sidebar (Navigation)
* **Default State**: Displays list of recent chat sessions ordered by timestamp with active state highlighting.
* **Actions**:
  - "New Growth Session" button creates clean conversation.
  - Trash icon deletes session with immediate list update.

#### B. Header & Model Selector
* Visible dropdown control displaying active provider (`Ollama (Local)`, `Anthropic (Claude)`, `OpenAI (GPT-4o)`).
* Connection indicator dot (Green = Available, Red = Missing Key or Unreachable).

#### C. Message Feed & Citations
* User messages styled with subtle accent background on right alignment.
* Assistant messages left-aligned with structured Markdown formatting.
* **Citations List**: Rendered below assistant response with episode title, guest name, and clickable podcast link. Clicking source expands source snippet modal or opens link.

#### D. Artifact Viewer (Side Panel)
* Appears dynamically when a conversation generates an artifact or when user clicks an artifact badge in chat.
* **Control Bar**:
  - Tabs: `Preview` vs `Source Code`.
  - Copy Button: Copies raw Markdown or HTML content to clipboard.
  - Download Button: Triggers browser download of file (`.md` or `.html`).
  - Close Button (`X`): Collapses artifact panel.

---

### 4. Accessibility & Responsiveness
* Keyboard navigation support (Ctrl/Cmd+Enter to send message, Esc to dismiss modal/panel).
* High contrast ratio (WCAG AA compliant text colors).
* Fully responsive layout: collapses artifact panel into tabbed overlay on smaller screen widths.
