This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# orVGoal
-----
Build a small, demo-ready Windows desktop assistant that integrates with the Netflix desktop application (Microsoft Store / UWP version), NOT the Netflix website. The assistant appears as a lightweight inline overlay near the Netflix search box and is triggered by typing `AI:`.

This is a proof-of-concept meant for a short PPT/demo video, not a production build.

Core Idea
---------
When the user types inside Netflix’s search field and begins the query with `AI:`, show a minimal, clean suggestion panel directly below the search field. The panel lists AI-curated results (e.g., horror movies) and allows keyboard or mouse selection. On selection, the assistant automatically fills the Netflix search and triggers native search.

Technical Constraints
---------------------
- Netflix desktop app is a UWP / packaged application.
- Direct DOM access is NOT available.
- Solution must use **system-level techniques**, not browser extensions.

Use one of the following acceptable approaches (prefer in this order):
1. Windows UI Automation (UIA) to detect and interact with the Netflix search textbox.
2. Accessibility APIs + focus tracking to monitor text input.
3. A transparent always-on-top overlay window positioned relative to the detected Netflix search box.
4. Keyboard hook (low-level) ONLY when Netflix app is in foreground.

High-Level Behavior
-------------------
1. Detect when the Netflix desktop app window is active.
2. Detect when the user focuses the Netflix search input.
3. Monitor typed text ONLY while Netflix search has focus.
4. If input starts with `AI:`:
   - Parse the query after `AI:`
   - Show a small overlay panel directly below the search box.
5. The overlay lists 6–10 results with:
   - title
   - year
   - small poster (optional placeholder)
   - rating (or N/A)

Interaction
-----------
- Arrow Up / Down → navigate results
- Enter → select highlighted result
- Mouse click → select
- Escape → close overlay

On selection:
-------------
- Replace the Netflix search input text with the selected title
- Programmatically send Enter / invoke UIA action to trigger Netflix’s native search

If direct triggering fails:
- Gracefully fallback to sending simulated keyboard input.

Data Source
-----------
Two modes:
- **Demo Mode (default)**: use local hardcoded JSON dataset (no API keys).
- **Live Mode (optional)**: fetch movie metadata from TMDB or OMDB.

UI Requirements
---------------
- Overlay must be:
  - Small
  - Border-radius
  - Subtle shadow
  - Aligned exactly below Netflix search box
- No full-screen overlays
- No blocking input
- No visual clutter

Implementation Stack (suggested)
--------------------------------
Choose ONE primary language:
- Python (with pywin32 + UI Automation)
OR
- C# (.NET + UIAutomationClient)
OR
- C++ (Win32 + UIA)

Overlay window:
- Transparent
- Click-through outside component
- Always-on-top ONLY when Netflix is active
- Hidden otherwise

Deliverables
------------
1. Minimal working prototype code
2. Demo dataset JSON
3. README explaining:
   - How the Netflix app is detected
   - How search box is identified
   - How overlay positioning works
4. A short demo script for a 30–60 second screen recording:
   - Open Netflix app
   - Click search
   - Type `AI: horror movies`
   - Show suggestions
   - Use arrow keys + Enter
   - Netflix search results appear

Privacy & Safety
----------------
- Do not log keystrokes globally
- Only observe input when Netflix is focused
- No data sent externally in Demo mode

Acceptance Criteria
-------------------
- Works with Netflix desktop app (not browser)
- Overlay appears within 200ms after `AI:` is typed
- Keyboard navigation works
- Selecting a movie triggers Netflix search
- Clean and professional appearance suitable for PPT demo
Goal
-----
Build a small, demo-ready Windows desktop assistant that integrates with the Netflix desktop application (Microsoft Store / UWP version), NOT the Netflix website. The assistant appears as a lightweight inline overlay near the Netflix search box and is triggered by typing `AI:`.

This is a proof-of-concept meant for a short PPT/demo video, not a production build.

Core Idea
---------
When the user types inside Netflix’s search field and begins the query with `AI:`, show a minimal, clean suggestion panel directly below the search field. The panel lists AI-curated results (e.g., horror movies) and allows keyboard or mouse selection. On selection, the assistant automatically fills the Netflix search and triggers native search.

Technical Constraints
---------------------
- Netflix desktop app is a UWP / packaged application.
- Direct DOM access is NOT available.
- Solution must use **system-level techniques**, not browser extensions.

Use one of the following acceptable Goal
-----
Build a small, demo-ready Windows desktop assistant that integrates with the Netflix desktop application (Microsoft Store / UWP version), NOT the Netflix website. The assistant appears as a lightweight inline overlay near the Netflix search box and is triggered by typing `AI:`.

This is a proof-of-concept meant for a short PPT/demo video, not a production build.

Core Idea
---------
When the user types inside Netflix’s search field and begins the query with `AI:`, show a minimal, clean suggestion panel directly below the search field. The panel lists AI-curated results (e.g., horror movies) and allows keyboard or mouse selection. On selection, the assistant automatically fills the Netflix search and triggers native search.

Technical Constraints
---------------------
- Netflix desktop app is a UWP / packaged application.
- Direct DOM access is NOT available.
- Solution must use **system-level techniques**, not browser extensions.

