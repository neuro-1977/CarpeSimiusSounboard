# Carpe Simius Soundboard

A simple, robust soundboard application that plays your local audio files.

## Setup

1.  **Place the Executable:** Put `CarpeSimiusSoundboard.exe` in a folder where you want to keep your soundboard.
2.  **Add Sounds:**
    *   Create a folder named `sounds` in the same directory as the `.exe`.
    *   Drag and drop your audio files (`.mp3`, `.wav`, `.ogg`) into this `sounds` folder.
3.  **Run:** Double-click `CarpeSimiusSoundboard.exe`.

## How to "Play Through Microphone"

To play sounds so others can hear them (e.g., in Discord, Zoom, Games), you need a **Virtual Audio Cable**.

1.  Install a Virtual Audio Cable driver (e.g., VB-Audio Cable).
2.  Open the Soundboard App.
3.  Click the **"Out: System Default"** button at the top left until it shows your Virtual Cable Input (e.g., "Out: CABLE Input").
4.  In your chat app (Discord, etc.), set your **Input Device** / Microphone to "CABLE Output".

Now, when you click a button, the sound travels through the virtual cable into your microphone channel.

## Features

*   **Auto-Grid:** Automatically creates buttons for every file in the `sounds` folder.
*   **Device Selector:** Click the top-left button to cycle through audio outputs (Speakers, Virtual Cables, etc.).
*   **Mute:** Top-right toggle to silence all audio immediately.
*   **Refresh:** Click the "Refresh" button to reload the sound list without restarting.
