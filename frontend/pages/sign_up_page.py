import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import os
import json
from pytablericons import TablerIcons, OutlineIcon
from backend.config import USERS_FILE, USER_DATA_FOLDER



class SignUpPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="black", width=600, height=400)
        self.controller = controller

        # Set fixed size for the window
        self.controller.geometry("600x400")
        self.controller.resizable(True, True)

        # Left frame with image and line (from LoginPage)
        self.left_frame = ctk.CTkFrame(self, fg_color="black")
        self.left_frame.pack(side="left", fill="y", padx=20)

        self.image = Image.open("assets/OUT__1_-removebg-preview.png")  # Adjust the image path if needed
        self.image = self.image.resize((250, 300))  # Resize the image
        self.image = ImageTk.PhotoImage(self.image)

        self.image_label = ctk.CTkLabel(self.left_frame, image=self.image, text="")
        self.image_label.pack(pady=20, expand=True)

        # Right frame for form elements
        self.right_frame = ctk.CTkFrame(self, fg_color="black")
        self.right_frame.pack(side="left", fill="both", expand=True)

          # Create a vertical line (using pack)
        self.left_line = ctk.CTkCanvas(self.right_frame, width=1, bg="white", highlightthickness=0)
        self.left_line.pack(side="left", fill="y")
        self.left_line.create_line(0, 0, 1, 400, fill="black", width=1)


                # Create a frame for centering the login form
        self.center_frame = ctk.CTkFrame(self.right_frame, fg_color="black")
        self.center_frame.pack(side="left", expand=True, anchor="center")  # Center it within the right frame

        # Create icons
        icon_user = TablerIcons.load(OutlineIcon.USER, size=24, color="#FFD700", stroke_width=2.0)
        icon_user_image = ImageTk.PhotoImage(icon_user)

        icon_password = TablerIcons.load(OutlineIcon.KEY, size=24, color="#FFD700", stroke_width=2.0)
        icon_password_image = ImageTk.PhotoImage(icon_password)

        icon_email = TablerIcons.load(OutlineIcon.MAIL, size=24, color="#FFD700", stroke_width=2.0)
        icon_email_image = ImageTk.PhotoImage(icon_email)

        self.title_label = ctk.CTkLabel(self.center_frame, text="Sign Up", font=("Arial", 24), text_color="white")
        self.title_label.pack(pady=20)

        # Username frame and widgets
        username_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        username_frame.pack(pady=10)

        username_icon = ctk.CTkLabel(username_frame, text="", image=icon_user_image)
        username_icon.pack(side="left", padx=5)

        self.username_entry = ctk.CTkEntry(username_frame, placeholder_text="Username", fg_color="black", width=250)
        self.username_entry.pack(side="left")

        # Password frame and widgets
        password_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        password_frame.pack(pady=10)

        password_icon = ctk.CTkLabel(password_frame, text="", image=icon_password_image)
        password_icon.pack(side="left", padx=5)

        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", fg_color="black", width=250)
        self.password_entry.pack(side="left")

        # Confirm Password frame and widgets
        confirm_password_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        confirm_password_frame.pack(pady=10)

        confirm_password_icon = ctk.CTkLabel(confirm_password_frame, text="", image=icon_password_image)
        confirm_password_icon.pack(side="left", padx=5)

        self.confirm_password_entry = ctk.CTkEntry(confirm_password_frame, placeholder_text="Confirm Password", show="*", fg_color="black", width=250)
        self.confirm_password_entry.pack(side="left")

        # Email frame and widgets
        email_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        email_frame.pack(pady=10)

        email_icon = ctk.CTkLabel(email_frame, text="", image=icon_email_image)
        email_icon.pack(side="left", padx=5)

        self.email_entry = ctk.CTkEntry(email_frame, placeholder_text="Email", fg_color="black", width=250)
        self.email_entry.pack(side="left")

        self.sign_up_button = ctk.CTkButton(self.center_frame, border_width=2, border_color="#FFD700", fg_color="black", text="Sign Up", command=self.register_user)
        self.sign_up_button.pack(pady=10)

        self.login_button = ctk.CTkButton(self.center_frame,text_color="black", text="Back to Login", fg_color="#FFD700", command=self.go_to_login)
        self.login_button.pack(pady=10)

    def go_to_login(self):
        self.clear_entries()
        self.controller.show_frame("LoginPage")

    def clear_entries(self):
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.confirm_password_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def load_users(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)

        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_users(self, users):
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

    def create_user_file(self, username):
        os.makedirs(USER_DATA_FOLDER, exist_ok=True)
        user_file = os.path.join(USER_DATA_FOLDER, f"{username}.json")
        if not os.path.exists(user_file):
            with open(user_file, "w") as f:
                json.dump({}, f)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()

        if not username or not password or not confirm_password or not email:
            CTkMessagebox(title="Sign Up Error", message="All fields are required", icon="cancel")
            return

        if password != confirm_password:
            CTkMessagebox(title="Sign Up Error", message="Passwords do not match", icon="cancel")
            return

        users = self.load_users()

        if username in users:
            CTkMessagebox(title="Sign Up Error", message="User already exists", icon="cancel")
        else:
            users[username] = {
                "password": password,
                "email": email
            }
            self.save_users(users)
            self.create_user_file(username)

            CTkMessagebox(title="Sign Up Success", message=f"User {username} registered successfully", icon="check")
            self.controller.show_frame("LoginPage")



