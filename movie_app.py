import customtkinter as ctk
from frontend.pages.home_page import HomePage
from frontend.pages.my_collections_page import MyCollectionsPage
from frontend.pages.cine_guru_page import CineGuruPage
from frontend.pages.login_page import LoginPage
from frontend.pages.sign_up_page import SignUpPage
from frontend.components.side_bar import Sidebar

class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CineBook")
        self.geometry("800x400")
        self.minsize(800, 400)
        self.resizable(True, True)
        self.configure(fg_color="black")

        # Property to store the currently logged-in user
        self.current_user = None 

        self.frames = {}

       

        self.attributes('-alpha', 0.90)
        self.create_container()

         
        # Create sidebar but don't pack it yet
        self.sidebar = Sidebar(self.container, self)

        # Add authentication pages
        # , CineGuruPage
        for F in (LoginPage, SignUpPage, HomePage, MyCollectionsPage, CineGuruPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
        


        # Start with LoginPage
        self.show_frame("LoginPage")

    def create_container(self):
        self.container = ctk.CTkFrame(self, fg_color="black")
        self.container.pack(side="right", fill="both", expand=True)

    def show_frame(self, page_name):

        # Show/hide sidebar based on page
        if page_name in ["LoginPage", "SignUpPage"]:
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y")


        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[page_name].pack(fill="both", expand=True)

    def set_current_user(self, username):
        """Set the currently logged-in user."""
        self.current_user = username
        print(f"Logged in as: {self.current_user}")


if __name__ == "__main__":
    # Run the MovieApp
    app = MovieApp()
    app.mainloop()  
