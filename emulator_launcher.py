"""
Simple GUI Launcher for Vision System Firmware Emulator
Allows easy startup without command line
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os
import sys
from pathlib import Path

class EmulatorLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Vision System Firmware Emulator Launcher")
        self.root.geometry("600x650")  # Increased height for flow control options
        self.root.resizable(False, False)
        
        self.process = None
        self.is_running = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create UI elements"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="Vision System Firmware Emulator",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)
        
        status_text = tk.Label(
            header_frame,
            text="COM Port: COM1 (Arduino) ↔ COM2 (Emulator)",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        status_text.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Control Frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Flow Control Options
        flow_control_frame = tk.Frame(self.root, bg="#ecf0f1", padx=20, pady=10)
        flow_control_frame.pack(fill=tk.X, padx=0, pady=0)
        
        flow_label = tk.Label(
            flow_control_frame,
            text="Flow Control (if VISA error 0x03000105 occurs):",
            font=("Arial", 9, "bold"),
            bg="#ecf0f1"
        )
        flow_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.flow_control_var = tk.StringVar(value="none")
        flow_options_frame = tk.Frame(flow_control_frame, bg="#ecf0f1")
        flow_options_frame.pack(anchor=tk.W, padx=40, pady=(0, 5))
        
        tk.Radiobutton(flow_options_frame, text="None (default)", variable=self.flow_control_var, 
                      value="none", bg="#ecf0f1", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Radiobutton(flow_options_frame, text="RTS/CTS", variable=self.flow_control_var,
                      value="rtscts", bg="#ecf0f1", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Radiobutton(flow_options_frame, text="DSR/DTR", variable=self.flow_control_var,
                      value="dsrdtr", bg="#ecf0f1", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Radiobutton(flow_options_frame, text="RTS/CTS + DSR/DTR", variable=self.flow_control_var,
                      value="both", bg="#ecf0f1", font=("Arial", 9)).pack(anchor=tk.W)
        
        # Start Button
        self.start_btn = tk.Button(
            control_frame,
            text="▶ START EMULATOR",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_emulator,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop Button
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ STOP EMULATOR",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10,
            command=self.stop_emulator,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear Logs Button
        clear_btn = tk.Button(
            control_frame,
            text="🗑 Clear Logs",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=10,
            command=self.clear_logs,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Status Label
        self.status_label = tk.Label(
            self.root,
            text="Status: Idle (Ready to start)",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        # Logs
        log_label = tk.Label(self.root, text="Live Output:", font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            height=15,
            width=70,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="#00ff00"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.log_text.config(state=tk.DISABLED)
        
        # Info at bottom
        info_frame = tk.Frame(self.root, bg="#ecf0f1")
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        info_text = tk.Label(
            info_frame,
            text="ℹ️ After clicking START, open your LabVIEW app and connect to Arduino COM port.",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#2c3e50",
            wraplength=550,
            justify=tk.LEFT
        )
        info_text.pack(anchor=tk.W)
        
    def log(self, message):
        """Add message to log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def start_emulator(self):
        """Start the emulator process"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Emulator is already running!")
            return
        
        self.clear_logs()
        self.log("[INFO] Starting Vision System Firmware Emulator...")
        self.log("[INFO] COM Port: COM2 (ELTIMA Emulator)")
        self.log("[INFO] Arduino Port: COM1 (for LabVIEW)")
        self.log("[INFO] Baud Rate: 115200")
        self.log("[INFO] Waiting for LabVIEW connection...")
        self.log("-" * 60)
        
        # Start emulator in background thread
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: ▶ Running...", fg="#27ae60")
        
        thread = threading.Thread(target=self._run_emulator, daemon=True)
        thread.start()
        
    def _check_dependencies(self) -> bool:
        """Check that required packages are installed. Returns True if OK."""
        missing = []
        try:
            import flask  # noqa: F401
        except ImportError:
            missing.append("flask")
        try:
            import flask_cors  # noqa: F401
        except ImportError:
            missing.append("flask-cors")
        try:
            import serial  # noqa: F401
        except ImportError:
            missing.append("pyserial")

        if missing:
            self.log(f"[ERROR] Missing Python packages: {', '.join(missing)}")
            self.log("[INFO] Install them by running in a terminal:")
            self.log(f"       {sys.executable} -m pip install {' '.join(missing)}")
            self.log("[INFO] Then restart the launcher.")
            self.root.after(0, lambda: self.status_label.config(
                text="Status: ❌ Missing dependencies - see log", fg="#e74c3c"))
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            return False
        return True

    def _run_emulator(self):
        """Run emulator in background thread"""
        try:
            # Get the emulator script path
            emulator_dir = Path(__file__).parent
            script_path = emulator_dir / "firmware_emulator" / "src" / "main.py"
            
            if not script_path.exists():
                self.log(f"[ERROR] Script not found: {script_path}")
                self.status_label.config(text="Status: ❌ Error - Script not found", fg="#e74c3c")
                return

            if not self._check_dependencies():
                return

            self.log(f"[INFO] Script: {script_path}")
            self.log("[INFO] Starting process...\n")
            
            # Show opcode statistics
            try:
                sys.path.insert(0, str(emulator_dir))
                from firmware_emulator.src.opcode_handler import OpcodeHandler
                import logging
                logger = logging.getLogger()
                handler = OpcodeHandler(logger)
                opcode_count = len(handler.list_handlers())
                self.log(f"[INFO] Firmware API: {opcode_count} opcodes loaded")
            except Exception as e:
                self.log(f"[WARNING] Could not load opcode statistics: {e}")
            
            # Use COM2 (ELTIMA Emulator port)
            port = "COM2"
            self.log(f"[INFO] Using port: {port}")
            
            # Get flow control selection
            flow_control = self.flow_control_var.get()
            self.log(f"[INFO] Flow control: {flow_control}")
            
            # Start emulator process
            cmd = [
                sys.executable,
                "-m", "firmware_emulator.src.main",
                "--port", port,
                "--baudrate", "115200",
                "--verbose"
            ]
            
            # Add flow control flags if selected
            if flow_control == "rtscts":
                cmd.append("--rtscts")
            elif flow_control == "dsrdtr":
                cmd.append("--dsrdtr")
            elif flow_control == "both":
                cmd.append("--rtscts")
                cmd.append("--dsrdtr")
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(emulator_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.is_running = True
            self.log("[SUCCESS] Emulator started successfully!")
            self.log("[INFO] Listening for commands on COM2 port...")
            self.log("=" * 60 + "\n")
            
            # Read output in real-time
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log(line.rstrip())
                if not self.is_running:
                    break
                    
        except Exception as e:
            self.log(f"[ERROR] Failed to start emulator: {e}")
            self.status_label.config(text=f"Status: ❌ Error", fg="#e74c3c")
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Status: ⏹ Stopped", fg="#e74c3c")
            
    def stop_emulator(self):
        """Stop the emulator process"""
        if not self.is_running or self.process is None:
            messagebox.showinfo("Not Running", "Emulator is not running")
            return
        
        self.log("\n" + "=" * 60)
        self.log("[INFO] Stopping emulator...")
        self.is_running = False
        
        try:
            self.process.terminate()
            self.process.wait(timeout=2)
            self.log("[SUCCESS] Emulator stopped")
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.log("[WARNING] Force killed emulator")
        except Exception as e:
            self.log(f"[ERROR] Error stopping emulator: {e}")


def main():
    root = tk.Tk()
    launcher = EmulatorLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
