import customtkinter as ctk
from backend.cine_guru_backend import CineGuruBackend
from frontend.components.movie_card import MovieContainer
from PIL import Image, ImageTk
from pytablericons import TablerIcons, OutlineIcon

class CineGuruPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="black")
        self.controller = controller

        # Initialize backend
        self.backend = CineGuruBackend()

        # Left line
        self.left_line = ctk.CTkCanvas(self, width=1, bg="white", highlightthickness=0)
        self.left_line.pack(side="left", fill="y")
        self.left_line.create_line(0, 0, 1, 800, fill="black", width=1)

        # Robot image
        self.robot_image = Image.open("assets/robot.png").resize((100, 100))
        self.robot_image = ImageTk.PhotoImage(self.robot_image)
        self.robot_image_label = ctk.CTkLabel(self, image=self.robot_image, text="")
        self.robot_image_label.pack(pady=40)

        # Hi frame
        hi_frame = ctk.CTkFrame(self, fg_color="transparent")
        hi_frame.pack(pady=20)

        self.hi_image = Image.open("assets/hi.png").resize((20, 20))
        self.hi_image = ImageTk.PhotoImage(self.hi_image)
        self.hi_image_label = ctk.CTkLabel(hi_frame, image=self.hi_image, text="")
        self.hi_image_label.grid(row=0, column=1, padx=5)

        label = ctk.CTkLabel(hi_frame, text="Hi, I'm CineGuru", text_color="white", font=("Arial", 20))
        label.grid(row=0, column=0, padx=5)

        # Input frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=10)

        self.user_input_entry = ctk.CTkEntry(input_frame, placeholder_text="Tell me about your feelings...", width=400, corner_radius=20)
        self.user_input_entry.grid(row=0, column=0, padx=5)

        icon_camera = TablerIcons.load(OutlineIcon.CAMERA_COG, size=24, color="#FFFFFF", stroke_width=2.0)
        icon_camera_image = ImageTk.PhotoImage(icon_camera)

        self.recommend_button = ctk.CTkButton(input_frame, image=icon_camera_image, width=20, text="", fg_color="#FFD700",
                                              command=self.get_recommendations, corner_radius=20)
        self.recommend_button.grid(row=0, column=1, padx=5)

        # Scrollable container
        self.results_frame = ctk.CTkFrame(self, fg_color="black")
        self.results_frame.pack(fill="both", expand=True, pady=20, padx=20)

        self.canvas = ctk.CTkCanvas(self.results_frame, bg="black", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.results_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_inner_frame = ctk.CTkFrame(self.canvas, fg_color="black")

        self.scrollable_inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def get_recommendations(self):
        """
        Fetch user input, get recommendations from the backend, and display them in the UI.
        """
        user_input = self.user_input_entry.get()
        current_user = self.controller.current_user

        # Call the backend method to get movie recommendations
        recommendations = self.backend.recommend_movies(user_input)

        # Clear previous results
        for widget in self.scrollable_inner_frame.winfo_children():
            widget.destroy()

        # If recommendations are returned as a list of tuples (score, movie), display them
        if isinstance(recommendations, list):
            row, col = 0, 0
            widgets_per_row = self.calculate_widgets_per_row()

            for score, movie in recommendations:
                if col == widgets_per_row:
                    col = 0
                    row += 1

                # Ensure movie_id is passed here
                movie_id = movie.get('id')  # Ensure the 'id' field is available in the movie dictionary

                if movie.get("movie_id"):  # Check if movie_id exists
                    try:
                        movie_id = movie.get("movie_id", "Unknown ID")  # Get the movie_id, default to "Unknown ID" if not found
                        movie_container = MovieContainer(
                            self.scrollable_inner_frame,
                            movie_id=movie_id,  # Pass movie_id
                            username=current_user,
                            initial_status="To Watch",  # Example initial status
                            initial_rating=0,  # Example initial rating
                            initial_notes="",  # Example initial notes
                            show_buttons=["save"],  # Example buttons
                        )
                        movie_container.grid(row=row, column=col, padx=18, pady=20)
                        col += 1
                    except Exception as e:
                        print(f"Error creating MovieContainer for movie {movie}: {e}")
                else:
                    print(f"Error: No movie ID provided for movie: {movie}")

        else:
            # Display error or no results message
            no_results_label = ctk.CTkLabel(self.scrollable_inner_frame, text=recommendations, text_color="white")
            no_results_label.pack(pady=20)

    def calculate_widgets_per_row(self):
        window_width = self.winfo_width()
        return max(1, window_width // 200)