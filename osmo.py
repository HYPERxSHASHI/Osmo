import datetime
import queue
import subprocess
import threading
import webbrowser
from dataclasses import dataclass

import pyttsx3
import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox, scrolledtext


@dataclass
class AssistantState:
    listening: bool = False
    wake_word_heard: bool = False


class OsmoAssistant:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OSMO - Personal AI Assistant")
        self.root.geometry("980x640")
        self.root.configure(bg="#f8f8f2")

        self.state = AssistantState()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.event_queue: queue.Queue[str] = queue.Queue()

        self._build_ui()
        self._start_queue_processor()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="OSMO • Personal AI Assistant",
            font=("Segoe UI", 24, "bold"),
            bg="#f8f8f2",
            fg="#4e342e",
        )
        title.pack(pady=(18, 8))

        subtitle = tk.Label(
            self.root,
            text="White + Chocolate Brown Theme | Wake phrase: 'Hey Osmo'",
            font=("Segoe UI", 11),
            bg="#f8f8f2",
            fg="#6d4c41",
        )
        subtitle.pack(pady=(0, 14))

        button_frame = tk.Frame(self.root, bg="#f8f8f2")
        button_frame.pack(pady=8)

        self.listen_btn = tk.Button(
            button_frame,
            text="Start Listening",
            command=self.toggle_listening,
            font=("Segoe UI", 12, "bold"),
            width=18,
            bg="#6d4c41",
            fg="#ffffff",
            activebackground="#8d6e63",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
        )
        self.listen_btn.grid(row=0, column=0, padx=8)

        speak_btn = tk.Button(
            button_frame,
            text="Say Hello",
            command=lambda: self.speak("What happened sir, do you need something?"),
            font=("Segoe UI", 12, "bold"),
            width=18,
            bg="#a1887f",
            fg="#ffffff",
            activebackground="#8d6e63",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
        )
        speak_btn.grid(row=0, column=1, padx=8)

        self.command_input = tk.Entry(
            self.root,
            font=("Consolas", 12),
            width=72,
            bd=1,
            relief=tk.SOLID,
            fg="#3e2723",
        )
        self.command_input.pack(pady=(14, 8), ipady=8)

        run_btn = tk.Button(
            self.root,
            text="Run Typed Command",
            command=self.run_typed_command,
            font=("Segoe UI", 11, "bold"),
            bg="#5d4037",
            fg="#ffffff",
            activebackground="#8d6e63",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
        )
        run_btn.pack(pady=(0, 10))

        self.log = scrolledtext.ScrolledText(
            self.root,
            font=("Consolas", 11),
            width=110,
            height=24,
            bg="#fffdf8",
            fg="#3e2723",
            insertbackground="#3e2723",
            bd=1,
            relief=tk.SOLID,
        )
        self.log.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.log.insert(
            tk.END,
            "OSMO boot complete.\nSay 'Hey Osmo' to activate voice command mode.\n"
            "You can also type commands and click 'Run Typed Command'.\n\n"
        )
        self.log.config(state=tk.DISABLED)

    def _start_queue_processor(self) -> None:
        self.root.after(120, self._process_queue)

    def _process_queue(self) -> None:
        while not self.event_queue.empty():
            item = self.event_queue.get()
            self.write_log(item)
        self.root.after(120, self._process_queue)

    def write_log(self, msg: str) -> None:
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def speak(self, text: str) -> None:
        self.event_queue.put(f"OSMO: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def toggle_listening(self) -> None:
        self.state.listening = not self.state.listening
        if self.state.listening:
            self.listen_btn.config(text="Stop Listening", bg="#8d6e63")
            threading.Thread(target=self.listen_loop, daemon=True).start()
            self.event_queue.put("[System] Voice listener started.")
        else:
            self.listen_btn.config(text="Start Listening", bg="#6d4c41")
            self.event_queue.put("[System] Voice listener stopped.")

    def listen_loop(self) -> None:
        while self.state.listening:
            try:
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio).lower().strip()
                self.event_queue.put(f"You: {text}")
                self.handle_voice_text(text)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as exc:
                self.event_queue.put(f"[Error] Voice recognition issue: {exc}")

    def handle_voice_text(self, text: str) -> None:
        if "hey osmo" in text:
            self.state.wake_word_heard = True
            self.speak("What happened sir, do you need something?")
            return

        if not self.state.wake_word_heard:
            return

        self.execute_command(text)
        self.state.wake_word_heard = False

    def run_typed_command(self) -> None:
        command = self.command_input.get().strip()
        if not command:
            return
        self.event_queue.put(f"Typed command: {command}")
        self.execute_command(command.lower())
        self.command_input.delete(0, tk.END)

    def execute_command(self, command: str) -> None:
        if "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"Current time is {now}")

        elif "date" in command or "day" in command:
            today = datetime.datetime.now().strftime("%A, %d %B %Y")
            self.speak(f"Today is {today}")

        elif command.startswith("open "):
            target = command.replace("open ", "", 1).strip()
            self.open_target(target)

        elif command.startswith("search "):
            query = command.replace("search ", "", 1).strip()
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            self.speak(f"Searching for {query}")

        elif command.startswith("run command "):
            shell_cmd = command.replace("run command ", "", 1).strip()
            self.run_shell_command(shell_cmd)

        elif "shutdown" in command:
            self.speak("Shutdown command blocked by default for safety.")

        elif "help" in command:
            self.speak(
                "You can ask for time, date, open app or website, search topic, or run command with confirmation."
            )

        else:
            self.speak("I did not understand that command. Say help for available options.")

    def open_target(self, target: str) -> None:
        basic_apps = {
            "notepad": "notepad",
            "calculator": "calc",
            "explorer": "explorer",
            "cmd": "cmd",
            "powershell": "powershell",
        }

        if target in basic_apps:
            subprocess.Popen(basic_apps[target], shell=True)
            self.speak(f"Opening {target}")
            return

        if target.startswith("http") or "." in target:
            url = target if target.startswith("http") else f"https://{target}"
            webbrowser.open(url)
            self.speak(f"Opening {target}")
            return

        self.speak("I can open common apps or websites. Try open notepad or open youtube dot com.")

    def run_shell_command(self, shell_cmd: str) -> None:
        allow = messagebox.askyesno(
            "Safety Check",
            f"Allow OSMO to run this command?\n\n{shell_cmd}\n\nOnly continue if you trust this command.",
        )
        if not allow:
            self.speak("Command cancelled.")
            return

        try:
            result = subprocess.run(
                shell_cmd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=30,
            )
            output = result.stdout.strip() or result.stderr.strip() or "(No output)"
            self.event_queue.put(f"[Command Output]\n{output}\n")
            self.speak("Command execution finished.")
        except Exception as exc:
            self.event_queue.put(f"[Error] Command failed: {exc}")
            self.speak("Unable to run that command.")


def main() -> None:
    root = tk.Tk()
    app = OsmoAssistant(root)
    app.speak("OSMO is online. Say Hey Osmo to start.")
    root.mainloop()


if __name__ == "__main__":
    main()
