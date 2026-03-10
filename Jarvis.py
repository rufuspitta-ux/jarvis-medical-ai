#!/usr/bin/env python3
"""
Advanced Autonomous Jarvis AI - Consolidated Single File
Medical Specialized AI Assistant
Python 3.11+ Compatible Version

This is a consolidated version of the Jarvis AI system in a single file.
"""

from __future__ import annotations
import sys
import os
import argparse
import subprocess
import threading
import time
import logging
import tkinter as tk
from contextlib import redirect_stderr
import io

# Configure logging to suppress warnings
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Dict, List, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from PIL import Image, ImageTk
except ImportError:
    pass

import math
import queue
import re
import random
import json
import sqlite3
import requests
from datetime import datetime as dt
import datetime

# Handle speech_recognition and pyaudio compatibility
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    nltk = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import numpy as np
except ImportError:
    pass

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    pycaw_available = True
except ImportError:
    pycaw_available = False

try:
    import requests
except ImportError:
    requests = None

try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None

# JarvisGUI class
class JarvisGUI:
    """
    Graphical user interface for Jarvis AI.
    Features animated elements, conversation display, and voice controls.
    """

    def __init__(self, jarvis_instance: JarvisAI) -> None:
        """
        Initialize the GUI.

        Args:
            jarvis_instance: Instance of the main JarvisAI class
        """
        self.jarvis = jarvis_instance
        self.logger = logging.getLogger('JarvisGUI')

        # GUI state
        self.root = None
        self.running = False
        self.animation_running = False

        # UI elements
        self.conversation_text = None
        self.input_entry = None
        self.send_button = None
        self.voice_button = None
        self.status_label = None

        # Animation variables
        self.pulse_angle = 0
        self.wave_points = []

        # Colors and styling
        self.colors = {
            'bg': '#1a1a2e',
            'fg': '#ffffff',
            'accent': '#16213e',
            'highlight': '#0f3460',
            'text': '#e94560'
        }

        self.fonts = {
            'main': ('Arial', 10),
            'title': ('Arial', 14, 'bold'),
            'input': ('Arial', 11)
        }

    def start(self) -> None:
        """Start the GUI."""
        self.running = True
        self.root = tk.Tk()
        self._setup_window()
        self._create_widgets()
        self._start_animations()

        # Start GUI main loop
        self.root.mainloop()

    def stop(self) -> None:
        """Stop the GUI."""
        self.running = False
        self.animation_running = False
        if self.root:
            self.root.quit()

    def _setup_window(self) -> None:
        """Setup the main window."""
        self.root.title("Jarvis AI - Advanced Autonomous Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors['bg'])
        self.root.resizable(True, True)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Jarvis AI Assistant",
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(0, 10))

        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready",
            font=self.fonts['main'],
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            relief=tk.RAISED
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        # Conversation display
        conversation_frame = tk.Frame(main_frame, bg=self.colors['accent'])
        conversation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.conversation_text = scrolledtext.ScrolledText(
            conversation_frame,
            wrap=tk.WORD,
            font=self.fonts['main'],
            bg=self.colors['highlight'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg']
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure tags for different message types
        self.conversation_text.tag_configure("user", foreground="#4CAF50", font=('Arial', 10, 'bold'))
        self.conversation_text.tag_configure("ai", foreground="#2196F3", font=('Arial', 10, 'bold'))
        self.conversation_text.tag_configure("system", foreground="#FF9800", font=('Arial', 9, 'italic'))

        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Input entry
        self.input_entry = tk.Entry(
            input_frame,
            font=self.fonts['input'],
            bg=self.colors['highlight'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg']
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self._on_send_message)

        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self._on_send_message,
            font=self.fonts['main'],
            bg=self.colors['text'],
            fg=self.colors['bg']
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X)

        # Voice control button
        self.voice_button = tk.Button(
            control_frame,
            text="🎤 Voice Mode",
            command=self._toggle_voice_mode,
            font=self.fonts['main'],
            bg=self.colors['highlight'],
            fg=self.colors['fg']
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 10))

        # Clear conversation button
        clear_button = tk.Button(
            control_frame,
            text="Clear Chat",
            command=self._clear_conversation,
            font=self.fonts['main'],
            bg=self.colors['accent'],
            fg=self.colors['fg']
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # Settings button
        settings_button = tk.Button(
            control_frame,
            text="Settings",
            command=self._show_settings,
            font=self.fonts['main'],
            bg=self.colors['accent'],
            fg=self.colors['fg']
        )
        settings_button.pack(side=tk.LEFT)

        # Animation canvas
        self.canvas = tk.Canvas(
            main_frame,
            height=50,
            bg=self.colors['bg'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.X, pady=(10, 0))

    def _start_animations(self) -> None:
        """Start GUI animations."""
        self.animation_running = True
        self._animate_pulse()
        self._animate_wave()

    def _animate_pulse(self) -> None:
        """Animate pulsing effect."""
        if not self.animation_running:
            return

        # Update pulse animation
        self.pulse_angle += 0.1
        intensity = (math.sin(self.pulse_angle) + 1) / 2  # 0 to 1

        # Change status bar color intensity
        r = int(22 + intensity * 33)  # 22 to 55
        g = int(26 + intensity * 38)  # 26 to 64
        b = int(46 + intensity * 52)  # 46 to 98

        color = f'#{r:02x}{g:02x}{b:02x}'
        self.status_label.configure(bg=color)

        # Schedule next animation frame
        self.root.after(50, self._animate_pulse)

    def _animate_wave(self) -> None:
        """Animate wave effect on canvas."""
        if not self.animation_running:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Create wave points
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width > 1:
            points = []
            for x in range(0, width, 10):
                y = height/2 + math.sin((x + self.pulse_angle * 50) * 0.02) * 10
                points.extend([x, y])

            if len(points) > 3:
                self.canvas.create_line(
                    points,
                    fill=self.colors['text'],
                    width=2,
                    smooth=True
                )

        # Schedule next animation frame
        self.root.after(50, self._animate_wave)

    def _on_send_message(self, event: Optional[Any] = None) -> None:
        """Handle send message event."""
        message = self.input_entry.get().strip()
        if message:
            self._process_user_input(message)
            self.input_entry.delete(0, tk.END)

    def _process_user_input(self, message: str) -> None:
        """Process user input and display response."""
        # Display user message
        self._add_message("You", message, "user")

        # Update status
        self.status_label.config(text="Processing...")

        # Process in separate thread to avoid blocking GUI
        def process():
            try:
                response = self.jarvis.process_text_command(message)
                self.root.after(0, lambda: self._add_message("Jarvis", response, "ai"))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
                # Automatically speak the response
                threading.Thread(target=self.jarvis.voice_engine.speak, args=(response,), daemon=True).start()
            except Exception as e:
                self.root.after(0, lambda: self._add_message("System", f"Error: {e}", "system"))
                self.root.after(0, lambda: self.status_label.config(text="Error"))

        threading.Thread(target=process, daemon=True).start()

    def _toggle_voice_mode(self) -> None:
        """Toggle voice mode on/off."""
        current_text = self.voice_button.cget("text")
        if "Voice Mode" in current_text:
            self.voice_button.config(text="🎤 Voice Active", bg=self.colors['text'], fg=self.colors['bg'])
            self.status_label.config(text="Voice mode activated")
            # Start voice listening
            self.jarvis.voice_engine.start_listening(self.jarvis._process_voice_command)
        else:
            self.voice_button.config(text="🎤 Voice Mode", bg=self.colors['highlight'], fg=self.colors['fg'])
            self.status_label.config(text="Voice mode deactivated")
            # Stop voice listening
            self.jarvis.voice_engine.stop_listening()

    def _clear_conversation(self) -> None:
        """Clear the conversation display."""
        self.conversation_text.delete(1.0, tk.END)
        self._add_message("System", "Conversation cleared", "system")

    def _show_settings(self) -> None:
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Jarvis Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])

        tk.Label(
            settings_window,
            text="Settings (Coming Soon)",
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)

    def _add_message(self, sender: str, message: str, tag: str) -> None:
        """Add a message to the conversation display."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"

        self.conversation_text.insert(tk.END, formatted_message, tag)
        self.conversation_text.see(tk.END)

    def update_response(self, response: str) -> None:
        """Update the GUI with a new response (called from Jarvis)."""
        if self.running:
            self.root.after(0, lambda: self._add_message("Jarvis", response, "ai"))

    def show_notification(self, title: str, message: str) -> None:
        """Show a notification dialog."""
        if self.running:
            self.root.after(0, lambda: messagebox.showinfo(title, message))

    def _on_closing(self) -> None:
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit Jarvis AI?"):
            self.stop()

    def update_status(self, status: str) -> None:
        """Update the status bar."""
        if self.running:
            self.root.after(0, lambda: self.status_label.config(text=status))

# VoiceEngine class
class VoiceEngine:
    """
    Voice engine for speech recognition and text-to-speech.
    Handles PyAudio compatibility for Python 3.11+
    """

    def __init__(self) -> None:
        """Initialize voice engine components."""
        self.logger = logging.getLogger('VoiceEngine')
        
        if sr is None:
            self.recognizer = None
            self.microphone_available = False
            self.logger.warning("Speech recognition not available")
        else:
            self.recognizer = sr.Recognizer()
            # Check microphone availability
            self.microphone_available = False
            try:
                with sr.Microphone() as source:
                    pass
                self.microphone_available = True
            except Exception as e:
                self.logger.warning(f"Microphone not available: {e}")
        
        if pyttsx3 is None:
            self.engine = None
            self.tts_available = False
            self.logger.warning("Text-to-speech not available")
        else:
            self.engine = pyttsx3.init()
            self.tts_available = True
        
        self.listening = False
        self.speaking_queue: queue.Queue[str] = queue.Queue()
        self.callback: Optional[Callable[[str], None]] = None
        self.listen_thread: Optional[threading.Thread] = None

        # Configure TTS
        self._configure_tts()

        # Start speaking thread
        self.speaking_thread = threading.Thread(target=self._speaking_worker, daemon=True)
        self.speaking_thread.start()

    def _configure_tts(self) -> None:
        """Configure text-to-speech engine."""
        if self.engine is None:
            return
        
        # Set Jarvis-like voice properties
        self.engine.setProperty('rate', 160)  # Slightly slower for Jarvis-like speech
        self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Try to select a male voice that sounds like Jarvis
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                # Look for a male voice, preferably with British accent
                jarvis_voice = None
                for voice in voices:
                    # On Windows, look for Microsoft voices
                    if hasattr(voice, 'name') and 'david' in voice.name.lower():
                        jarvis_voice = voice
                        break
                    elif hasattr(voice, 'name') and 'george' in voice.name.lower():
                        jarvis_voice = voice
                        break
                    elif hasattr(voice, 'name') and ('male' in voice.name.lower() or 'man' in voice.name.lower()):
                        jarvis_voice = voice
                        break
                
                # If no specific voice found, try the second voice (often male)
                if not jarvis_voice and len(voices) > 1:
                    jarvis_voice = voices[1]  # Usually male voice
                
                if jarvis_voice:
                    self.engine.setProperty('voice', jarvis_voice.id)
                    self.logger.info(f"Selected Jarvis-like voice: {jarvis_voice.name if hasattr(jarvis_voice, 'name') else jarvis_voice.id}")
        except Exception as e:
            self.logger.warning(f"Could not set Jarvis voice: {e}")

    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Start continuous listening for voice commands.

        Args:
            callback: Function to call with recognized text
        """
        if self.listening:
            return

        if not self.microphone_available:
            self.logger.error("Microphone not available, cannot start listening")
            return

        self.listening = True
        self.callback = callback

        # Start listening thread
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

    def stop_listening(self) -> None:
        """Stop listening for voice commands."""
        self.listening = False

    def _listen_loop(self) -> None:
        """Main listening loop."""
        if self.recognizer is None:
            self.logger.error("Speech recognizer not initialized")
            return
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.logger.info("Voice engine listening...")

            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio).lower()
                    self.logger.info(f"Recognized: {text}")
                    if self.callback:
                        self.callback(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.logger.error(f"Speech recognition error: {e}")
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Voice listening error: {e}")
                    time.sleep(1)

    def speak(self, text: str) -> None:
        """
        Speak text using text-to-speech.

        Args:
            text: Text to speak
        """
        if self.tts_available and self.engine is not None:
            try:
                # Process full text to ensure complete readout
                if text:
                    # Split long text into chunks for better handling
                    sentences = text.replace('\n', ' ').split('. ')
                    for sentence in sentences:
                        if sentence.strip():
                            self.engine.say(sentence.strip() + '.')
                    self.engine.runAndWait()
            except Exception as e:
                self.logger.error(f"Speech error: {e}")
        else:
            self.logger.warning("TTS not available")

    def _speaking_worker(self) -> None:
        """Worker thread for speaking."""
        if self.engine is None:
            return
        while True:
            try:
                text = self.speaking_queue.get(timeout=1)
                self.engine.say(text)
                self.engine.runAndWait()
                self.speaking_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Speech error: {e}")

    def stop(self) -> None:
        """Stop the voice engine."""
        self.stop_listening()
        if self.engine is not None:
            self.engine.stop()

# AIBrain class
class AIBrain:
    """
    Core AI brain that processes commands and makes decisions.
    Uses rule-based system with learning capabilities.
    """

    def __init__(self, memory_system: MemorySystem, medical_ai: MedicalAIModule) -> None:
        """
        Initialize AI brain.

        Args:
            memory_system: Memory system instance
            medical_ai: Medical AI module instance
        """
        self.memory = memory_system
        self.medical_ai = medical_ai
        self.logger = logging.getLogger('AIBrain')

        # GPT4All configuration
        self.gpt4all_available = False
        self.gpt4all_model_name = "orca-mini-3b.ggmlv3.q4_0.bin"  # Common model, change if needed
        
        if GPT4All is not None:
            # allow overriding with explicit local path
            custom_path = os.getenv("GPT4ALL_MODEL_PATH")
            if custom_path:
                if os.path.isfile(custom_path):
                    try:
                        with redirect_stderr(io.StringIO()):
                            self.model = GPT4All(custom_path, device='cpu')
                        self.gpt4all_available = True
                        self.logger.info(f"Loaded GPT4All model from custom path: {custom_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load GPT4All model from {custom_path}: {e}")
                else:
                    self.logger.warning(f"GPT4ALL_MODEL_PATH set but file does not exist: {custom_path}")

            if not self.gpt4all_available:
                try:
                    # Try to load the default model name
                    with redirect_stderr(io.StringIO()):
                        self.model = GPT4All(self.gpt4all_model_name, device='cpu')
                    self.gpt4all_available = True
                    self.logger.info(f"GPT4All model loaded: {self.gpt4all_model_name}")
                except Exception as e:
                    self.logger.warning(f"GPT4All model loading failed: {e}")
                    # Try to list available models on disk
                    try:
                        with redirect_stderr(io.StringIO()):
                            models = GPT4All.list_models()
                        if models:
                            self.gpt4all_model_name = models[0]['filename']
                            with redirect_stderr(io.StringIO()):
                                self.model = GPT4All(self.gpt4all_model_name, device='cpu')
                            self.gpt4all_available = True
                            self.logger.info(f"Using available GPT4All model: {self.gpt4all_model_name}")
                        else:
                            self.logger.warning("No GPT4All models available")
                    except Exception as e2:
                        self.logger.warning(f"Failed to list GPT4All models: {e2}")

        # Conversation context
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 5
        self.last_response: Optional[str] = None  # For repeat functionality

        # Command patterns and responses
        self.command_patterns: Dict[str, List[str]] = {
            'greeting': [
                r'\b(hello|hi|hey|greetings|good\s+(morning|afternoon|evening)|what\'?s\s+up|howdy)\b'
            ],
            'time': [
                r'\b(what\s+time|current\s+time|time\s+now|what\s+time\s+is\s+it|time)\b'
            ],
            'date': [
                r'\b(what\s+date|current\s+date|today\'?s?\s+date|what\s+day\s+is\s+it|date|today)\b'
            ],
            'weather': [
                r'\b(weather|forecast|temperature|is\s+it\s+(hot|cold|rainy|sunny))\b'
            ],
            'search': [
                r'\b(search|find|look\s+up|google|tell\s+me\s+about)\b'
            ],
            'open': [
                r'\b(open|launch|start|run)\b'
            ],
            'medical': [
                r'\b(medical|health|symptoms|treatment|disease|pain|fever|cough|headache|sore\s+throat|nausea|fatigue|hypertension|diabetes|asthma|arthritis|cancer|heart|stroke|depression|anxiety)\b'
            ],
            'question': [
                r'\b(what|how|why|when|where|who|which|can|do|is|are|does|should|will)\b.*\?'
            ],
            'how_are_you': [
                r'\b(how\s+are\s+you|how\s+do\s+you\s+do|what\'?s\s+up|how\s+you\s+doing)\b'
            ],
            'thanks': [
                r'\b(thank\s+you|thanks|thx|ty|appreciate\s+it|grateful)\b'
            ],
            'volume': [
                r'\b(volume|sound|audio)\b.*\b(up|down|increase|decrease|mute|unmute|louder|quieter)\b'
            ],
            'screenshot': [
                r'\b(screenshot|screen\s+shot|capture\s+screen|take\s+a\s+picture)\b'
            ],
            'shutdown': [
                r'\b(shutdown|turn\s+off|power\s+off|quit|exit)\b'
            ],
            'restart': [
                r'\b(restart|reboot|reset)\b'
            ],
            'joke': [
                r'\b(tell\s+me\s+a\s+joke|joke|funny|make\s+me\s+laugh)\b'
            ],
            'reminder': [
                r'\b(remind\s+me|set\s+a\s+reminder|reminder|don\'?t\s+forget)\b'
            ],
            'help': [
                r'\b(help|assist|support)\b'
            ],
            'name': [
                r'\b(what\s+is\s+your\s+name|who\s+are\s+you|your\s+name)\b'
            ],
            'capabilities': [
                r'\b(what\s+can\s+you\s+do|your\s+abilities|features|what\s+you\s+can\s+do|what\s+are\s+your\s+abilities|what\s+do\s+you\s+do|specifications|specs|abilities|abilitys)\b'
            ],
            'goodbye': [
                r'\b(bye|goodbye|see\s+you|later|farewell)\b'
            ],
            'compliment': [
                r'\b(you\'?re\s+(awesome|great|amazing|smart|helpful)|good\s+job|well\s+done)\b'
            ],
            'casual': [
                r'\b(nice|cool|awesome|wow|oh|really|interesting)\b'
            ],
            'tell_me': [
                r'\b(tell\s+me|can\s+you\s+tell\s+me|let\s+me\s+know)\b'
            ],
            'explain': [
                r'\b(explain|what\s+is|how\s+does|why\s+does)\b'
            ],
            'what_is': [
                r'\b(what\s+is|define|meaning\s+of)\b'
            ],
            'general_chat': [
                r'\b(i\s+(think|feel|want|need|like|love|hate)|my\s+(day|life|work)|today|tomorrow|yesterday)\b'
            ],
            'emotion': [
                r'\b(i\s+(am|feel)\s+(happy|sad|angry|excited|worried|stressed|tired|bored)|i\s+love|i\s+hate)\b'
            ],
            'opinion': [
                r'\b(what\s+do\s+you\s+think|do\s+you\s+(like|love|hate|prefer)|your\s+opinion|what\s+about\s+you)\b'
            ],
            'story': [
                r'\b(tell\s+me\s+a\s+story|story|once\s+upon\s+a\s+time|share\s+a\s+story)\b'
            ],
            'personal': [
                r'\b(how\s+old\s+are\s+you|where\s+are\s+you\s+from|what\s+do\s+you\s+do|your\s+hobbies)\b'
            ],
            'hobby': [
                r'\b(do\s+you\s+(play|like|enjoy)|what\s+do\s+you\s+do\s+for\s+fun|hobbies|interests)\b'
            ]
        }

        # Response templates
        self.responses: Dict[str, List[str]] = {
            'greeting': [
                "Hello! How can I assist you today?",
                "Hi there! What can I do for you?",
                "Greetings! I'm here to help with anything you need.",
                "Hello! Ready to help - what would you like to know?",
                "Hey! How's it going? What can I help with?"
            ],
            'time': [
                "The current time is {time}.",
                "It's {time} right now.",
                "The time is {time}.",
                "Right now it's {time}."
            ],
            'date': [
                "Today is {date}.",
                "The date is {date}.",
                "It's {date} today.",
                "We're looking at {date}."
            ],
            'how_are_you': [
                "I'm doing well, thank you! How can I help you?",
                "I'm functioning optimally. What can I assist with?",
                "I'm great! Ready to help with whatever you need.",
                "I'm excellent, thanks for asking! How about you?"
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "Anytime!",
                "Glad I could assist.",
                "No problem at all!",
                "My pleasure!"
            ],
            'question': [
                "That's an interesting question. Let me help with that.",
                "Good question! Based on what I know...",
                "I'd be happy to help with that.",
                "Let me see what I can tell you about that."
            ],
            'volume': [
                "I'll adjust the volume for you.",
                "Volume control activated.",
                "Adjusting audio settings.",
                "Got it, changing the volume."
            ],
            'screenshot': [
                "Taking a screenshot now.",
                "Screen captured.",
                "Screenshot saved.",
                "Captured the screen for you."
            ],
            'shutdown': [
                "Initiating system shutdown.",
                "Shutting down the computer.",
                "Goodbye!",
                "See you later!"
            ],
            'restart': [
                "Restarting the system.",
                "Rebooting now.",
                "System restart initiated.",
                "Restarting as requested."
            ],
            'joke': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call fake spaghetti? An impasta!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "Why don't eggs tell jokes? They'd crack each other up!",
                "What do you call a bear with no teeth? A gummy bear!"
            ],
            'reminder': [
                "I'll help you set a reminder.",
                "Reminder system activated.",
                "What would you like me to remind you about?",
                "Sure, I can set a reminder for you."
            ],
            'help': [
                "I can help with medical information, general questions, system controls, and more. Just ask!",
                "I'm here to assist with health queries, daily tasks, and information. What do you need?",
                "I can provide medical knowledge, answer questions, control your computer, and have conversations. How can I help?"
            ],
            'name': [
                "I'm Jarvis, your advanced AI assistant!",
                "You can call me Jarvis. I'm here to help!",
                "My name is Jarvis - nice to meet you!"
            ],
            'capabilities': [
                "I am Jarvis, an advanced AI assistant with comprehensive medical knowledge and general capabilities. Here's what I can do:",
                "",
                "🩺 MEDICAL EXPERTISE:",
                "• Answer medical questions and provide health information",
                "• Explain symptoms, diseases, and treatments",
                "• Check drug interactions and medication details",
                "• Access telemedicine services and emergency protocols",
                "• Provide preventive care guidance and health calculators",
                "",
                "💬 GENERAL ASSISTANCE:",
                "• Have natural conversations and answer questions",
                "• Tell time, date, and provide information",
                "• Set reminders and manage tasks",
                "• Control system functions (volume, screenshots, apps)",
                "• Search the web and open applications",
                "",
                "🎤 VOICE FEATURES:",
                "• Voice recognition and text-to-speech",
                "• Hands-free interaction",
                "",
                "🧠 SMART FEATURES:",
                "• Learn from conversations and remember preferences",
                "• Contextual responses based on your input",
                "• Emergency detection and appropriate responses",
                "",
                "Just ask me anything - I'm here to help! What would you like to know?"
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later!",
                "Take care!",
                "Farewell!"
            ],
            'compliment': [
                "Thank you! I appreciate that.",
                "Thanks! I'm glad I could help.",
                "You're too kind! Happy to assist."
            ],
            'casual': [
                "Glad you think so!",
                "Thanks for the feedback!",
                "I appreciate that!"
            ],
            'tell_me': [
                "Sure, I'd be happy to tell you!",
                "Let me share that information with you.",
                "Here's what I know about that."
            ],
            'explain': [
                "Let me explain that for you.",
                "I'll break it down for you.",
                "Here's how it works."
            ],
            'what_is': [
                "That's a great question! Let me define it for you.",
                "Here's the definition.",
                "Let me explain what that means."
            ],
            'general_chat': [
                "That sounds interesting! Tell me more.",
                "I understand. How can I help with that?",
                "Thanks for sharing. Is there anything specific you'd like to know?",
                "I hear you. What else is on your mind?"
            ],
            'emotion': [
                "I'm glad you're feeling that way!",
                "That's great to hear!",
                "I'm here if you want to talk about it.",
                "Emotions are important. How can I help?"
            ],
            'opinion': [
                "That's an interesting perspective!",
                "I think that's a valid point.",
                "As an AI, I don't have personal opinions, but I can discuss it.",
                "What do you think about it?"
            ],
            'story': [
                "Sure, let me tell you a short story.",
                "Once upon a time, in a digital world...",
                "Here's a quick tale: There was once an AI who loved helping people.",
                "Story time! Let me share something fun."
            ],
            'personal': [
                "I'm Jarvis, an AI assistant created to help people.",
                "I'm from the digital realm, always ready to assist.",
                "I'm designed to be helpful and knowledgeable.",
                "I'm an AI, so I don't have an age, but I'm always learning!"
            ],
            'hobby': [
                "As an AI, my 'hobby' is helping people and learning new things.",
                "I enjoy processing information and solving problems.",
                "I like chatting with users like you!",
                "My interests include technology, health, and assisting humans."
            ],
            'unknown': [
                "That's interesting! Can you tell me more about that?",
                "I'm curious about what you mean. Could you elaborate?",
                "I'd love to help with that. What specifically are you asking?",
                "Hmm, I'm not entirely sure, but I'm here to chat! What's on your mind?",
                "Let's talk about that. Can you give me more details?"
            ]
        }

    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command and return response.

        Args:
            command: Input command

        Returns:
            Response with text, task info, etc.
        """
        command = command.lower().strip()

        # Store in memory
        self.memory.store_interaction(command, "user")

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": command})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        # Check for repeat command
        if any(word in command for word in ['repeat', 'say again', 'say that again', 'what did you say']):
            if self.last_response:
                response_text = self.last_response
            else:
                response_text = "I haven't said anything yet to repeat."
        # Check for medical queries first (including single disease names)
        elif any(re.search(pattern, command) for pattern in self.command_patterns['medical']) or self._is_disease_query(command):
            response_text = self.medical_ai.query(command)
        else:
            # Check other patterns
            response_text = self._match_patterns(command)

        # Check for name introduction
        name_match = re.search(r'my\s+name\s+is\s+(\w+)', command)
        if name_match:
            name = name_match.group(1)
            self.store_user_preference("name", name)
            response_text += f" Nice to meet you, {name}!"

        # Personalize response with name if known
        user_name = self.get_user_preference("name")
        if user_name and random.random() < 0.3:  # 30% chance to use name
            response_text = f"{user_name}, {response_text.lower()}"

        # Generate response
        response = {
            'text': response_text,
            'speak': True,
            'task': self._extract_task(command)
        }

        # Store response and update last response for repeat
        self.memory.store_interaction(response_text, "ai")
        self.last_response = response_text

        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response_text})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        return response

    def _is_disease_query(self, command: str) -> bool:
        """Check if command is asking about a disease."""
        diseases = ['cancer', 'diabetes', 'heart disease', 'hypertension', 'asthma', 'arthritis', 
                   'stroke', 'pneumonia', 'flu', 'covid', 'depression', 'anxiety', 'alzheimer', 
                   'parkinson', 'hepatitis', 'tuberculosis', 'malaria', 'ulcer', 'psoriasis']
        # Check if disease name appears in command
        for disease in diseases:
            if disease in command:
                return True
        return False

    def _match_patterns(self, command: str) -> str:
        """Match command against known patterns with improved logic."""
        # First priority: medical queries
        if any(re.search(pattern, command) for pattern in self.command_patterns.get('medical', [])) or self._is_disease_query(command):
            return self.medical_ai.query(command)
        
        # Check for 'open' command with specific apps
        if 'open' in command or 'launch' in command or 'start' in command:
            return self._handle_open_command(command)
        
        # Check for 'explain' with medical context
        if 'explain' in command:
            # Check if explaining a disease
            if self._is_disease_query(command):
                return self.medical_ai.query(command)
            # Otherwise provide generic explain response  
            return self._generate_response('explain')
        
        # Check specific patterns
        for category, patterns in self.command_patterns.items():
            if category in ['medical', 'open', 'explain']:
                continue  # Already handled above
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return self._generate_response(category)
        
        # Fast fallback - respond to any text
        return self._generate_contextual_response(command)

    def _handle_open_command(self, command: str) -> str:
        """Handle open/launch/start commands smartly."""
        apps = ['notepad', 'chrome', 'firefox', 'edge', 'calculator', 'paint', 'word', 'excel']
        for app in apps:
            if app in command:
                return f"I'll open {app} for you now."
        return "I'll help you open an application. Which one would you like?"
    
    def _generate_contextual_response(self, text: str) -> str:
        """Generate contextual response for any text input."""
        text_lower = text.lower()
        
        # Check for keywords and generate relevant responses
        if any(word in text_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
            return random.choice(self.responses['thanks'])
        elif any(word in text_lower for word in ['hello', 'hi', 'hey', 'greet']):
            return random.choice(self.responses['greeting'])
        elif '?' in text:
            return random.choice(self.responses['question'])
        elif any(word in text_lower for word in ['bye', 'goodbye', 'farewell', 'see you']):
            return random.choice(self.responses['goodbye'])
        elif any(word in text_lower for word in ['love', 'awesome', 'amazing', 'great', 'wonderful']):
            return random.choice(self.responses['compliment'])
        elif len(text) > 50:
            # Longer inputs - show interest
            return "That's very interesting! Can you tell me more about it? I'd like to understand better."
        else:
            # Default engaging response
            return random.choice(self.responses['unknown'])

    def _generate_response(self, category: str) -> str:
        """Generate response for a category with context awareness."""
        if category == 'time':
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return random.choice(self.responses['time']).format(time=current_time)
        elif category == 'date':
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            return random.choice(self.responses['date']).format(date=current_date)
        elif category == 'medical':
            return self.medical_ai.query(self.conversation_history[-1]['content'] if self.conversation_history else "")
        elif category == 'capabilities':
            # Join all capability lines for complete response
            return '\n'.join(self.responses['capabilities'])
        elif category in ['greeting', 'how_are_you', 'thanks', 'question', 'volume', 'screenshot', 'shutdown', 'restart', 'joke', 'reminder', 'help', 'name', 'goodbye', 'compliment', 'casual', 'tell_me', 'explain', 'what_is', 'general_chat', 'emotion', 'opinion', 'story', 'personal', 'hobby']:
            return random.choice(self.responses[category])
        else:
            return random.choice(self.responses['unknown'])

    def _add_context(self, response: str) -> str:
        """Add context-aware elements to response."""
        # Simple context: if user asked about time/date before, acknowledge continuity
        recent_messages = [msg for msg in self.conversation_history[-3:] if msg["role"] == "user"]
        
        if len(recent_messages) > 1:
            # Check for repeated topics
            if any("time" in msg["content"] for msg in recent_messages) and "time" in response.lower():
                response = "As I mentioned earlier, " + response.lower()
            elif any("date" in msg["content"] for msg in recent_messages) and "date" in response.lower():
                response = "Just to confirm, " + response.lower()
        
        return response

    def store_user_preference(self, key: str, value: str) -> None:
        """Store user preference."""
        self.memory.store_preference(f"user_{key}", value)

    def get_user_preference(self, key: str) -> Optional[str]:
        """Get user preference."""
        return self.memory.get_preference(f"user_{key}")

    def _query_gpt4all(self, prompt: str) -> str:
        """Query GPT4All for AI-like response."""
        if not self.gpt4all_available:
            return "GPT4All not available for advanced responses."
        try:
            # Generate response
            with self.model.chat_session():
                response = self.model.generate(prompt, max_tokens=200)
            return response.strip()
        except Exception as e:
            return f"GPT4All query failed: {e}"

    def _extract_task(self, command: str) -> Optional[Dict[str, Any]]:
        """Extract task information from command."""
        # Simple task extraction with improved app detection
        if 'open' in command or 'launch' in command or 'start' in command:
            apps = {'chrome': 'chrome', 'browser': 'chrome', 'firefox': 'firefox', 
                   'notepad': 'notepad', 'editor': 'notepad', 'calculator': 'calc',
                   'paint': 'paint', 'word': 'winword', 'excel': 'excel'}
            for keyword, app in apps.items():
                if keyword in command:
                    return {'type': 'open_app', 'app': app}
        elif 'search' in command or 'google' in command or 'find' in command or 'look up' in command:
            query = command.replace('search', '').replace('google', '').replace('find', '').replace('look up', '').strip()
            if query:
                return {'type': 'web_search', 'query': query}
        elif 'volume' in command:
            if 'up' in command or 'increase' in command or 'louder' in command:
                return {'type': 'volume', 'action': 'up'}
            elif 'down' in command or 'decrease' in command or 'quieter' in command:
                return {'type': 'volume', 'action': 'down'}
            elif 'mute' in command or 'silent' in command:
                return {'type': 'volume', 'action': 'mute'}
        elif 'screenshot' in command or 'screen shot' in command or 'capture' in command:
            return {'type': 'screenshot'}
        elif 'shutdown' in command or 'turn off' in command or 'power off' in command:
            return {'type': 'shutdown'}
        elif 'restart' in command or 'reboot' in command or 'reset' in command:
            return {'type': 'restart'}
        elif 'reminder' in command or 'remind' in command:
            return {'type': 'reminder', 'command': command}

        return None

# TaskExecutor class
class TaskExecutor:
    """
    Task execution and automation system.
    """

    def __init__(self) -> None:
        """Initialize task executor."""
        self.logger = logging.getLogger('TaskExecutor')

    def execute_task(self, task: Optional[Dict[str, Any]]) -> None:
        """
        Execute a task.

        Args:
            task: Task information
        """
        if not task:
            return

        task_type = task.get('type')
        if task_type == 'open_app':
            self._open_application(task.get('app'))
        elif task_type == 'web_search':
            self._perform_web_search(task.get('query'))
        elif task_type == 'volume':
            self._adjust_volume(task.get('action'))
        elif task_type == 'screenshot':
            self._take_screenshot()
        elif task_type == 'shutdown':
            self._shutdown_system()
        elif task_type == 'restart':
            self._restart_system()
        elif task_type == 'reminder':
            self._set_reminder(task.get('command'))

    def _open_application(self, app_name: Optional[str]) -> None:
        """Open an application."""
        if not app_name:
            return

        try:
            if app_name == 'chrome':
                os.system('start chrome')
            elif app_name == 'notepad':
                os.system('start notepad')
            self.logger.info(f"Opened {app_name}")
        except Exception as e:
            self.logger.error(f"Failed to open {app_name}: {e}")

    def _perform_web_search(self, query: Optional[str]) -> None:
        """Perform web search."""
        if not query:
            return
        try:
            import webbrowser
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            self.logger.info(f"Searched for: {query}")
        except Exception as e:
            self.logger.error(f"Failed to search: {e}")

    def _adjust_volume(self, action: Optional[str]) -> None:
        """Adjust system volume."""
        if not pycaw_available:
            self.logger.warning("Volume control not available - pycaw not installed")
            return
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            if action == 'up':
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
            elif action == 'down':
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
            elif action == 'mute':
                volume.SetMute(not volume.GetMute(), None)
            
            self.logger.info(f"Volume adjusted: {action}")
        except Exception as e:
            self.logger.error(f"Failed to adjust volume: {e}")

    def _take_screenshot(self) -> None:
        """Take a screenshot."""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot.save(filename)
            self.logger.info(f"Screenshot saved as {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")

    def _shutdown_system(self) -> None:
        """Shutdown the system."""
        try:
            os.system('shutdown /s /t 30')  # Shutdown in 30 seconds
            self.logger.info("System shutdown initiated")
        except Exception as e:
            self.logger.error(f"Failed to shutdown: {e}")

    def _restart_system(self) -> None:
        """Restart the system."""
        try:
            os.system('shutdown /r /t 30')  # Restart in 30 seconds
            self.logger.info("System restart initiated")
        except Exception as e:
            self.logger.error(f"Failed to restart: {e}")

    def _set_reminder(self, command: str) -> None:
        """Set a reminder (placeholder)."""
        # This would require a more complex implementation
        self.logger.info(f"Reminder requested: {command}")
        # For now, just log it

# MemorySystem class
class MemorySystem:
    """
    Persistent memory and learning system.
    """

    def __init__(self) -> None:
        """Initialize memory system."""
        self.logger = logging.getLogger('MemorySystem')
        self.db_path = 'jarvis_memory.db'
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS interactions
                     (id INTEGER PRIMARY KEY, timestamp TEXT, type TEXT, content TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS preferences
                     (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()

    def store_interaction(self, content: str, type_: str) -> None:
        """Store an interaction."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO interactions (timestamp, type, content) VALUES (?, ?, ?)",
                  (timestamp, type_, content))
        conn.commit()
        conn.close()

    def get_recent_interactions(self, limit: int = 10) -> List[tuple]:
        """Get recent interactions."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
        results = c.fetchall()
        conn.close()
        return results

    def store_preference(self, key: str, value: str) -> None:
        """Store a preference."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    def get_preference(self, key: str) -> Optional[str]:
        """Get a preference."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def start(self) -> None:
        """Start memory system."""
        pass

    def stop(self) -> None:
        """Stop memory system."""
        pass

# MedicalAIModule class
class MedicalAIModule:
    """
    Advanced Medical AI module that handles comprehensive health-related queries.
    Features: symptom analysis, drug interactions, medical calculators, emergency response.
    """

    def __init__(self) -> None:
        """Initialize advanced medical AI module."""
        self.logger = logging.getLogger('MedicalAI')
        self.knowledge_base: Dict[str, Dict[str, Any]] = self._load_knowledge_base()
        self.patient_history: Dict[str, Any] = {}  # For tracking user health data
        self.emergency_keywords = [
            'chest pain', 'difficulty breathing', 'severe bleeding', 'unconscious',
            'heart attack', 'stroke symptoms', 'severe allergic reaction', 'poisoning'
        ]

    def _load_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive medical knowledge base with advanced features and latest telemedicines."""
        return {
            'telemedicine_services': {
                'Teladoc': {'specialties': ['General Medicine', 'Dermatology', 'Behavioral Health'], 'wait_time': '15-30 min', 'available_24_7': True},
                'MDLIVE': {'specialties': ['Urgent Care', 'Behavioral Health', 'Chronic Conditions'], 'wait_time': '10-20 min', 'available_24_7': True},
                'Amwell': {'specialties': ['Primary Care', 'Specialists', 'Behavioral Health'], 'wait_time': '20-45 min', 'available_24_7': False},
                'Doctor On Demand': {'specialties': ['General Medicine', 'Dermatology', 'Behavioral Health'], 'wait_time': '15-30 min', 'available_24_7': True},
                'Ro': {'specialties': ['GLP-1 Weight Loss', 'Hair Loss', 'Dermatology'], 'wait_time': 'Asynchronous', 'available_24_7': True},
                'Keeps': {'specialties': ['Hair Loss Treatment'], 'wait_time': 'Online evaluation', 'available_24_7': True},
                'GoodRx Telehealth': {'specialties': ['Urgent Care', 'Prescriptions'], 'wait_time': '15-30 min', 'available_24_7': True},
                'Amazon Clinic': {'specialties': ['General Medicine', 'Urgent Care'], 'wait_time': '10-30 min', 'available_24_7': True},
                'CVS MinuteClinic': {'specialties': ['Urgent Care', 'Vaccinations', 'Basic Care'], 'locations': 'In-store available', 'available_24_7': False},
                'Walgreens Virtual': {'specialties': ['Primary Care', 'Urgent Care'], 'wait_time': '15-30 min', 'available_24_7': True}
            },
            'symptoms': {
                'headache': {
                    'description': 'Pain in the head or neck area',
                    'common_causes': ['Stress', 'Dehydration', 'Lack of sleep', 'Eye strain', 'Migraine', 'Tension', 'Sinus infection'],
                    'home_remedies': ['Rest in dark room', 'Hydrate', 'Apply cold compress', 'Take pain reliever', 'Massage temples', 'Caffeine (in moderation)'],
                    'when_to_see_doctor': ['Severe pain', 'With nausea/vomiting', 'After head injury', 'Frequent occurrence', 'Vision changes', 'Neurological symptoms'],
                    'severity_levels': {'mild': 'Over-the-counter remedies', 'moderate': 'Prescription medication', 'severe': 'Immediate medical attention'},
                    'associated_conditions': ['Migraine', 'Tension headache', 'Cluster headache', 'Sinusitis']
                },
                'chest pain': {
                    'description': 'Pain or discomfort in the chest area',
                    'common_causes': ['Heart attack', 'Angina', 'GERD', 'Pneumonia', 'Anxiety', 'Muscle strain', 'Costochondritis'],
                    'home_remedies': ['Rest', 'Over-the-counter pain relievers', 'Warm compress'],
                    'when_to_see_doctor': ['Severe pain', 'Shortness of breath', 'Dizziness', 'Nausea', 'Sweating', 'Call emergency if suspected heart attack'],
                    'emergency': True,
                    'red_flags': ['Radiating pain to arm/jaw', 'Shortness of breath', 'Sweating', 'Nausea']
                },
                'abdominal pain': {
                    'description': 'Pain in the stomach or abdominal area',
                    'common_causes': ['Indigestion', 'Gas', 'Constipation', 'Food poisoning', 'Appendicitis', 'Gallstones', 'Ulcer', 'IBS', 'Crohn\'s disease'],
                    'home_remedies': ['Rest', 'Clear fluids', 'Over-the-counter antacids', 'Heat pad', 'Small meals'],
                    'when_to_see_doctor': ['Severe pain', 'Fever', 'Vomiting', 'Blood in stool', 'Pain lasts >24 hours', 'Pain in lower right quadrant'],
                    'severity_levels': {'mild': 'Home remedies', 'moderate': 'Medical evaluation', 'severe': 'Emergency care'},
                    'associated_conditions': ['Appendicitis', 'Cholecystitis', 'Diverticulitis', 'Gastroenteritis']
                },
                'fatigue': {
                    'description': 'Persistent tiredness and lack of energy',
                    'common_causes': ['Sleep deprivation', 'Anemia', 'Thyroid disorder', 'Depression', 'Chronic illness', 'Medications'],
                    'home_remedies': ['Adequate sleep', 'Regular exercise', 'Balanced diet', 'Stress management'],
                    'when_to_see_doctor': ['Persistent for >2 weeks', 'With fever/weight loss', 'Affecting daily activities']
                },
                'fever': {
                    'description': 'Elevated body temperature above 98.6°F (37°C)',
                    'common_causes': ['Infection', 'Influenza', 'Common cold', 'COVID-19', 'Strep throat'],
                    'home_remedies': ['Rest', 'Fluids', 'Acetaminophen or ibuprofen', 'Cool compress'],
                    'when_to_see_doctor': ['>103°F', 'In infants <3 months', 'With severe symptoms', 'Lasting >3 days']
                },
                'cough': {
                    'description': 'Involuntary expulsion of air from lungs',
                    'common_causes': ['Common cold', 'Flu', 'Bronchitis', 'Pneumonia', 'Asthma', 'Allergies'],
                    'home_remedies': ['Honey', 'Cough drops', 'Humidifier', 'Fluids', 'Rest'],
                    'when_to_see_doctor': ['With bloody sputum', 'With chest pain', 'Lasting >3 weeks', 'Difficulty breathing']
                },
                'sore throat': {
                    'description': 'Pain or irritation in the throat',
                    'common_causes': ['Strep throat', 'Cold', 'Flu', 'Allergies', 'Tonsillitis'],
                    'home_remedies': ['Warm salt water gargle', 'Throat lozenges', 'Fluids', 'Rest', 'Humidifier'],
                    'when_to_see_doctor': ['Severe pain', 'Difficulty swallowing', 'With fever', 'Lasting >7 days']
                },
                'nausea': {
                    'description': 'Feeling of discomfort and urge to vomit',
                    'common_causes': ['Food poisoning', 'Gastroenteritis', 'Medication side effects', 'Pregnancy', 'Migraines'],
                    'home_remedies': ['Ginger', 'Peppermint', 'Small frequent meals', 'Hydration', 'Rest'],
                    'when_to_see_doctor': ['With severe vomiting', 'Lasting >24 hours', 'With abdominal pain']
                }
            },
            'diseases': {
                'diabetes': {
                    'description': 'Chronic condition affecting blood sugar regulation',
                    'types': ['Type 1', 'Type 2', 'Gestational', 'Type 1.5 (LADA)', 'Neonatal'],
                    'symptoms': ['Frequent urination', 'Excessive thirst', 'Fatigue', 'Blurred vision', 'Slow healing', 'Tingling/numbness', 'Increased hunger'],
                    'treatment': ['Insulin', 'Metformin', 'GLP-1 agonists', 'SGLT2 inhibitors', 'DPP-4 inhibitors', 'Diet', 'Exercise'],
                    'complications': ['Heart disease', 'Kidney damage', 'Nerve damage', 'Eye problems', 'Foot ulcers', 'Stroke', 'Neuropathy'],
                    'prevention': ['Healthy diet', 'Regular exercise', 'Weight management', 'Regular screening', 'Blood pressure control'],
                    'management_goals': ['HbA1c <7%', 'Blood pressure <130/80', 'Cholesterol <100 LDL'],
                    'latest_treatment': ['Continuous glucose monitoring', 'Insulin pumps', 'Hybrid closed-loop systems']
                },
                'hypertension': {
                    'description': 'High blood pressure (>130/80 mmHg)',
                    'causes': ['Genetics', 'Diet high in sodium', 'Obesity', 'Stress', 'Medical conditions', 'Age', 'Sedentary lifestyle'],
                    'symptoms': ['Often asymptomatic', 'Headaches', 'Dizziness', 'Chest pain', 'Shortness of breath', 'Nosebleeds'],
                    'treatment': ['ACE inhibitors', 'Beta-blockers', 'Calcium channel blockers', 'Thiazide diuretics', 'ARBs'],
                    'complications': ['Heart attack', 'Stroke', 'Kidney damage', 'Vision loss', 'Aortic aneurysm'],
                    'target_bp': ['<120/80 mmHg (normal)', '<130/80 mmHg (with risk factors)', '<140/90 mmHg (elderly)'],
                    'lifestyle_modifications': ['DASH diet', 'Reduce sodium', 'Regular exercise', 'Weight loss', 'Stress management']
                },
                'coronary artery disease': {
                    'description': 'Narrowing of coronary arteries reducing blood flow to heart',
                    'risk_factors': ['High cholesterol', 'Hypertension', 'Smoking', 'Diabetes', 'Family history', 'Age', 'Obesity', 'Sedentary lifestyle'],
                    'symptoms': ['Chest pain (angina)', 'Shortness of breath', 'Fatigue', 'Heart palpitations', 'Sweating'],
                    'diagnosis': ['ECG', 'Stress test', 'Cardiac catheterization', 'CT angiogram', 'Troponin levels'],
                    'treatment': ['Medications (statins, beta-blockers)', 'Angioplasty', 'Stent placement', 'Bypass surgery', 'Lifestyle changes'],
                    'prevention': ['Heart-healthy diet', 'Exercise', 'Smoking cessation', 'Cholesterol management', 'BP control']
                },
                'asthma': {
                    'description': 'Chronic inflammatory airway disease',
                    'types': ['Allergic', 'Non-allergic', 'Exercise-induced', 'Occupational', 'Severe asthma'],
                    'symptoms': ['Wheezing', 'Shortness of breath', 'Coughing (especially at night)', 'Chest tightness'],
                    'triggers': ['Allergens', 'Exercise', 'Cold air', 'Infections', 'Air pollution', 'Stress'],
                    'treatment': ['Rescue inhalers (albuterol)', 'Controller inhalers (steroids)', 'Long-acting bronchodilators', 'Biologics'],
                    'management': ['Asthma action plan', 'Peak flow monitoring', 'Trigger avoidance'],
                    'latest_treatment': ['Monoclonal antibodies (Dupilumab, Omalizumab)', 'LTRA']
                },
                'copd': {
                    'description': 'Chronic Obstructive Pulmonary Disease',
                    'types': ['Emphysema', 'Chronic bronchitis'],
                    'symptoms': ['Persistent cough', 'Shortness of breath', 'Wheezing', 'Chest tightness', 'Fatigue'],
                    'causes': ['Smoking', 'Air pollution', 'Genetic (Alpha-1 antitrypsin deficiency)'],
                    'treatment': ['Bronchodilators', 'Corticosteroids', 'Oxygen therapy', 'Vaccines', 'Pulmonary rehabilitation'],
                    'screening': ['Spirometry test', 'GOLD criteria']
                },
                'heart failure': {
                    'description': 'Heart unable to pump blood effectively',
                    'types': ['HFrEF (reduced ejection fraction)', 'HFpEF (preserved ejection fraction)', 'HFmrEF (mildly reduced)'],
                    'symptoms': ['Shortness of breath', 'Fatigue', 'Edema', 'Frequent urination', 'Rapid/weak pulse'],
                    'causes': ['CAD', 'Hypertension', 'Cardiomyopathy', 'Valve disease', 'Arrhythmias'],
                    'treatment': ['ACE inhibitors', 'Beta-blockers', 'Aldosterone antagonists', 'SGLT2 inhibitors', 'Diuretics'],
                    'staging': ['Stage A (at risk)', 'Stage B (structural)', 'Stage C (symptoms)', 'Stage D (advanced)']
                },
                'stroke': {
                    'description': 'Loss of blood flow to the brain',
                    'types': ['Ischemic (85%)', 'Hemorrhagic (15%)'],
                    'risk_factors': ['Hypertension', 'Atrial fibrillation', 'Diabetes', 'High cholesterol', 'Smoking', 'Obesity'],
                    'symptoms': ['Sudden weakness/numbness', 'Trouble speaking', 'Vision problems', 'Dizziness', 'Severe headache'],
                    'treatment': ['tPA (thrombolytic)', 'Thrombectomy', 'Antiplatelet drugs', 'Anticoagulants'],
                    'assessment': ['FAST: Face drooping, Arm weakness, Speech difficulty, Time'],
                    'prevention': ['BP control', 'Antiplatelet therapy', 'Afib management', 'Lifestyle changes']
                },
                'atrial fibrillation': {
                    'description': 'Irregular heart rhythm in the atria',
                    'types': ['Paroxysmal', 'Persistent', 'Permanent'],
                    'symptoms': ['Heart palpitations', 'Shortness of breath', 'Fatigue', 'Dizziness', 'Chest discomfort'],
                    'causes': ['Age', 'CVD', 'Thyroid disease', 'Sleep apnea', 'Lung disease'],
                    'treatment': ['Rate control (beta-blockers, diltiazem)', 'Rhythm control (antiarrhythmics)', 'Anticoagulation'],
                    'risk_stratification': ['CHA2DS2-VASc score']
                },
                'cancer': {
                    'types': ['Lung', 'Breast', 'Prostate', 'Colorectal', 'Melanoma', 'Lymphoma', 'Pancreatic', 'Ovarian'],
                    'risk_factors': ['Smoking', 'Family history', 'Age', 'Alcohol', 'Obesity', 'Infections', 'Radiation'],
                    'screening': ['Mammography', 'Colonoscopy', 'PSA testing', 'Pap smear', 'Skin checks'],
                    'treatment': ['Chemotherapy', 'Radiation', 'Surgery', 'Immunotherapy', 'Targeted therapy', 'Hormone therapy'],
                    'latest_developments': ['CAR-T cell therapy', 'Checkpoint inhibitors', 'Personalized medicine']
                },
                'covid-19': {
                    'description': 'Coronavirus disease 2019',
                    'symptoms': ['Fever', 'Dry cough', 'Fatigue', 'Loss of taste/smell', 'Difficulty breathing'],
                    'severity': ['Asymptomatic', 'Mild', 'Moderate', 'Severe', 'Critical'],
                    'treatment': ['Supportive care', 'Antivirals (Paxlovid, Molnupiravir)', 'Monoclonal antibodies', 'Steroids'],
                    'prevention': ['Vaccination', 'Masking', 'Distancing', 'Hand hygiene', 'Ventilation'],
                    'variants': ['Omicron', 'Variants of concern'],
                    'vaccines': ['mRNA (Pfizer, Moderna)', 'Viral vector (J&J)', 'Protein subunit (Novavax)']
                },
                'influenza': {
                    'description': 'Seasonal flu infection',
                    'symptoms': ['High fever', 'Cough', 'Muscle aches', 'Fatigue', 'Headache', 'Sore throat'],
                    'treatment': ['Antivirals (Tamiflu)', 'Supportive care', 'Rest', 'Fluids'],
                    'prevention': ['Annual vaccine', 'Hand hygiene', 'Antiviral prophylaxis'],
                    'at_risk_populations': ['Elderly', 'Young children', 'Pregnant women', 'Immunocompromised']
                },
                'pneumonia': {
                    'types': ['Bacterial', 'Viral', 'Fungal', 'Aspiration'],
                    'symptoms': ['Cough', 'Fever', 'Shortness of breath', 'Chest pain', 'Fatigue'],
                    'diagnosis': ['Chest X-ray', 'CT scan', 'Blood tests', 'Sputum culture'],
                    'treatment': ['Antibiotics', 'Antivirals', 'Supportive care', 'Oxygen'],
                    'prevention': ['Pneumococcal vaccine', 'Flu vaccine']
                },
                'depression': {
                    'description': 'Major depressive disorder',
                    'symptoms': ['Persistent sadness', 'Loss of interest', 'Fatigue', 'Sleep changes', 'Appetite changes', 'Guilt', 'Concentration difficulty'],
                    'risk_factors': ['Family history', 'Life stressors', 'Medical conditions', 'Hormonal changes'],
                    'treatment': ['SSRIs (sertraline, fluoxetine)', 'SNRIs', 'Tricyclics', 'Psychotherapy (CBT, IPT)', 'TMS', 'Lifestyle changes'],
                    'severity': ['Mild', 'Moderate', 'Severe'],
                    'suicidal_ideation_resources': ['National Suicide Prevention Lifeline: 988', 'Crisis Text Line: Text HOME to 741741']
                },
                'anxiety_disorder': {
                    'types': ['Generalized anxiety disorder', 'Panic disorder', 'Social anxiety', 'OCD', 'PTSD'],
                    'symptoms': ['Worry', 'Panic attacks', 'Physical tension', 'Avoidance', 'Sleep problems'],
                    'treatment': ['SSRIs', 'Buspirone', 'CBT', 'Exposure therapy', 'Meditation', 'Exercise'],
                    'latest_therapies': ['Esketamine (Spravato)', 'Psychedelic-assisted therapy']
                },
                'thyroid_disease': {
                    'types': ['Hyperthyroidism (Graves disease, Hashimoto)', 'Hypothyroidism', 'Thyroiditis', 'Goiter'],
                    'symptoms': ['Energy changes', 'Weight changes', 'Temperature sensitivity', 'Mood changes'],
                    'diagnosis': ['TSH level', 'Free T3/T4', 'Antibodies', 'Ultrasound'],
                    'treatment': ['Levothyroxine (synthroid)', 'Beta-blockers', 'Antithyroid meds', 'Surgery', 'Radioactive iodine'],
                    'monitoring': ['Annual TSH checks']
                },
                'arthritis': {
                    'types': ['Osteoarthritis', 'Rheumatoid arthritis', 'Lupus', 'Gout', 'Psoriatic'],
                    'symptoms': ['Joint pain', 'Stiffness', 'Swelling', 'Reduced mobility', 'Fatigue'],
                    'treatment': ['NSAIDs', 'DMARDs', 'Biologics (TNF inhibitors)', 'Corticosteroids', 'Physical therapy'],
                    'latest_biologics': ['JAK inhibitors', 'IL-6 inhibitors']
                },
                'chronic_kidney_disease': {
                    'description': 'Progressive loss of kidney function',
                    'stages': ['Stage 1 (GFR >90)', 'Stage 2 (GFR 60-89)', 'Stage 3a (GFR 45-59)', 'Stage 3b (GFR 30-44)', 'Stage 4 (GFR 15-29)', 'Stage 5 (GFR <15)'],
                    'monitoring': ['Creatinine', 'GFR', 'Proteinuria'],
                    'treatment': ['ACE inhibitors/ARBs', 'Phosphate binders', 'ESAs', 'Iron supplementation', 'Dialysis', 'Transplant']
                },
                'liver_disease': {
                    'types': ['Hepatitis A', 'Hepatitis B', 'Hepatitis C', 'Cirrhosis', 'NAFLD', 'Alcoholic liver disease'],
                    'symptoms': ['Jaundice', 'Fatigue', 'Abdominal pain', 'Nausea', 'Dark urine'],
                    'treatment': ['Antivirals', 'Immunosuppression', 'Supportive care', 'Transplant'],
                    'screening': ['Liver function tests', 'Viral serology', 'Ultrasound', 'Biopsy']
                },
                'sleep_disorders': {
                    'types': ['Insomnia', 'Sleep apnea', 'Narcolepsy', 'RLS', 'Parasomnia'],
                    'treatment': ['CBT-I', 'Sleep medications', 'CPAP', 'Stimulants', 'Lifestyle changes'],
                    'hygiene_tips': ['Consistent sleep schedule', 'Dark cool room', 'No screens 1 hour before bed', 'No caffeine after 2pm']
                },
                'obesity': {
                    'description': 'BMI ≥30',
                    'complications': ['Type 2 diabetes', 'CVD', 'Hypertension', 'Sleep apnea', 'Joint problems'],
                    'treatment': ['Lifestyle changes', 'Medications (GLP-1 agonists)', 'Bariatric surgery'],
                    'latest_medications': ['Semaglutide (Ozempic, Wegovy)', 'Tirzepatide (Zepbound)']
                }
            },
            'medications': {
                'acetaminophen': {
                    'uses': ['Pain relief', 'Fever reduction'],
                    'side_effects': ['Liver damage (overdose)', 'Nausea', 'Rash', 'Rare allergic reactions'],
                    'dosage': ['Adults: 500-1000mg every 4-6 hours', 'Max 4000mg/day', 'Children: 10-15mg/kg every 4-6 hours'],
                    'warnings': ['Avoid alcohol', 'Liver disease caution', 'Pregnancy category B', 'Not for long-term use'],
                    'interactions': ['Warfarin', 'Alcohol', 'Carbamazepine'],
                    'brand_names': ['Tylenol', 'Paracetamol']
                },
                'ibuprofen': {
                    'uses': ['Pain relief', 'Inflammation reduction', 'Fever reduction', 'Arthritis'],
                    'side_effects': ['Stomach upset', 'Ulcers', 'Kidney problems', 'Heart risks', 'Allergic reactions'],
                    'dosage': ['Adults: 200-400mg every 4-6 hours', 'Max 1200mg/day', 'With food to reduce GI upset'],
                    'warnings': ['Stomach issues', 'Kidney disease', 'Heart conditions', 'Pregnancy category C/D'],
                    'interactions': ['Aspirin', 'Warfarin', 'ACE inhibitors', 'Diuretics'],
                    'brand_names': ['Advil', 'Motrin']
                },
                'metformin': {
                    'uses': ['Type 2 diabetes', 'PCOS', 'Weight management', 'Prediabetes'],
                    'side_effects': ['Nausea', 'Diarrhea', 'Vitamin B12 deficiency', 'Lactic acidosis (rare)', 'Metallic taste'],
                    'dosage': ['500-1000mg twice daily', 'Extended release available', 'Titrate slowly'],
                    'warnings': ['Kidney function monitoring', 'Heart failure', 'Alcohol use', 'Radiologic procedures with contrast'],
                    'monitoring': ['Kidney function', 'Vitamin B12 levels', 'HbA1c every 3-6 months'],
                    'brand_names': ['Glucophage', 'Glumetza']
                },
                'lisinopril': {
                    'class': 'ACE inhibitor',
                    'uses': ['Hypertension', 'Heart failure', 'Post-MI'],
                    'dosage': ['10-40mg once daily'],
                    'side_effects': ['Persistent cough', 'Dizziness', 'Hyperkalemia', 'Angioedema'],
                    'monitoring': ['Blood pressure', 'Potassium', 'Creatinine'],
                    'brand_names': ['Prinivil', 'Zestril']
                },
                'atorvastatin': {
                    'class': 'Statin',
                    'uses': ['High cholesterol', 'CAD prevention', 'Stroke prevention'],
                    'dosage': ['10-80mg once daily'],
                    'side_effects': ['Muscle pain', 'Liver enzyme elevation', 'Fatigue'],
                    'interactions': ['Grapefruit juice', 'Some antifungals', 'Macrolide antibiotics'],
                    'monitoring': ['Lipid panel', 'LFTs']
                },
                'amlodipine': {
                    'class': 'Calcium channel blocker',
                    'uses': ['Hypertension', 'Angina'],
                    'dosage': ['2.5-10mg once daily'],
                    'side_effects': ['Ankle edema', 'Headache', 'Flushing', 'Palpitations'],
                    'brand_names': ['Norvasc', 'Lotrel']
                },
                'metoprolol': {
                    'class': 'Beta-blocker',
                    'uses': ['Hypertension', 'Angina', 'Heart failure', 'Post-MI', 'Arrhythmias'],
                    'dosage': ['25-190mg twice daily'],
                    'side_effects': ['Fatigue', 'Dizziness', 'Bradycardia', 'Sexual dysfunction'],
                    'monitoring': ['Heart rate', 'Blood pressure'],
                    'brand_names': ['Lopressor', 'Toprol']
                },
                'sertraline': {
                    'class': 'SSRI',
                    'uses': ['Depression', 'Anxiety disorders', 'OCD', 'PTSD', 'Panic disorder'],
                    'dosage': ['50-200mg daily'],
                    'side_effects': ['Nausea', 'Insomnia', 'Sexual dysfunction', 'Serotonin syndrome'],
                    'warnings': ['Risk of suicidal thoughts in young adults', 'Withdrawal symptoms on discontinuation'],
                    'brand_names': ['Zoloft']
                },
                'fluoxetine': {
                    'class': 'SSRI',
                    'uses': ['Depression', 'Anxiety', 'OCD', 'Bulimia'],
                    'dosage': ['20-80mg daily'],
                    'side_effects': ['Insomnia', 'Nausea', 'Sexual dysfunction'],
                    'brand_names': ['Prozac', 'Sarafem']
                },
                'escitalopram': {
                    'class': 'SSRI',
                    'uses': ['Depression', 'Anxiety'],
                    'dosage': ['10-20mg daily'],
                    'side_effects': ['Sleep problems', 'Nausea', 'Fatigue'],
                    'brand_names': ['Lexapro', 'Cipralex']
                },
                'omeprazole': {
                    'class': 'Proton pump inhibitor',
                    'uses': ['GERD', 'Peptic ulcer', 'Heartburn'],
                    'dosage': ['20-40mg daily'],
                    'side_effects': ['Headache', 'Nausea', 'B12 deficiency', 'Bone fractures'],
                    'warnings': ['Long-term use risk', 'Vitamin deficiencies'],
                    'brand_names': ['Prilosec', 'Losec']
                },
                'pantoprazole': {
                    'class': 'Proton pump inhibitor',
                    'uses': ['GERD', 'Ulcer disease'],
                    'dosage': ['40mg once daily'],
                    'brand_names': ['Protonix']
                },
                'albuterol': {
                    'uses': ['Asthma', 'COPD', 'Bronchospasm'],
                    'forms': ['Inhaler', 'Nebulizer', 'Tablets'],
                    'dosage': ['2 puffs every 4-6 hours as needed'],
                    'side_effects': ['Tremor', 'Tachycardia', 'Nervousness', 'Headache'],
                    'brand_names': ['Ventolin', 'ProAir', 'Asmol']
                },
                'prednisone': {
                    'class': 'Corticosteroid',
                    'uses': ['Inflammation', 'Autoimmune', 'Allergies', 'Asthma flare-up'],
                    'dosage': ['Varies widely', 'Taper off slowly'],
                    'side_effects': ['Increased appetite', 'Mood changes', 'Insomnia', 'Immunosuppression'],
                    'warnings': ['Do not stop abruptly', 'Diabetes risk', 'Osteoporosis risk'],
                    'brand_names': ['Deltasone']
                },
                'warfarin': {
                    'class': 'Anticoagulant',
                    'uses': ['AFib stroke prevention', 'DVT/PE treatment', 'Mechanical heart valves'],
                    'dosage': ['2-10mg daily (individualized)'],
                    'monitoring': ['INR 2-3 (most conditions)', 'Weekly until stable'],
                    'major_interactions': ['NSAIDs', 'Aspirin', 'Antibiotics', 'Antifungals'],
                    'brand_names': ['Coumadin', 'Jantoven']
                },
                'apixaban': {
                    'class': 'DOAC',
                    'uses': ['AFib stroke prevention', 'DVT/PE treatment', 'Mechanical mitral valve'],
                    'dosage': ['2.5-5mg twice daily'],
                    'advantages': ['No INR monitoring', 'Predictable', 'Fewer interactions'],
                    'brand_names': ['Eliquat']
                },
                'rivaroxaban': {
                    'class': 'DOAC',
                    'uses': ['AFib stroke prevention', 'DVT/PE treatment'],
                    'dosage': ['15-20mg once daily with food'],
                    'brand_names': ['Xarelto']
                },
                'semaglutide': {
                    'class': 'GLP-1 agonist',
                    'uses': ['Type 2 diabetes', 'Weight loss', 'Cardiovascular risk reduction'],
                    'dosage': ['0.5-2.4mg weekly subcutaneous'],
                    'side_effects': ['Nausea', 'Vomiting', 'Diarrhea', 'Pancreatitis risk'],
                    'brand_names': ['Ozempic (diabetes)', 'Wegovy (weight loss)']
                },
                'tirzepatide': {
                    'class': 'GIP/GLP-1 receptor agonist',
                    'uses': ['Type 2 diabetes', 'Obesity', 'NASH'],
                    'dosage': ['2.5-15mg weekly subcutaneous'],
                    'benefits': ['More weight loss than GLP-1 alone', 'Better glucose control'],
                    'brand_names': ['Mounjaro (diabetes)', 'Zepbound (obesity)']
                },
                'insulin_glargine': {
                    'class': 'Long-acting insulin',
                    'uses': ['Type 1 diabetes', 'Type 2 diabetes'],
                    'dosage': ['10-100 units daily subcutaneous'],
                    'monitoring': ['Blood glucose', 'HbA1c'],
                    'brand_names': ['Lantus', 'Basaglar', 'Toujeo']
                },
                'dapagliflozin': {
                    'class': 'SGLT2 inhibitor',
                    'uses': ['Type 2 diabetes', 'Heart failure', 'CKD'],
                    'dosage': ['5-10mg once daily'],
                    'benefits': ['Cardiovascular protection', 'Kidney protection', 'Weight loss'],
                    'brand_names': ['Farxiga']
                },
                'spironolactone': {
                    'class': 'Aldosterone antagonist',
                    'uses': ['Heart failure', 'Hypertension', 'Hyperkalemia management'],
                    'dosage': ['12.5-50mg once daily'],
                    'side_effects': ['Hyperkalemia', 'Gynecomastia', 'Menstrual changes'],
                    'monitoring': ['Potassium', 'Creatinine'],
                    'brand_names': ['Aldactone']
                },
                'furosemide': {
                    'class': 'Loop diuretic',
                    'uses': ['Heart failure', 'Pulmonary edema', 'Hypertension', 'Edema'],
                    'dosage': ['20-600mg daily (varies)'],
                    'monitoring': ['Electrolytes', 'Kidney function'],
                    'brand_names': ['Lasix']
                },
                'atorvastatin': {
                    'class': 'Statin',
                    'uses': ['CAD prevention', 'Cholesterol reduction'],
                    'dosage': ['10-80mg once daily'],
                    'monitoring': ['Lipid panel', 'LFTs']
                },
                'donepezil': {
                    'class': 'Acetylcholinesterase inhibitor',
                    'uses': ['Alzheimer disease'],
                    'dosage': ['5-10mg once daily at bedtime'],
                    'brand_names': ['Aricept']
                },
                'memantine': {
                    'class': 'NMDA antagonist',
                    'uses': ['Alzheimer disease (moderate to severe)', 'Dementia'],
                    'dosage': ['5-20mg daily'],
                    'brand_names': ['Namenda']
                },
                'paxlovid': {
                    'class': 'Antiviral (protease inhibitor)',
                    'uses': ['COVID-19 (mild-moderate in high-risk)'],
                    'dosage': ['Combination therapy for 5 days'],
                    'effectiveness': ['Reduces hospitalization >85%', 'Reduces death >90%'],
                    'drug_interactions': ['Many CYP3A4 interactions']
                },
                'remdesivir': {
                    'class': 'Antiviral nucleotide analog',
                    'uses': ['COVID-19 (hospitalized)', 'Ebola'],
                    'dosage': ['200mg IV loading, then 100mg daily'],
                    'effectiveness': ['Shortens recovery time 4-5 days']
                },
                'molnupiravir': {
                    'class': 'Oral antiviral',
                    'uses': ['COVID-19 (mild-moderate)'],
                    'dosage': ['800mg twice daily for 5 days'],
                    'advantages': ['Oral availability', 'Early treatment option']
                },
                'tocilizumab': {
                    'class': 'IL-6 inhibitor',
                    'uses': ['Severe COVID-19', 'RA', 'Cytokine storm'],
                    'brand_names': ['Actemra']
                },
                'insulin_lispro': {
                    'class': 'Rapid-acting insulin',
                    'uses': ['Type 1 and Type 2 diabetes'],
                    'onset': ['10-15 minutes', 'Peak: 1-2 hours'],
                    'brand_names': ['Humalog', 'Admelog']
                },
                'gabapentin': {
                    'class': 'Anticonvulsant/Neuropathic pain agent',
                    'uses': ['Neuropathic pain', 'Seizures', 'Anxiety'],
                    'dosage': ['300-3600mg daily in divided doses'],
                    'side_effects': ['Dizziness', 'Fatigue', 'Cognitive impairment']
                }
            },
            'drug_interactions': {
                'warfarin_nsaid': {
                    'drugs': ['Warfarin', 'NSAIDs (Ibuprofen, Naproxen)'],
                    'risk_level': 'SEVERE',
                    'mechanism': 'NSAIDs inhibit platelet function + warfarin anticoagulation = severe bleeding',
                    'management': 'Avoid combination entirely; use acetaminophen for pain',
                    'symptoms': ['Unusual bruising', 'Blood in urine/stool', 'GI bleeding']
                },
                'warfarin_antibiotics': {
                    'drugs': ['Warfarin', 'Antibiotics (Trimethoprim, Metronidazole, Fluoroquinolones)'],
                    'risk_level': 'MODERATE-SEVERE',
                    'mechanism': 'Many antibiotics disrupt vitamin K synthesis or inhibit warfarin metabolism',
                    'management': 'Monitor INR closely, increase INR frequency to weekly',
                    'affected_antibiotics': ['Trimethoprim-sulfamethoxazole', 'Metronidazole', 'Ciprofloxacin', 'Amoxicillin']
                },
                'warfarin_acetaminophen': {
                    'drugs': ['Warfarin', 'Acetaminophen'],
                    'risk_level': 'MODERATE',
                    'mechanism': 'Chronic high-dose acetaminophen may potentiate warfarin effects',
                    'management': 'Use lowest effective dose; monitor INR',
                    'safe': 'Occasional use at recommended doses is acceptable'
                },
                'statin_grapefruit': {
                    'drugs': ['Statins (especially Atorvastatin, Simvastatin)', 'Grapefruit juice'],
                    'risk_level': 'MODERATE-SEVERE',
                    'mechanism': 'CYP3A4 inhibition increases statin blood levels 3-15x',
                    'management': 'Avoid grapefruit juice; use pravastatin or rosuvastatin instead',
                    'symptoms': ['Muscle pain/myopathy', 'Dark urine', 'Fatigue']
                },
                'statin_fibrates': {
                    'drugs': ['Statins (all)', 'Fibrates (Gemfibrozil, Fenofibrate)'],
                    'risk_level': 'HIGH',
                    'mechanism': 'Both increase myopathy and rhabdomyolysis risk',
                    'management': 'Avoid combination or use pravastatin (lower interaction); monitor CK',
                    'note': 'Risk particularly high with gemfibrozil + simvastatin'
                },
                'ace_inhibitor_nsaid': {
                    'drugs': ['ACE inhibitors (Lisinopril)', 'NSAIDs'],
                    'risk_level': 'MODERATE',
                    'mechanism': 'NSAIDs reduce ACE inhibitor effectiveness + increase renal dysfunction risk',
                    'management': 'Use acetaminophen; if NSAID needed, monitor renal function',
                    'monitoring': ['Creatinine', 'Potassium']
                },
                'ssri_maoi': {
                    'drugs': ['SSRIs (Sertraline, Fluoxetine)', 'MAOIs'],
                    'risk_level': 'CONTRAINDICATED',
                    'mechanism': 'Serotonin syndrome (life-threatening)',
                    'management': 'Never combine; wait 5 weeks after SSRI before MAOI',
                    'symptoms': ['Agitation', 'Confusion', 'High fever', 'Muscle rigidity', 'Seizures']
                },
                'metformin_alcohol': {
                    'drugs': ['Metformin', 'Alcohol'],
                    'risk_level': 'MODERATE',
                    'mechanism': 'Increased lactic acidosis risk',
                    'management': 'Limit alcohol; avoid in acute illness'
                },
                'omeprazole_clopidogrel': {
                    'drugs': ['Omeprazole/Pantoprazole', 'Clopidogrel (Plavix)'],
                    'risk_level': 'MODERATE',
                    'mechanism': 'PPI reduces clopidogrel effectiveness',
                    'management': 'Use famotidine or H2-blocker instead'
                },
                'insulin_alcohol': {
                    'drugs': ['Insulin', 'Alcohol'],
                    'risk_level': 'MODERATE-HIGH',
                    'mechanism': 'Alcohol impairs hypoglycemia awareness',
                    'management': 'Limit alcohol; eat food with alcohol'
                }
            },
            'medical_calculators': {
                'bmi': {
                    'formula': 'weight_kg / (height_m ** 2)',
                    'alternative': 'weight_lb / (height_in ** 2) × 703',
                    'categories': {
                        'underweight': '< 18.5 (risk: nutritional deficiency)',
                        'normal': '18.5-24.9 (ideal range)',
                        'overweight': '25-29.9 (risk: hypertension, diabetes)',
                        'obese_class_1': '30-34.9 (significant health risk)',
                        'obese_class_2': '35-39.9 (high health risk)',
                        'obese_class_3': '≥ 40 (very high health risk)'
                    },
                    'limitations': ['Does not account for muscle mass', 'Not accurate for pregnant women', 'Ethnic differences', 'Does not measure body fat distribution']
                },
                'framingham_risk_score': {
                    'purpose': 'Estimates 10-year risk of major coronary event',
                    'factors': ['Age', 'Gender', 'Total cholesterol', 'HDL cholesterol', 'Systolic BP', 'Smoking', 'Diabetes'],
                    'output': 'Percentage risk (low <5%, intermediate 5-20%, high >20%)',
                    'action': 'Risk ≥20% warrants intensive lipid management'
                },
                'ascvd_risk_score': {
                    'purpose': '10-year risk of atherosclerotic CVD (MI, stroke, death)',
                    'factors': ['Age', 'Gender', 'Race', 'Total cholesterol', 'HDL', 'Systolic BP', 'Diabetes', 'Smoking', 'Hypertension treatment status'],
                    'output': 'Percentage risk',
                    'interpretation': 'ACC/AHA tool used to guide statin therapy'
                },
                'cha2ds2_vasc': {
                    'purpose': 'Predicts stroke risk in AFib patients',
                    'score_points': {
                        'C': '(Congestive heart failure) = 1 point',
                        'H': '(Hypertension) = 1 point',
                        'A2': '(Age ≥75) = 2 points',
                        'D': '(Diabetes) = 1 point',
                        'S2': '(Prior Stroke/TIA/thromboembolism) = 2 points',
                        'V': '(Vascular disease) = 1 point',
                        'A': '(Age 65-74) = 1 point',
                        'Sc': '(Sex category - female) = 1 point'
                    },
                    'action': 'Score ≥2 (men) or ≥3 (women) warrants anticoagulation'
                },
                'egfr': {
                    'purpose': 'Estimate GFR (kidney function)',
                    'formula': 'MDRD: 175 × (Creatinine**-1.154) × (Age**-0.203) × (0.742 if female) × (1.212 if African American)',
                    'simplified': 'CKD-EPI equation (preferred)',
                    'stages': {
                        '1': '≥90 (normal)',
                        '2': '60-89 (mild decrease)',
                        '3a': '45-59 (mild-moderate decrease)',
                        '3b': '30-44 (moderate-severe decrease)',
                        '4': '15-29 (severe decrease)',
                        '5': '<15 (kidney failure)'
                    }
                },
                'tscore': {
                    'purpose': 'Bone mineral density assessment (osteoporosis screening)',
                    'method': 'DEXA scan',
                    'interpretation': {
                        'normal': 'T-score ≥ -1.0',
                        'osteopenia': 'T-score -1.0 to -2.5',
                        'osteoporosis': 'T-score ≤ -2.5',
                        'severe_osteoporosis': 'T-score ≤ -2.5 + fragility fracture'
                    }
                },
                'frax_score': {
                    'purpose': '10-year fracture risk in osteoporosis',
                    'inputs': ['Age', 'Gender', 'BMI', 'Prior fracture', 'Parent fracture', 'Smoking', 'Corticosteroids', 'Rheumatoid arthritis', 'Secondary osteoporosis', 'Alcohol use', 'T-score'],
                    'output': '10-year probability of major osteoporotic fracture'
                },
                'apri_score': {
                    'purpose': 'Predicts liver fibrosis in hepatitis C',
                    'formula': '(AST/upper_limit_normal) / platelet_count × 100',
                    'interpretation': 'Useful for non-invasive fibrosis assessment'
                }
            },
            'emergency_protocols': {
                'chest_pain_acute_mi': {
                    'symptoms': ['Central chest pain/pressure', 'Radiates to left arm/jaw/back', 'Shortness of breath', 'Sweating', 'Nausea', 'Palpitations', 'Anxiety'],
                    'atypical_symptoms': ['Shortness of breath alone (especially women/elderly)', 'Epigastric pain', 'Fatigue', 'Syncope'],
                    'immediate_actions': [
                        'Call 911 immediately - DO NOT DELAY',
                        'Chew aspirin 325mg (if no contraindications)',
                        'Take nitroglycerin if prescribed (sublingual)',
                        'Loosen tight clothing',
                        'Sit/lie down',
                        'CPR if patient becomes unresponsive'
                    ],
                    'hospital_treatment': ['ECG within 10 minutes', 'Troponin levels', 'Primary PCI or thrombolysis within 12 hours', 'Dual antiplatelet therapy'],
                    'prognosis': 'Mortality depends on time to treatment - "time is muscle"'
                },
                'stroke_ischemic': {
                    'symptoms': ['Facial drooping', 'Arm weakness/numbness', 'Speech difficulty', 'Vision loss (one eye)', 'Vertigo/ataxia', 'Severe headache (with weakness)'],
                    'assessment': ['FAST test: Face drooping? Arm weakness? Speech difficulty? Time to call 911'],
                    'immediate_actions': [
                        'Call 911 immediately - NOTE EXACT TIME SYMPTOM STARTED',
                        'Do NOT give food/water (aspiration risk)',
                        'Do NOT drive - arrange emergency transport',
                        'Have patient lie on side if unconscious'
                    ],
                    'treatment_windows': [
                        'IV tPA (alteplase): 3-4.5 hours from symptom onset',
                        'Mechanical thrombectomy: up to 24 hours in select patients'
                    ],
                    'hospital_workup': ['Stat CT/MRI brain', 'ECG', 'Troponin', 'Coagulation studies', 'Blood glucose']
                },
                'severe_sepsis': {
                    'definition': 'Life-threatening organ dysfunction due to infection (SIRS + infection)',
                    'symptoms': ['Fever/hypothermia', 'Tachycardia >90', 'Tachypnea >20', 'Confusion', 'Hypotension', 'Lactate elevated'],
                    'immediate_actions': [
                        'Call 911',
                        'Obtain IV access if trained',
                        'Keep patient warm',
                        'Position supine with legs elevated (300mL bolus position)',
                        'Administer oxygen if SpO2 <90%'
                    ],
                    'hospital_treatment': ['Blood cultures before antibiotics', 'Broad-spectrum antibiotics <1 hour', 'Fluid resuscitation', 'Vasopressors if hypotensive'],
                    'risk_stratification': 'qSOFA score for bedside assessment'
                },
                'anaphylaxis': {
                    'definition': 'Severe, potentially life-threatening allergic reaction',
                    'onset': 'Usually within minutes of exposure',
                    'symptoms': [
                        'Respiratory: wheezing, stridor, shortness of breath, hypoxia',
                        'Cardiovascular: hypotension, shock, syncope, tachycardia',
                        'Skin: flushing, urticaria, angioedema',
                        'GI: cramping, vomiting, diarrhea',
                        'Neurologic: confusion, loss of consciousness'
                    ],
                    'immediate_actions': [
                        'EPINEPHRINE 0.3mg IM immediately (0.01mg/kg up to 0.5mg if obese)',
                        'Call 911 after giving epinephrine',
                        'Remove allergen (food, stinger, IV)',
                        'Position supine with legs elevated',
                        'Administer oxygen',
                        'Establish IV access'
                    ],
                    'follow_up_medications': ['Antihistamines (H1 blocker)', 'H2 blocker (ranitidine)', 'Corticosteroid (methylprednisolone)'],
                    'observation': 'Admit for 4-8 hours, biphasic reactions possible'
                },
                'respiratory_failure': {
                    'definition': 'Inadequate oxygenation (Type I) or ventilation (Type II)',
                    'symptoms': ['Severe shortness of breath', 'Altered mental status', 'Cyanosis', 'Use of accessory muscles', 'Paradoxical breathing'],
                    'causes': ['Pneumonia', 'COPD exacerbation', 'Asthma attack', 'Pulmonary embolism', 'Pulmonary edema', 'Aspiration'],
                    'immediate_actions': [
                        'Call 911',
                        'Position upright/semi-Fowler',
                        'Administer high-flow oxygen (non-rebreather mask 10-15L)',
                        'Auscultate lungs for wheezing/crackles',
                        'Prepare for possible intubation'
                    ],
                    'hospital_treatment': ['ABG analysis', 'Chest X-ray', 'Mechanical ventilation if needed', 'Treatment of underlying cause']
                },
                'severe_hypoglycemia': {
                    'definition': 'Blood glucose <40 mg/dL with altered mental status',
                    'symptoms': ['Confusion', 'Slurred speech', 'Seizures', 'Loss of consciousness', 'Sweating', 'Tremor', 'Tachycardia'],
                    'immediate_actions': [
                        'Get away from hazardous situations',
                        'If conscious: give 15g fast-acting carbs (juice, glucose tabs)',
                        'If unconscious with seizure: GLUCAGON IM/SC 1mg (if available)',
                        'Call 911 if not improving or unconscious',
                        'Position in recovery position if unconscious'
                    ],
                    'hospital_treatment': ['IV dextrose (D50W) 25g', 'Glucose monitoring', 'Investigation of cause']
                },
                'poison_overdose': {
                    'immediate_actions': [
                        'Call Poison Control: 1-800-222-1222 (US)',
                        'Have container/information ready',
                        'Follow poison control instructions (may include activated charcoal, induced vomiting status)',
                        'Do NOT induce vomiting for some substances (corrosives, hydrocarbons)'
                    ],
                    'assessment_needed': ['Time of ingestion', 'Amount', 'Type of substance', 'Weight of patient', 'Vital signs']
                }
            },
            'preventive_care': {
                'cancer_screening': {
                    'breast_cancer': {
                        'age_40_44': 'Mammography optional annual or shared decision',
                        'age_45_54': 'Annual mammography (USPSTF Grade A)',
                        'age_55_plus': 'Annual or biennial mammography (USPSTF Grade B)',
                        'risk_factors': 'Earlier screening if: family history, BRCA mutation, prior breast cancer, dense breast tissue',
                        'supplemental_imaging': 'Ultrasound or MRI may be considered with dense breasts'
                    },
                    'colorectal_cancer': {
                        'age_45_and_up': 'Screening starting at 45 (updated 2021)',
                        'screening_methods': ['Colonoscopy every 10 years', 'Flexible sigmoidoscopy every 5 years', 'fecal testing annually (FOBT/FIT)', 'CT colonography every 5 years'],
                        'high_risk': 'Earlier/more frequent screening if: family history, inflammatory bowel disease, personal polyp history',
                        'positive_findings': 'Polyps removed during colonoscopy'
                    },
                    'cervical_cancer': {
                        'age_21_29': 'Pap test every 3 years (HPV co-testing not recommended)',
                        'age_30_65': 'HPV test every 5 years OR Pap + HPV every 5 years (preferred) OR Pap every 3 years',
                        'age_65_plus': 'Stop if adequate prior screening, no high-risk factors',
                        'vaccination': 'Gardasil 9 for ages 11-26 (up to 45 with shared decision)'
                    },
                    'prostate_cancer': {
                        'age_50': 'Shared decision making with PSA/DRE',
                        'age_40_49_high_risk': 'Discuss with African American men, family history',
                        'rationale': 'PSA can be falsely elevated; many cancers slow-growing'
                    },
                    'lung_cancer': {
                        'high_risk': 'Age 50-80 with 20+ pack-year history, current/former smoker',
                        'screening': 'Annual low-dose CT (LDCT) if eligible'
                    },
                    'skin_cancer': {
                        'self_exam': 'Monthly using ABCDE method (Asymmetry, Border irregularity, Color variation, Diameter >5mm, Evolving/changing)',
                        'professional_exam': 'Annual by dermatologist for high-risk individuals'
                    }
                },
                'cardiovascular_screening': {
                    'blood_pressure': {
                        'frequency': 'At every healthcare visit; Home monitoring if borderline',
                        'normal': '<120/80 mmHg',
                        'elevated': '120-129/<80',
                        'stage_1_hypertension': '130-139/80-89',
                        'stage_2_hypertension': '≥140/90'
                    },
                    'lipid_panel': {
                        'age_20_39': 'Every 4-6 years (more frequent with risk factors)',
                        'age_40_75': 'Every 4-6 years (more frequent with risk factors)',
                        'frequency_with_risk': 'Annual if diabetes, CVD, LDL >160, or 10-year CVD risk ≥7.5%',
                        'targets': ['TC <200', 'LDL <100 (or <70 if high-risk)', 'HDL >40 (men), >50 (women)', 'TG <150']
                    },
                    'diabetes': {
                        'screening_age': 'Starting age 45 (or age 35+ with risk factors)',
                        'frequency': 'Every 3 years if normal, annually if prediabetic',
                        'risk_factors': ['Overweight', 'Family history', 'Sedentary lifestyle', 'Minority ethnicity', 'Prior gestational diabetes'],
                        'testing': ['Fasting glucose', 'HbA1c', 'OGTT (if indicated)']
                    },
                    'aha_acc_risk_calculator': 'Assess 10-year ASCVD risk to determine statin therapy'
                },
                'infectious_disease_prevention': {
                    'influenza_vaccine': {
                        'annual': 'All adults age 6 months and older',
                        'timing': 'September-October preferred for Northern Hemisphere',
                        'effectiveness': '40-60% effective depending on strain match'
                    },
                    'pneumococcal_vaccine': {
                        'age_65_plus': 'Pneumococcal conjugate vaccine (PCV20 preferred, or PCV15 + PPSV23)',
                        'high_risk': 'Age 19-64 with chronic disease, immunosuppression, smoking',
                        'protection': 'Prevents invasive pneumococcal disease'
                    },
                    'tetanus_tdap': {
                        'initial': 'Series of 3 doses as child (DPT)',
                        'adult': 'TD booster every 10 years; One-time Tdap at age 19-64 (or if not previously)',
                        'high_risk': 'Tetanus prophylaxis for contaminated wounds'
                    },
                    'herpes_zoster': {
                        'age_50_plus': 'Recombinant zoster vaccine (RZV/Shingrix) - 2 series, preferred over live vaccine',
                        'protection': '90% efficacy against shingles, excellent for ≥65 years'
                    },
                    'covid_19': {
                        'primary_series': 'All eligible patients; timing depends on vaccine type',
                        'boosters': 'Additional dose 6 months after primary (especially if immunocompromised)',
                        'timing': 'Annual booster for all age 60+, or immunocompromised'
                    },
                    'hpv_vaccine': {
                        'age_11_26': 'Routine vaccination (3-dose series)',
                        'age_27_45': 'Shared decision in some cases',
                        'protection': 'Prevents HPV-related cancers (cervical, anal, oropharyngeal)'
                    }
                },
                'women_health_screening': {
                    'pelvic_exam': 'Annual with Pap smear (see cervical cancer screening)',
                    'bone_density': 'DXA at age 65+ (earlier if risk factors for osteoporosis)',
                    'reproductive_health': 'Contraceptive counseling, preconception planning',
                    'postmenopausal': 'Discuss HRT pros/cons; monitor for osteoporosis, cardiovascular risk'
                },
                'mens_health_screening': {
                    'prostate': 'Shared decision at 50 (or 40-45 if high-risk)',
                    'testicular': 'Self-exam monthly starting at age 15',
                    'abdominal_aortic_aneurysm': 'One-time ultrasound for men age 65-75 with smoking history'
                },
                'lifestyle_modification': {
                    'exercise': {
                        'minimum': '150 minutes moderate-intensity OR 75 minutes vigorous-intensity per week',
                        'additional': 'Muscle-strengthening activities 2 days/week',
                        'benefits': 'Reduces CVD risk, diabetes, obesity, mental health issues'
                    },
                    'nutrition_guidelines': {
                        'diet_pattern': 'Mediterranean or DASH diet pattern',
                        'key_components': ['Fruits 2.5 cups/day', 'Vegetables 3 cups/day', 'Whole grains 6 oz/day', 'Fish 2 times/week', 'Nuts/legumes regularly'],
                        'limiting': 'Saturated fat <7% calories, sodium <2300mg/day, added sugar <10% calories'
                    },
                    'sleep_hygiene': {
                        'duration': '7-9 hours per night for adults',
                        'consistency': 'Same bedtime/wake time daily',
                        'sleep_environment': 'Dark, cool (68°F/20°C), quiet'
                    },
                    'stress_management': {
                        'techniques': ['Meditation/mindfulness', 'Yoga', 'Progressive muscle relaxation', 'Cognitive behavioral therapy if needed'],
                        'social_support': 'Maintain relationships, community involvement'
                    },
                    'substance_use': {
                        'tobacco': 'Complete cessation; offer pharmacotherapy + counseling',
                        'alcohol': 'Men: ≤2 drinks/day; Women: ≤1 drink/day',
                        'drugs': 'Complete avoidance of recreational drugs; proper opioid use if prescribed'
                    },
                    'weight_management': {
                        'target_bmi': '<25 kg/m²',
                        'approach': 'Caloric deficit 500-1000 kcal/day for 1-2 lb/week loss',
                        'medications': 'GLP-1 agonists (semaglutide/tirzepatide) for BMI >30 with comorbidities'
                    }
                }
            }
        }

    def query(self, query: str) -> str:
        """
        Process medical queries and provide intelligent responses.
        
        Args:
            query: The medical question or symptom description
            
        Returns:
            Medical information and advice
        """
        query = query.lower().strip()
        
        try:
            # Check for emergency keywords
            if any(keyword in query for keyword in self.emergency_keywords) and any(personal in query for personal in ['i have', 'i\'m', 'my', 'i feel', 'i am experiencing', 'i\'m experiencing']):
                return ("⚠️ EMERGENCY ALERT: This sounds like a medical emergency. " +
                       "Please call emergency services (911) immediately or go to the nearest emergency room. " +
                       "Do not wait - seek immediate medical attention!")
            
            # Symptom analysis
            if any(word in query for word in ['symptom', 'symptoms', 'feeling', 'pain', 'ache', 'hurt']):
                # Check if it's "explain symptoms for X"
                import re
                match = re.search(r'explain\s+symptoms\s+(?:of|for)\s+(\w+)', query)
                if match:
                    disease = match.group(1)
                    # Look up disease and return symptoms
                    result = self._lookup_disease(disease)
                    if result:
                        return result
                return self._analyze_symptoms(query)
            
            # Disease information - check knowledge base
            diseases = self.knowledge_base.get('diseases', {})
            if diseases:
                for disease_key in diseases.keys():
                    # Check if query contains disease name
                    if disease_key in query or disease_key.replace('_', ' ') in query:
                        try:
                            info = diseases[disease_key]
                            # Check if it's a valid disease entry with data
                            if info and ('description' in info or 'symptoms' in info or 'treatment' in info):
                                return self._format_disease_info(disease_key, info)
                        except Exception as e:
                            self.logger.warning(f"Error formatting disease info for {disease_key}: {e}")
                            continue
            
            # Fallback: Provide info for common diseases that might be in knowledge base but empty
            common_diseases_fallback = {
                'cancer': 'Cancer is a group of diseases characterized by abnormal cell growth. There are many types (lung, breast, colon, etc.) with different symptoms and treatments. Early detection improves outcomes. Please consult a healthcare provider for evaluation and treatment options.',
                'diabetes': 'Diabetes is a metabolic disorder affecting blood sugar levels. Type 1 (autoimmune) requires insulin, Type 2 (insulin resistance) managed with lifestyle/medication. Symptoms: increased thirst, urination, fatigue. Management includes diet, exercise, monitoring.',
                'heart disease': 'Heart disease involves problems with the heart and blood vessels. Risk factors: high blood pressure, cholesterol, smoking, obesity. Symptoms: chest pain, shortness of breath. Treatment: lifestyle changes, medications, sometimes surgery.',
                'hypertension': 'High blood pressure (>130/80 mmHg) damages blood vessels. Often asymptomatic but increases risk of heart attack/stroke. Treatment: DASH diet, exercise, reduce sodium/alcohol, medications if needed.',
                'asthma': 'Asthma causes airway inflammation and breathing difficulties. Triggers: allergens, exercise, cold air. Symptoms: wheezing, shortness of breath, chest tightness. Treatment: inhalers (rescue/controller), avoiding triggers, action plans.',
            }
            
            for disease_name, disease_info in common_diseases_fallback.items():
                if disease_name in query:
                    return f"**{disease_name.title()}**\n\n{disease_info}\n\nPlease consult a healthcare professional for personalized advice."
            
            # Medication information
            medications = self.knowledge_base.get('medications', {})
            if medications:
                for med_key in medications.keys():
                    if med_key in query or med_key.replace('_', ' ') in query:
                        try:
                            info = medications[med_key]
                            return self._format_medication_info(med_key, info)
                        except Exception as e:
                            self.logger.warning(f"Error formatting medication info for {med_key}: {e}")
                            continue
            
            # General medical advice
            if 'prevention' in query or 'prevent' in query:
                return self._get_prevention_advice(query)
            
            if 'screening' in query or 'checkup' in query:
                return self._get_screening_info(query)
            
            # Default response for general medical query
            return ("I'm here to help with medical information. You can ask about:\n\n" +
                   "• Symptoms and conditions (e.g., 'cancer', 'diabetes', 'fever')\n" +
                   "• Medications and drug interactions\n" +
                   "• Health screenings and preventive care\n" +
                   "• Treatment options\n\n" +
                   "For emergencies, please seek immediate medical attention.")
        
        except Exception as e:
            self.logger.error(f"Error in medical query processing: {e}")
            return "I encountered an issue processing your medical query. Please try asking about a specific condition or symptom."
    
    def _lookup_disease(self, disease_name: str) -> Optional[str]:
        """Look up a disease in the knowledge base."""
        try:
            diseases = self.knowledge_base.get('diseases', {})
            # Try exact match
            if disease_name in diseases:
                info = diseases[disease_name]
                return self._format_disease_info(disease_name, info)
            # Try with underscores instead of spaces
            disease_with_underscore = disease_name.replace(' ', '_')
            if disease_with_underscore in diseases:
                info = diseases[disease_with_underscore]
                return self._format_disease_info(disease_name, info)
            return None
        except Exception as e:
            self.logger.warning(f"Error looking up disease {disease_name}: {e}")
            return None

    def _analyze_symptoms(self, query: str) -> str:
        """Analyze symptoms and provide possible causes and advice."""
        symptoms_found = []
        
        for symptom, info in self.knowledge_base.get('symptoms', {}).items():
            if symptom in query:
                symptoms_found.append((symptom, info))
        
        if not symptoms_found:
            return ("I couldn't identify specific symptoms in your query. " +
                   "Please describe your symptoms more clearly (e.g., 'headache', 'chest pain', 'fever').")
        
        response = "Based on your symptoms, here are some possibilities:\n\n"
        
        for symptom, info in symptoms_found[:3]:  # Limit to top 3
            response += f"**{symptom.title()}:**\n"
            response += f"• Description: {info['description']}\n"
            response += f"• Common causes: {', '.join(info['common_causes'][:3])}\n"
            response += f"• Home remedies: {', '.join(info['home_remedies'][:3])}\n"
            
            if info.get('when_to_see_doctor'):
                response += f"• When to see a doctor: {', '.join(info['when_to_see_doctor'][:3])}\n"
            
            if info.get('emergency'):
                response += "⚠️ **EMERGENCY:** Seek immediate medical attention!\n"
            
            response += "\n"
        
        response += ("**Important:** This is not a diagnosis. " +
                    "Please consult a healthcare professional for proper evaluation.")
        
        return response

    def _format_disease_info(self, disease: str, info: Dict[str, Any]) -> str:
        """Format disease information for display."""
        response = f"**{disease.title()}**\n\n"
        response += f"Description: {info['description']}\n\n"
        
        if 'symptoms' in info:
            response += f"Common symptoms: {', '.join(info['symptoms'])}\n\n"
        
        if 'treatment' in info:
            response += f"Treatment options: {', '.join(info['treatment'])}\n\n"
        
        if 'prevention' in info:
            response += f"Prevention: {', '.join(info['prevention'])}\n\n"
        
        response += "Please consult a healthcare professional for personalized advice."
        
        return response

    def _format_medication_info(self, medication: str, info: Dict[str, Any]) -> str:
        """Format medication information for display."""
        response = f"**{medication.title()}**\n\n"
        
        if 'uses' in info:
            response += f"Uses: {', '.join(info['uses'])}\n\n"
        
        if 'side_effects' in info:
            response += f"Common side effects: {', '.join(info['side_effects'])}\n\n"
        
        if 'warnings' in info:
            response += f"Important warnings: {', '.join(info['warnings'])}\n\n"
        
        if 'interactions' in info:
            response += f"Drug interactions: {', '.join(info['interactions'])}\n\n"
        
        response += "Always consult your doctor or pharmacist before taking medications."
        
        return response

    def _get_prevention_advice(self, query: str) -> str:
        """Provide preventive care advice."""
        prevention = self.knowledge_base.get('preventive_care', {})
        
        if 'cancer' in query:
            screenings = prevention.get('screenings', {}).get('cancer', {})
            response = "**Cancer Prevention Screenings:**\n\n"
            for cancer_type, schedule in screenings.items():
                response += f"• {cancer_type.title()}: {schedule}\n"
        elif 'heart' in query or 'cardiovascular' in query:
            cv = prevention.get('screenings', {}).get('cardiovascular', {})
            response = "**Cardiovascular Health Screenings:**\n\n"
            for test, schedule in cv.items():
                response += f"• {test.title()}: {schedule}\n"
        else:
            lifestyle = prevention.get('lifestyle', {})
            response = "**General Preventive Health Measures:**\n\n"
            for category, advice in lifestyle.items():
                response += f"• {category.title()}: {advice}\n"
        
        return response

    def _get_screening_info(self, query: str) -> str:
        """Provide screening information."""
        screenings = self.knowledge_base.get('preventive_care', {}).get('screenings', {})
        
        response = "**Recommended Health Screenings:**\n\n"
        
        for category, tests in screenings.items():
            response += f"**{category.title()} Screenings:**\n"
            for test, schedule in tests.items():
                response += f"• {test.title()}: {schedule}\n"
            response += "\n"
        
        response += "Consult your healthcare provider to determine the best screening schedule for you."
        
        return response