Use one of the following acceptable approaches (prefer in this order):
1. Windows UI Automation (UIA) to detect and interact with the Netflix search textbox.
2. Accessibility APIs + focus tracking to monitor text input.
3. A transparent always-on-top overlay window positioned relative to the detected Netflix search box.
4. Keyboard hook (low-level) ONLY when Netflix app is in foreground.

High-Level Behavior
-------------------
1. Detect when the Netflix desktop app window is active.
2. Detect when the user focuses the Netflix search input.
3. Monitor typed text ONLY while Netflix search has focus.
4. If input starts with `AI:`:
   - Parse the query after `AI:`
   - Show a small overlay panel directly below the search box.
5. The overlay lists 6–10 results with:
   - title
   - year
   - small poster (optional placeholder)
   - rating (or N/A)

Interaction
-----------
- Arrow Up / Down → navigate results
- Enter → select highlighted result
- Mouse click → select
- Escape → close overlay

On selection:
-------------
- Replace the Netflix search input text with the selected title
- Programmatically send Enter / invoke UIA action to trigger Netflix’s native search

If direct triggering fails:
- Gracefully fallback to sending simulated keyboard input.

Data Source
-----------
Two modes:
- **Demo Mode (default)**: use local hardcoded JSON dataset (no API keys).
- **Live Mode (optional)**: fetch movie metadata from TMDB or OMDB.

UI Requirements
---------------
- Overlay must be:
  - Small
  - Border-radius
  - Subtle shadow
  - Aligned exactly below Netflix search box
- No full-screen overlays
- No blocking input
- No visual clutter

Implementation Stack (suggested)
--------------------------------
Choose ONE primary language:
- Python (with pywin32 + UI Automation)
OR
- C# (.NET + UIAutomationClient)
OR
- C++ (Win32 + UIA)

Overlay window:
- Transparent
- Click-through outside component
- Always-on-top ONLY when Netflix is active
- Hidden otherwise

Deliverables
------------
1. Minimal working prototype code
2. Demo dataset JSON
3. README explaining:
   - How the Netflix app is detected
   - How search box is identified
   - How overlay positioning works
4. A short demo script for a 30–60 second screen recording:
   - Open Netflix app
   - Click search
   - Type `AI: horror movies`
   - Show suggestions
   - Use arrow keys + Enter
   - Netflix search results appear

Privacy & Safety
----------------
- Do not log keystrokes globally
- Only observe input when Netflix is focused
- No data sent externally in Demo mode

Acceptance Criteria
-------------------
- Works with Netflix desktop app (not browser)
- Overlay appears within 200ms after `AI:` is typed
- Keyboard navigation works
- Selecting a movie triggers Netflix search
- Clean and professional appearance suitable for PPT demo
approaches (prefer in this order):
1. Windows UI Automation (UIA) to detect and interact with the Netflix search textbox.
2. Accessibility APIs + focus tracking to monitor text input.
3. A transparent always-on-top overlay window positioned relative to the detected Netflix search box.
4. Keyboard hook (low-level) ONLY when Netflix app is in foreground.

High-Level Behavior
-------------------
1. Detect when the Netflix desktop app window is active.
2. Detect when the user focuses the Netflix search input.
3. Monitor typed text ONLY while Netflix search has focus.
4. If input starts with `AI:`:
   - Parse the query after `AI:`
   - Show a small overlay panel directly below the search box.
5. The overlay lists 6–10 results with:
   - title
   - year
   - small poster (optional placeholder)
   - rating (or N/A)

Interaction
-----------
- Arrow Up / Down → navigate results
- Enter → select highlighted result
- Mouse click → select
- Escape → close overlay

On selection:
-------------
- Replace the Netflix search input text with the selected title
- Programmatically send Enter / invoke UIA action to trigger Netflix’s native search

If direct triggering fails:
- Gracefully fallback to sending simulated keyboard input.

Data Source
-----------
Two modes:
- **Demo Mode (default)**: use local hardcoded JSON dataset (no API keys).
- **Live Mode (optional)**: fetch movie metadata from TMDB or OMDB.

UI Requirements
---------------
- Overlay must be:
  - Small
  - Border-radius
  - Subtle shadow
  - Aligned exactly below Netflix search box
- No full-screen overlays
- No blocking input
- No visual clutter

Implementation Stack (suggested)
--------------------------------
Choose ONE primary language:
- Python (with pywin32 + UI Automation)
OR
- C# (.NET + UIAutomationClient)
OR
- C++ (Win32 + UIA)

Overlay window:
- Transparent
- Click-through outside component
- Always-on-top ONLY when Netflix is active
- Hidden otherwise

Deliverables
------------
1. Minimal working prototype code
2. Demo dataset JSON
3. README explaining:
   - How the Netflix app is detected
   - How search box is identified
   - How overlay positioning works
4. A short demo script for a 30–60 second screen recording:
   - Open Netflix app
   - Click search
   - Type `AI: horror movies`
   - Show suggestions
   - Use arrow keys + Enter
   - Netflix search results appear

Privacy & Safety
----------------
- Do not log keystrokes globally
- Only observe input when Netflix is focused
- No data sent externally in Demo mode

Acceptance Criteria
-------------------
- Works with Netflix desktop app (not browser)
- Overlay appears within 200ms after `AI:` is typed
- Keyboard navigation works
- Selecting a movie triggers Netflix search
- Clean and professional appearance suitable for PPT demo

bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
