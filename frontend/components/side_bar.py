import customtkinter as ctk
from PIL import Image, ImageTk
from pytablericons import TablerIcons, OutlineIcon

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=100, corner_radius=0, fg_color="black")
        self.controller = controller
        self.buttons = {}

        ctk.set_appearance_mode("dark")
        self.mode = "dark"

        # Logo
        self.image = Image.open("assets/OUT__2_-removebg-preview.png")
        self.image = self.image.resize((75, 75))
        self.image = ImageTk.PhotoImage(self.image)
        self.image_label = ctk.CTkLabel(self, image=self.image, text="")
        self.image_label.pack(pady=40)

        icons = {
            "Home": OutlineIcon.HOME,
            "My Collections": OutlineIcon.BOOKS,
            "CineGuru": OutlineIcon.ROBOT
        }

        self.btn_frame = ctk.CTkFrame(self, fg_color="black")
        self.btn_frame.pack(fill="both", expand=True, anchor="center")

        menu_items = [("Home", "HomePage"), ("My Collections", "MyCollectionsPage"), ("CineGuru", "CineGuruPage")]
        for item, page in menu_items:
            button_container = ctk.CTkFrame(self.btn_frame, fg_color="black", height=40)
            button_container.pack(fill="x", padx=5, pady=2)
            button_container.pack_propagate(False)

            indicator = ctk.CTkFrame(
                button_container,
                width=4,
                height=30,
                corner_radius=10,
                fg_color="gold"
            )

            icon = TablerIcons.load(icons[item], size=24, color="#FFD700", stroke_width=2.0)
            icon_image = ImageTk.PhotoImage(icon)

            button = ctk.CTkButton(
                button_container,
                text=item,
                anchor="w",
                width=60,
                height=40,
                image=icon_image,
                corner_radius=10,
                text_color="white",
                fg_color="#333333" if page == "HomePage" else "black",
                hover_color="#333333",
                command=lambda p=page: self.navigate_to(p)
            )
            button.image = icon_image
            button.pack(side="left", fill="x", expand=True)

            if page == "HomePage":
                indicator.pack(side="left")

            self.buttons[page] = {
                'container': button_container,
                'indicator': indicator,
                'button': button
            }

        self.active_page = "HomePage"

        # Logout section
        logout_icon = TablerIcons.load(OutlineIcon.LOGOUT, size=26, color="#FFD700", stroke_width=2.0)
        logout_icon_image = ImageTk.PhotoImage(logout_icon)
        logout_frame = ctk.CTkFrame(self, fg_color="black")
        logout_frame.pack(side=ctk.BOTTOM, fill="x", padx=10, pady=10)
        logout_button = ctk.CTkButton(
            logout_frame,
            height=40,
            text="",
            image=logout_icon_image,
            fg_color="black",
            command=self.logout
        )
        logout_button.image = logout_icon_image
        logout_button.pack(side="left", fill="x", expand=True)


    def navigate_to(self, page):
        def update_ui():
            # Remove old indicator
            if self.active_page in self.buttons:
                self.buttons[self.active_page]['indicator'].pack_forget()
                self.buttons[self.active_page]['button'].configure(fg_color="black")
            
            # Set new active page
            self.active_page = page
            
            # Show new indicator
            if page in self.buttons:
                self.buttons[page]['indicator'].pack(side="left")
                self.buttons[page]['button'].configure(fg_color="#333333")
            
            # Change page
            self.controller.show_frame(page)
        
        # Schedule UI update for next event loop iteration
        self.after(1, update_ui)

    def logout(self):
        if self.active_page in self.buttons:
            self.buttons[self.active_page]['indicator'].pack_forget()
            self.buttons[self.active_page]['button'].configure(fg_color="black")
        self.active_page = None
        self.controller.show_frame("LoginPage")