# ErrorHandler class
class ErrorHandler:
    """
    Error handling and logging system.
    """

    def __init__(self) -> None:
        """Initialize error handler."""
        self.logger = logging.getLogger('ErrorHandler')

    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle an error."""
        self.logger.error(f"Error in {context}: {error}")
        # Could implement repair logic here

# SelfUpdate class
class SelfUpdate:
    """
    Self-improvement and update system.
    """

    def __init__(self) -> None:
        """Initialize self-update system."""
        self.logger = logging.getLogger('SelfUpdate')

    def start(self) -> None:
        """Start self-update system."""
        pass

    def stop(self) -> None:
        """Stop self-update system."""
        pass

# Main JarvisAI class
class JarvisAI:
    """
    Main Jarvis AI class that orchestrates all components.
    """

    def __init__(self, mode: str = 'gui') -> None:
        """
        Initialize Jarvis AI components.

        Args:
            mode: Operation mode ('gui', 'voice', 'headless')
        """
        self.mode = mode
        self.running = False

        # Initialize error handler first
        self.error_handler = ErrorHandler()

        # Initialize other components
        self.memory_system = MemorySystem()
        self.medical_ai = MedicalAIModule()
        self.ai_brain = AIBrain(self.memory_system, self.medical_ai)
        self.task_executor = TaskExecutor()
        self.self_update = SelfUpdate()
        self.voice_engine = VoiceEngine()
        self.gui: Optional[JarvisGUI] = None
        self.logger: Optional[logging.Logger] = None

        # Initialize GUI if in GUI mode
        if mode == 'gui':
            self.gui = JarvisGUI(self)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            filename='jarvis.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('JarvisAI')

    # ErrorHandler class
    def start(self) -> None:
        """Start the Jarvis AI system."""
        try:
            self.logger.info("Starting Jarvis AI...")
            self.running = True

            # Start components
            self.memory_system.start()
            self.self_update.start()

            if self.mode == 'gui':
                self.gui.start()
            elif self.mode == 'voice':
                self._start_voice_mode()
            else:  # headless
                self._start_headless_mode()

        except Exception as e:
            self.error_handler.handle_error(e, "Failed to start Jarvis AI")
            sys.exit(1)

    def stop(self) -> None:
        """Stop the Jarvis AI system."""
        self.logger.info("Stopping Jarvis AI...")
        self.running = False

        # Stop components
        if self.gui is not None:
            self.gui.stop()
        self.voice_engine.stop()
        self.memory_system.stop()
        self.self_update.stop()

    def _start_voice_mode(self) -> None:
        """Start voice-only mode."""
        self.logger.info("Starting voice mode...")
        self.voice_engine.start_listening(self._process_voice_command)

    def _start_headless_mode(self) -> None:
        """Start headless mode for background operation."""
        self.logger.info("Starting headless mode...")
        # Implement headless operation logic
        pass

    def _process_voice_command(self, command: str) -> None:
        """
        Process voice commands.

        Args:
            command: Voice command text
        """
        try:
            # Process through AI brain
            response = self.ai_brain.process_command(command)

            # Execute tasks if needed
            if 'task' in response:
                self.task_executor.execute_task(response['task'])

            # Speak response
            if response.get('speak', True):
                self.voice_engine.speak(response['text'])

            # Update GUI if available
            if hasattr(self, 'gui'):
                self.gui.update_response(response['text'])

        except Exception as e:
            self.error_handler.handle_error(e, "Voice command processing failed")

    def process_text_command(self, command: str) -> str:
        """
        Process text commands from GUI.

        Args:
            command: Text command

        Returns:
            Response text
        """
        try:
            response = self.ai_brain.process_command(command)

            if 'task' in response:
                self.task_executor.execute_task(response['task'])

            return response['text']

        except Exception as e:
            self.error_handler.handle_error(e, "Text command processing failed")
            return "Sorry, I encountered an error processing your command."

def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description='Advanced Autonomous Jarvis AI - Python 3.11+')
    parser.add_argument('--mode', choices=['gui', 'voice', 'headless'],
                       default='gui', help='Operation mode')
    args = parser.parse_args()

    # Create Jarvis instance
    jarvis = JarvisAI(mode=args.mode)

    try:
        jarvis.start()

        # Keep main thread alive
        while jarvis.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down Jarvis AI...")
    finally:
        jarvis.stop()

if __name__ == "__main__":
    main()
