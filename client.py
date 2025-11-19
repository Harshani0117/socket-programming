import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

# ============================
# Configuration
# ============================
SERVER_IP = "20.193.248.167"  # Replace with Azure VM public IP
PORT = 9999
TEST_MODE = False  # Set to True to test GUI without server


class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Smart Chat Client")
        self.master.geometry("480x550")
        self.master.configure(bg="#f5f5f5")

        # Prevent window closing without disconnecting
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Username
        self.username = None

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, state='disabled',
            font=("Arial", 11), bg="#ffffff", fg="#333333"
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Message input
        self.message_entry = tk.Entry(master, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.message_entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        # Button frame
        button_frame = tk.Frame(master, bg="#f5f5f5")
        button_frame.pack(fill=tk.X)

        self.connect_button = tk.Button(
            button_frame, text="Connect", bg="lightgreen",
            command=self.connect_to_server, width=10
        )
        self.connect_button.pack(side=tk.LEFT, padx=12, pady=5)

        self.disconnect_button = tk.Button(
            button_frame, text="Disconnect", bg="tomato",
            command=self.disconnect_from_server, state='disabled', width=10
        )
        self.disconnect_button.pack(side=tk.RIGHT, padx=12, pady=5)

        self.client = None
        self.running = False

    def connect_to_server(self):
        # Ask for username before connecting
        if not self.username:
            self.username = simpledialog.askstring("Username", "Enter your name:")
            if not self.username:
                messagebox.showwarning("Warning", "Username is required!")
                return

        if TEST_MODE:
            self.display_message(f"[TEST MODE] Connected as {self.username}")
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            return

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((SERVER_IP, PORT))
            self.running = True

            self.display_message(f"[CONNECTED] {self.username} connected to {SERVER_IP}:{PORT}")
            self.client.send(f"{self.username} joined the chat".encode())

            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')

            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def receive_messages(self):
        try:
            while self.running:
                message = self.client.recv(1024).decode()
                if not message:
                    break
                self.display_message("<< " + message)
        except:
            self.display_message("[ERROR] Connection lost")
        finally:
            self.disconnect_from_server()

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return  # Prevent sending empty messages

        if TEST_MODE:
            self.display_message(f">> {self.username}: {message}")
            self.message_entry.delete(0, tk.END)
            return

        if self.client:
            try:
                full_message = f"{self.username}: {message}"
                self.client.send(full_message.encode())
                self.display_message(">> " + full_message)
                self.message_entry.delete(0, tk.END)
            except:
                self.display_message("[ERROR] Unable to send message")

    def disconnect_from_server(self):
        self.running = False
        try:
            if self.client:
                self.client.send(f"{self.username} disconnected".encode())
                self.client.close()
        except:
            pass

        self.display_message("[DISCONNECTED]")
        self.connect_button.config(state='normal')
        self.disconnect_button.config(state='disabled')

    def on_close(self):
        if self.running:
            if messagebox.askyesno("Exit", "Disconnect first?"):
                self.disconnect_from_server()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatClientGUI(root)
    root.mainloop()
