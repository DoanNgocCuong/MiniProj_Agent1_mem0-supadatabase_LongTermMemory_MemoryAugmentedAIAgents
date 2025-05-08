from mem0 import MemoryClient
import tkinter as tk
from tkinter import scrolledtext
import threading

# Set up Mem0 client
client = MemoryClient(api_key="m0-taw5e5N03yG5Di4bWlsBd4eEVyIHsi4BOzwoWKqQ")

# Sample user info - this would come from user registration in a real app
USER_ID = "alex"

# Initialize with some info
def initialize_user():
    messages = [
        {"role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and I'm allergic to nuts."},
        {"role": "assistant", "content": "Hello Alex! I've noted that you're a vegetarian and have a nut allergy. I'll keep this in mind for any food-related recommendations or discussions."}
    ]
    client.add(messages, user_id=USER_ID)

# Create chat UI
class ChatApp:
    def __init__(self, root):
        self.root = root
        root.title("Mem0 Chat")
        root.geometry("600x700")
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=30)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED)
        
        # Message input
        self.message_input = tk.Entry(root, width=50)
        self.message_input.grid(row=1, column=0, padx=10, pady=10)
        self.message_input.bind("<Return>", self.send_message)
        
        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Initialize with welcome message
        self.update_chat("Assistant: Hello! How can I help you today?")
    
    def update_chat(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        user_message = self.message_input.get()
        if not user_message:
            return
        
        # Show user message
        self.update_chat(f"You: {user_message}")
        self.message_input.delete(0, tk.END)
        
        # Process in background to keep UI responsive
        threading.Thread(target=self.process_message, args=(user_message,)).start()
    
    def process_message(self, user_message):
        # Save message to memory
        messages = [{"role": "user", "content": user_message}]
        client.add(messages, user_id=USER_ID)
        
        # Search for relevant context
        results = client.search(user_message, user_id=USER_ID)
        
        # In a real app, you would use an LLM to generate a response
        # based on the context. Here we'll just show the context.
        response = "I found this relevant information about you:\n"
        if results and len(results) > 0:
            for item in results:
                response += f"- {item['content']}\n"
        else:
            response = "I don't have any specific information about that yet."
        
        # Update UI with assistant response
        self.root.after(0, self.update_chat, f"Assistant: {response}")


# Main app
def main():
    # Initialize user data
    initialize_user()
    
    # Start UI
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
