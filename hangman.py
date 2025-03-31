import random
import tkinter as tk
from tkinter import messagebox, ttk
import os

class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Word lists by difficulty
        self.words_by_difficulty = {
            "easy": [
                {"word": "PYTHON", "hint": "A popular programming language"},
                {"word": "CODING", "hint": "The process of writing computer programs"},
                {"word": "GAME", "hint": "An activity for entertainment"},
                {"word": "LEARN", "hint": "To gain knowledge or skill"},
                {"word": "WEB", "hint": "The internet"},
                {"word": "CODE", "hint": "Instructions for a computer"},
                {"word": "EASY", "hint": "Not difficult"},
                {"word": "FUN", "hint": "Enjoyable activity"},
                {"word": "PLAY", "hint": "To engage in an activity for enjoyment"},
                {"word": "WORD", "hint": "A single unit of language"}
            ],
            "medium": [
                {"word": "JAVASCRIPT", "hint": "A programming language often used in web browsers"},
                {"word": "HANGMAN", "hint": "The name of this game"},
                {"word": "DEVELOPER", "hint": "Someone who creates software"},
                {"word": "WEBSITE", "hint": "A collection of web pages"},
                {"word": "CHALLENGE", "hint": "A difficult task that tests ability"},
                {"word": "FUNCTION", "hint": "A reusable block of code"},
                {"word": "VARIABLE", "hint": "A storage location in programming"},
                {"word": "DATABASE", "hint": "Organized collection of data"},
                {"word": "KEYBOARD", "hint": "Input device with keys"},
                {"word": "COMPUTER", "hint": "Electronic device for processing data"}
            ],
            "hard": [
                {"word": "ASYNCHRONOUS", "hint": "Not occurring at the same time"},
                {"word": "ALGORITHM", "hint": "A step-by-step procedure for calculations"},
                {"word": "REFACTORING", "hint": "Restructuring code without changing its behavior"},
                {"word": "ABSTRACTION", "hint": "The process of removing characteristics to reduce to a set of essential elements"},
                {"word": "CRYPTOGRAPHY", "hint": "The practice of secure communication"},
                {"word": "ARCHITECTURE", "hint": "The structure and organization of a system"},
                {"word": "MIDDLEWARE", "hint": "Software that acts as a bridge between systems"},
                {"word": "DEPLOYMENT", "hint": "The process of making software available for use"},
                {"word": "INHERITANCE", "hint": "When an object acquires properties of another in OOP"},
                {"word": "SERIALIZATION", "hint": "Converting an object to a format for storage or transmission"}
            ]
        }
        
        # Game variables
        self.secret_word = ""
        self.secret_hint = ""
        self.guessed_word = []
        self.tries = 6
        self.guessed_letters = []
        self.game_over = False
        self.used_words = {
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        # Create UI
        self.create_ui()
        
        # Start a new game
        self.start_game()
        
    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for difficulty selection
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Difficulty label and combobox
        tk.Label(top_frame, text="Difficulty:").pack(side=tk.LEFT, padx=(0, 10))
        self.difficulty_var = tk.StringVar(value="medium")
        difficulty_combo = ttk.Combobox(top_frame, textvariable=self.difficulty_var, 
                                        values=["easy", "medium", "hard"], state="readonly", width=10)
        difficulty_combo.pack(side=tk.LEFT)
        difficulty_combo.bind("<<ComboboxSelected>>", lambda e: self.start_game())
        
        # Middle frame for game display
        middle_frame = tk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas for hangman drawing
        self.canvas = tk.Canvas(middle_frame, width=200, height=200, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Game info frame
        game_info = tk.Frame(middle_frame)
        game_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tries remaining
        tries_frame = tk.Frame(game_info)
        tries_frame.pack(fill=tk.X, pady=5)
        tk.Label(tries_frame, text="Tries remaining:").pack(side=tk.LEFT)
        self.tries_label = tk.Label(tries_frame, text="6", font=("Arial", 12, "bold"))
        self.tries_label.pack(side=tk.LEFT, padx=5)
        
        # Word display
        self.word_display = tk.Label(game_info, text="", font=("Arial", 24), wraplength=300)
        self.word_display.pack(fill=tk.X, pady=10)
        
        # Message display
        self.message_display = tk.Label(game_info, text="", font=("Arial", 12), wraplength=300, height=2)
        self.message_display.pack(fill=tk.X, pady=10)
        
        # Keyboard frame
        keyboard_frame = tk.Frame(main_frame)
        keyboard_frame.pack(fill=tk.X, pady=10)
        
        # Create keyboard
        self.keys = {}
        keyboard_layout = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        for row_idx, row in enumerate(keyboard_layout):
            row_frame = tk.Frame(keyboard_frame)
            row_frame.pack(pady=2)
            
            for letter in row:
                key = tk.Button(row_frame, text=letter, width=3, height=1, 
                               command=lambda l=letter: self.handle_guess(l))
                key.pack(side=tk.LEFT, padx=2)
                self.keys[letter] = key
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.new_game_btn = tk.Button(control_frame, text="New Game", command=self.start_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.hint_btn = tk.Button(control_frame, text="Hint", command=self.show_hint)
        self.hint_btn.pack(side=tk.LEFT, padx=5)
        
    def draw_hangman(self):
        self.canvas.delete("all")
        
        # Draw gallows
        self.canvas.create_line(40, 180, 160, 180, width=3)  # base
        self.canvas.create_line(60, 20, 60, 180, width=3)    # pole
        self.canvas.create_line(58, 20, 130, 20, width=3)    # beam
        self.canvas.create_line(130, 20, 130, 40, width=3)   # rope
        
        # Draw person based on tries left
        if self.tries < 6:  # head
            self.canvas.create_oval(110, 40, 150, 80, width=3)
        
        if self.tries < 5:  # body
            self.canvas.create_line(130, 80, 130, 130, width=3)
        
        if self.tries < 4:  # left arm
            self.canvas.create_line(130, 90, 110, 120, width=3)
        
        if self.tries < 3:  # right arm
            self.canvas.create_line(130, 90, 150, 120, width=3)
        
        if self.tries < 2:  # left leg
            self.canvas.create_line(130, 130, 110, 160, width=3)
        
        if self.tries < 1:  # right leg
            self.canvas.create_line(130, 130, 150, 160, width=3)
    
    def get_random_word(self, difficulty):
        word_list = self.words_by_difficulty[difficulty]
        
        # If we've used all words in this difficulty, reset the used words
        if len(self.used_words[difficulty]) >= len(word_list):
            self.used_words[difficulty] = []
        
        # Get available words (not recently used)
        available_words = [word for word in word_list 
                          if word["word"] not in self.used_words[difficulty]]
        
        # Get a random word from available words
        selected_word = random.choice(available_words)
        
        # Add this word to used words
        self.used_words[difficulty].append(selected_word["word"])
        
        return selected_word
    
    def start_game(self):
        difficulty = self.difficulty_var.get()
        word_data = self.get_random_word(difficulty)
        
        self.secret_word = word_data["word"]
        self.secret_hint = word_data["hint"]
        self.guessed_word = ["_"] * len(self.secret_word)
        self.tries = 6
        self.guessed_letters = []
        self.game_over = False
        
        # Reset UI
        self.message_display.config(text="")
        self.tries_label.config(text=str(self.tries))
        self.draw_hangman()
        
        # Reset keyboard
        for key in self.keys.values():
            key.config(state="normal", bg="SystemButtonFace")
        
        self.update_display()
    
    def update_display(self):
        self.word_display.config(text=" ".join(self.guessed_word))
        self.tries_label.config(text=str(self.tries))
    
    def handle_guess(self, guess):
        if self.game_over or guess in self.guessed_letters:
            return
        
        self.guessed_letters.append(guess)
        key = self.keys[guess]
        
        if guess in self.secret_word:
            # Correct guess
            key.config(bg="#a3e4a3")  # Light green
            
            for i in range(len(self.secret_word)):
                if self.secret_word[i] == guess:
                    self.guessed_word[i] = guess
            
            if "_" not in self.guessed_word:
                self.game_over = True
                self.message_display.config(text="You win! 🎉")
        else:
            # Incorrect guess
            key.config(bg="#e4a3a3")  # Light red
            self.tries -= 1
            self.draw_hangman()
            
            if self.tries == 0:
                self.game_over = True
                self.message_display.config(text=f"Game over! The word was: {self.secret_word}")
        
        key.config(state="disabled")
        self.update_display()
    
    def show_hint(self):
        if not self.game_over and self.tries > 0:
            self.message_display.config(text=f"Hint: {self.secret_hint}")

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    
    # Handle keyboard input
    def key_press(event):
        key = event.char.upper()
        if not game.game_over and key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and key not in game.guessed_letters:
            game.handle_guess(key)
    
    root.bind("<Key>", key_press)
    root.mainloop()