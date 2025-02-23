import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import json
import os
from PIL import Image, ImageTk
from pytablericons import TablerIcons, OutlineIcon
from backend.config import USERS_FILE

class LoginPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="black", width=600, height=400)
        self.controller = controller

        # Disable resizing for the window
        self.controller.resizable(False, False)

        # Create a frame to hold the left side (image and line)
        self.left_frame = ctk.CTkFrame(self, fg_color="black")
        self.left_frame.pack(side="left", fill="y", padx=20)

        # Load the image and create a label to display it on the left
        self.image = Image.open("assets/OUT__1_-removebg-preview.png")  # Adjust the image path if needed
        self.image = self.image.resize((250, 300))  # Resize the image (optional)
        self.image = ImageTk.PhotoImage(self.image)

        self.image_label = ctk.CTkLabel(self.left_frame, image=self.image, text="")
        self.image_label.pack(expand=True, fill="both", anchor="center")  # Center the image in the frame

        # Create the right frame to hold the login form
        self.right_frame = ctk.CTkFrame(self, fg_color="black")
        self.right_frame.pack(side="left", fill="both", expand=True)

        # Create a vertical line (using pack)
        self.left_line = ctk.CTkCanvas(self.right_frame, width=1, bg="white", highlightthickness=0)
        self.left_line.pack(side="left", fill="y")
        self.left_line.create_line(0, 0, 1, 400, fill="black", width=1)


        # Create a frame for centering the login form
        self.center_frame = ctk.CTkFrame(self.right_frame, fg_color="black")
        self.center_frame.pack(side="left", expand=True, anchor="center")

        # Load the image and create a label to display it on the left
        self.welcome_image = Image.open("assets/welcome.png")  # Adjust the image path if needed
        self.welcome_image = self.welcome_image.resize((150, 150))  # Resize the image (optional)
        self.welcome_image = ImageTk.PhotoImage(self.welcome_image)

        self.welcome_image_label = ctk.CTkLabel(self.center_frame, image=self.welcome_image, text="")
        self.welcome_image_label.pack(pady=20, expand=True, anchor="center") 

        icon_login = TablerIcons.load(OutlineIcon.USER, size=24, color="#FFD700", stroke_width=2.0)
        icon_login_image = ImageTk.PhotoImage(icon_login)

        icon_password = TablerIcons.load(OutlineIcon.KEY, size=24, color="#FFD700", stroke_width=2.0)
        con_password_image = ImageTk.PhotoImage(icon_password)

        self.title_label = ctk.CTkLabel(self.center_frame, text="Please enter login details below           ", font=("Arial", 12), text_color="white")
        self.title_label.pack(pady=(0,5))

        # Create frame for username input group
        username_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        username_frame.pack(pady=(0, 10))

        self.login_label = ctk.CTkLabel(username_frame, text="", image=icon_login_image)
        self.login_label.pack(side="left", padx=5)

        self.username_entry = ctk.CTkEntry(username_frame, placeholder_text="Username", fg_color="black", width=250)
        self.username_entry.pack(side="left")

        # Create frame for password input group
        password_frame = ctk.CTkFrame(self.center_frame, fg_color="black")
        password_frame.pack(pady=10)

        self.password_label = ctk.CTkLabel(password_frame, text="", image=con_password_image)
        self.password_label.pack(side="left", padx=5)

        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", fg_color="black", width=250)
        self.password_entry.pack(side="left")

        self.login_button = ctk.CTkButton(
            self.center_frame,
            text="Login",
            command=self.login_user,
            fg_color="black",  # Background color (green)
            # hover_color="#FFA500",  # Hover background color
            text_color="white",  # Text color (white)
            border_width=2,  # Border width
            border_color="#FFD700" # Border color (dark green)
        )
        self.login_button.pack(pady=(20, 10))

        self.sign_up_button = ctk.CTkButton(
            self.center_frame,
            text="Sign Up",
            command=lambda: controller.show_frame("SignUpPage"),
            fg_color="#FFD700",  # Background color (blue)
            hover_color="#007bb5",  # Hover background color
            text_color="black",  # Text color (white)
            # border_width=2,  # Border width
            # border_color="#005f73"  # Border color (dark blue)
        )
        self.sign_up_button.pack(pady=10)

    def load_users(self):
        """Load user credentials."""
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)

        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        users = self.load_users()

        if username in users:
            if users[username]["password"] == password:
                self.controller.set_current_user(username)

                my_collections_page = self.controller.frames["MyCollectionsPage"]
                my_collections_page.refresh_movies()

                self.controller.show_frame("HomePage")
                CTkMessagebox(message="Login successful. Welcome back!", icon="check", option_1="Thanks")

                self.username_entry.delete(0, "end")  # Clear username entry
                self.password_entry.delete(0, "end")  # Clear password entry

            else:
                CTkMessagebox(title="Login Error", message="Incorrect password. Please try again.", icon="cancel")
        else:
            CTkMessagebox(title="User Not Found", message=f"User '{username}' does not exist.", icon="info")

