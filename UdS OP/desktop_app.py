import asyncio
import re
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from typing import Optional

from app.agent.udsop import udsop
from app.logger import logger


class UdsopDesktopApp:
    """Desktop application for the UdS_OP agent"""

    def __init__(self, root):
        self.root = root
        self.root.title("UdS_OP Desktop Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Initialize the agent
        self.agent = udsop()
        self.processing = False
        
        # Apply styling
        self._apply_styling()
        
        # Create UI elements
        self._create_ui()
        
        # Welcome message
        self._append_to_output("Assistant: Welcome to the UdS_OP Desktop Assistant! Type your instruction or question below.")
        
    def _apply_styling(self):
        """Apply styling to the application"""
        style = ttk.Style()
        
        # Set theme if available
        try:
            style.theme_use("clam")  # 'clam', 'alt', 'default', 'classic'
        except tk.TclError:
            pass  # Theme not available
        
        # Configure styles
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabelframe", background="#f5f5f5")
        style.configure("TLabelframe.Label", foreground="#333333", background="#f5f5f5", font=("TkDefaultFont", 10, "bold"))
        style.configure("TButton", foreground="#333333", background="#dddddd", font=("TkDefaultFont", 10))
        style.map("TButton", 
                  foreground=[("pressed", "#000000"), ("active", "#000000")],
                  background=[("pressed", "#cccccc"), ("active", "#eeeeee")])
        style.configure("TLabel", foreground="#333333", background="#f5f5f5", font=("TkDefaultFont", 10))
        
    def _create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Middle section - Conversation history
        self.output_frame = ttk.LabelFrame(main_frame, text="Conversation History")
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_area = scrolledtext.ScrolledText(
            self.output_frame, wrap=tk.WORD, state=tk.DISABLED, 
            width=70, height=20, font=("TkDefaultFont", 10),
            background="#ffffff"
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom section - Input
        input_frame = ttk.Frame(main_frame, padding="5")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_label = ttk.Label(input_frame, text="Your instruction or question:")
        self.input_label.pack(anchor=tk.W, padx=5)
        
        input_box_frame = ttk.Frame(input_frame)
        input_box_frame.pack(fill=tk.X, expand=True)
        
        self.input_area = scrolledtext.ScrolledText(
            input_box_frame, wrap=tk.WORD, height=4, 
            font=("TkDefaultFont", 10), background="#ffffff"
        )
        self.input_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_area.bind("<Return>", self._on_enter)
        self.input_area.bind("<Control-Return>", self._insert_newline)
        
        self.submit_button = ttk.Button(
            input_box_frame, text="Submit", command=self._process_input,
            style="TButton"
        )
        self.submit_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _on_enter(self, event):
        """Handle Enter key press"""
        if not event.state & 0x4:  # If Ctrl is not pressed
            self._process_input()
            return "break"  # Prevent default behavior
        return None
    
    def _insert_newline(self, event):
        """Handle Ctrl+Enter key press to insert a newline"""
        return None  # Allow default behavior (insert newline)
    
    def _process_input(self):
        """Process the user's input"""
        if self.processing:
            return
        
        user_input = self.input_area.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        self._append_to_output(f"You: {user_input}")
        self.input_area.delete("1.0", tk.END)
        
        # Disable UI during processing
        self.processing = True
        self.status_var.set("Processing...")
        self.submit_button.configure(state=tk.DISABLED)
        
        # Use a thread to avoid blocking the UI
        threading.Thread(target=self._run_agent, args=(user_input,), daemon=True).start()
    
    def _run_agent(self, user_input: str):
        """Run the agent in a separate thread"""
        # Create and run a new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create a future for the agent's response
        output_collector = OutputCollector()
        
        # Patch the agent's logger to capture output
        original_info = logger.info
        original_error = logger.error
        
        try:
            # Override logger.info and logger.error
            def capture_info(msg, *args, **kwargs):
                original_info(msg, *args, **kwargs)
                output_collector.add_output(msg)
            
            def capture_error(msg, *args, **kwargs):
                original_error(msg, *args, **kwargs)
                output_collector.add_output(f"Error: {msg}")
            
            logger.info = capture_info
            logger.error = capture_error
            
            # Run the agent
            loop.run_until_complete(self.agent.run(user_input))
        except Exception as e:
            output_collector.add_output(f"An error occurred: {str(e)}")
        finally:
            # Restore original logger methods
            logger.info = original_info
            logger.error = original_error
            loop.close()
            
            # Update UI in main thread
            self.root.after(0, self._update_ui_after_processing, output_collector.get_output())
    
    def _update_ui_after_processing(self, output: str):
        """Update the UI after processing is complete"""
        # Extract only the answer part for all interactions
        formatted_output = output
        
        if output and "Request processing completed" in output:
            # Extract the answer part between the processing messages
            parts = output.split("🔍 Processing your request...")
            if len(parts) > 1:
                answer_parts = parts[1].split("✅ Request processing completed.")
                if len(answer_parts) > 1:
                    answer = answer_parts[0].strip()
                    formatted_output = f"Assistant: {answer}"
        
        # Add to conversation history
        self._append_to_output(formatted_output)
        
        # Reset UI state
        self.processing = False
        self.status_var.set("Ready")
        self.submit_button.configure(state=tk.NORMAL)
    
    def _append_to_output(self, text: str):
        """Append text to the output area"""
        self.output_area.configure(state=tk.NORMAL)
        if self.output_area.index(tk.END) != "1.0":
            self.output_area.insert(tk.END, "\n\n")
        self.output_area.insert(tk.END, text)
        self.output_area.configure(state=tk.DISABLED)
        self.output_area.see(tk.END)


class OutputCollector:
    """Helper class to collect output from the agent"""
    
    def __init__(self):
        self.output = []
    
    def add_output(self, msg: str):
        self.output.append(str(msg))
    
    def get_output(self) -> str:
        return "\n".join(self.output)


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = UdsopDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 