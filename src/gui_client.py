import tkinter as tk
import threading
import time
from tkinter import ttk, scrolledtext
from base_client import JarvesClientBase
import tkinter.messagebox as messagebox


class JarvesClientGUI(tk.Tk, JarvesClientBase):
    def __init__(self, host, port):
        tk.Tk.__init__(self)
        JarvesClientBase.__init__(self, port)

        self.title("Jarves Chat")
        self.geometry("800x600")

        self.create_widgets()

        user_list_update_thread = threading.Thread(
            target=self.update_user_list_periodically)
        user_list_update_thread.daemon = True
        user_list_update_thread.start()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_exit(self):
        try:
            self.logout()
        except Exception as e:
            print("Error logging out:", e)
        self.destroy()

    def create_widgets(self):
        # Create frames
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        print("stub:", self.stub)
        if not self.stub:
            self.retry_button = ttk.Button(
                top_frame, text="Retry Connection", command=self.retry_connection)
            self.retry_button.pack(side=tk.LEFT, padx=5)
            messagebox.showerror(
                "Error", "Failed to establish connection. Click the Retry Connection button to try again.")

        chat_frame = ttk.Frame(self)
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        recipient_frame = ttk.Frame(self)
        recipient_frame.pack(side=tk.TOP, fill=tk.X)

        message_frame = ttk.Frame(self)
        message_frame.pack(side=tk.TOP, fill=tk.X)

        # Create input fields and labels
        self.logged_in_label = ttk.Label(top_frame, text="Logged in as:")
        self.logged_in_label.pack(side=tk.LEFT, padx=5)
        self.logged_in_label.pack_forget()

        self.username_label = ttk.Label(top_frame, text="Username:")
        self.username_label.pack(side=tk.LEFT, padx=5)

        self.username_entry = ttk.Entry(top_frame)
        self.username_entry.pack(side=tk.LEFT, padx=5)

        self.password_label = ttk.Label(top_frame, text="Password:")
        self.password_label.pack(side=tk.LEFT, padx=5)

        self.password_entry = ttk.Entry(top_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5)

        # Create buttons
        self.signup_button = ttk.Button(
            top_frame, text="Sign up", command=self.signup)
        self.signup_button.pack(side=tk.LEFT, padx=5)

        # Create buttons
        self.login_button = ttk.Button(
            top_frame, text="Login", command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        # logout button
        self.logout_button = ttk.Button(
            top_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.LEFT, padx=5)
        self.logout_button.pack_forget()

        # Create chat display area
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state='disabled')
        self.chat_text.pack(fill=tk.BOTH, expand=True)

        # Create message input field and send button
        self.message_entry = ttk.Entry(message_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        send_button = ttk.Button(
            message_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=5)

        recipient_label = ttk.Label(recipient_frame, text="To:")
        recipient_label.pack(side=tk.LEFT, padx=5)

        choosen_recipient = tk.StringVar()
        self.recipient_combobox = ttk.Combobox(
            recipient_frame, state="readonly", textvariable=choosen_recipient)
        self.recipient_combobox.pack(
            side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Add this line to bind the callback function to the variable
        self.recipient_combobox.bind(
            "<<ComboboxSelected>>", self.load_chat_history)

        list_users_button = ttk.Button(
            recipient_frame, text="List Users", command=self.display_users)
        list_users_button.pack(side=tk.RIGHT, padx=5)
        clear_button = ttk.Button(
            chat_frame, text="Clear", command=self.clear_chat)
        clear_button.pack(side=tk.BOTTOM, pady=5)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        response = JarvesClientBase.create_account(self, username, password)
        if response.error_code != 0:
            messagebox.showerror("Error", response.error_message)
            return
        self.login()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        response = JarvesClientBase.login(self, username, password)

        if response.error_code == 0:
            self.user_session_id = response.session_id
            # threading.Thread(target=self.receive_thread).start()
            self.username_label.pack_forget()
            self.username_entry.pack_forget()
            self.password_label.pack_forget()
            self.password_entry.pack_forget()
            self.login_button.pack_forget()
            self.signup_button.pack_forget()

            self.logout_button.pack(side="left", padx=(10, 0))

            self.logged_in_label.config(text=f"Logged in as: {username}")
            self.logged_in_label.pack(side="left")

        else:
            messagebox.showerror("Error", response.error_message)

    def logout(self):
        response = JarvesClientBase.logout(self)

        if response.error_code == 0:
            self.logged_in_label.pack_forget()
            self.logout_button.pack_forget()

            self.username_label.pack(side="left")
            self.username_entry.pack(side="left")
            self.password_label.pack(side="left")
            self.password_entry.pack(side="left")
            self.login_button.pack(side="left")
            self.signup_button.pack(side="left")

    def display_users(self):
        response = JarvesClientBase.list_users(self)

        if response:
            users = [user for user in response]

            self.recipient_combobox["values"] = tuple(
                [user.username for user in users])

            self.chat_text.config(state='normal')
            self.chat_text.insert(tk.END, "List of users:\n")
            for user in users:
                self.chat_text.insert(
                    tk.END, f"{user.username} [{user.status}]\n")
            self.chat_text.config(state='disabled')

    def send_message(self):
        to = self.recipient_combobox.get()
        message = self.message_entry.get()

        if to and message:
            response = JarvesClientBase.send_message(self, to, message)
            if response.error_code == 0:
                self.message_entry.delete(0, tk.END)
                # self.display_message(f"You: {message}")
            else:
                messagebox.showerror("Error", response.error_message)
        else:
            messagebox.showerror(
                "Error", "Please select a recipient and enter a message.")

    def retry_connection(self):
        self.connect()
        if self.stub:
            messagebox.showinfo("Success", "Connection re-established.")
            self.retry_button.pack_forget()
        else:
            messagebox.showerror(
                "Error", "Failed to establish connection. Try again.")

    def clear_chat(self):
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state='disabled')

    def load_chat_history(self, event):
        recipient = event.widget.get()

        print("inside load_chat_history: ", recipient)

        if recipient:
            response = JarvesClientBase.get_chat(self, recipient)

            if response.error_code == 0:
                self.clear_chat()
                self.chat_text.config(state='normal')
                self.chat_text.delete(1.0, tk.END)
                for message in response.message:
                    self.chat_text.insert(
                        tk.END, f"{message.from_}: {message.message}")
                self.chat_text.config(state='disabled')
            else:
                print(response.error_message)

    def receive_thread(self):
        while True:
            msgs = JarvesClientBase.receive_messages(self)

            if msgs.error_code != 0:
                time.sleep(1)
                continue
            else:
                for message in msgs.message:
                    self.display_message(f"{message.from_}: {message.message}")

                # Send acknowledgment for the received messages
                message_ids = [msg.id for msg in msgs.message]
                ack_response = JarvesClientBase.acknowledge_received_messages(
                    self, message_ids)

                if ack_response.error_code != 0:
                    print(
                        f"Error acknowledging messages: {ack_response.error_message}")
                    return

                if msgs.error_code != 0:
                    return

    def update_user_list_periodically(self, interval=10):
        while True:
            users = self.list_users()

            self.recipient_combobox['values'] = [
                user.username for user in users]
            time.sleep(interval)

    @classmethod
    def run(cls, host, port):
        app = cls(host, port)
        app.mainloop()


if __name__ == "__main__":
    JarvesClientGUI.run("localhost", 2627)
