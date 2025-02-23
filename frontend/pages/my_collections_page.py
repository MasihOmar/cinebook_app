import customtkinter as ctk
import json
import os
import time
import shutil
from CTkMessagebox import CTkMessagebox
from frontend.components.movie_card import MovieContainer
from pytablericons import TablerIcons, OutlineIcon
from PIL import ImageTk
from backend.config import USER_DATA_FOLDER, IMAGES_FOLDER


class MyCollectionsPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="black")
        self.controller = controller
        self.resize_timer = None
        self.movie_data = []


        # Ensure images folder exists
        os.makedirs(IMAGES_FOLDER, exist_ok=True)


        self.left_line = ctk.CTkCanvas(self, width=1, bg="white", highlightthickness=0)
        self.left_line.pack(side="left", fill="y")
        self.left_line.create_line(0, 0, 1, 800, fill="black", width=1)


        self.top_frame = ctk.CTkFrame(self, fg_color="black")
        self.top_frame.pack(pady=35, padx=10, anchor='n', fill='x')

        # Configure grid columns for three sections
        self.top_frame.grid_columnconfigure(0, weight=1)  # Left space
        self.top_frame.grid_columnconfigure(1, weight=0)  # Center content
        self.top_frame.grid_columnconfigure(2, weight=1)  # Right space

        # Load icons
        icon_search = TablerIcons.load(OutlineIcon.WORLD_SEARCH, size=24, color="#FFFFFF", stroke_width=2.0)
        icon_search_image = ImageTk.PhotoImage(icon_search)

        icon_plus = TablerIcons.load(OutlineIcon.TABLE_PLUS, size=24, color="#FFFFFF", stroke_width=2.0)
        icon_plus_image = ImageTk.PhotoImage(icon_plus)

        icon_filter = TablerIcons.load(OutlineIcon.ADJUSTMENTS_ALT, size=24, color="#FFFFFF", stroke_width=2.0)
        icon_filter_image = ImageTk.PhotoImage(icon_filter)

       

        # Center section - Search
        center_frame = ctk.CTkFrame(self.top_frame, fg_color="black")
        center_frame.grid(row=0, column=1)

        self.search_entry = ctk.CTkEntry(center_frame, corner_radius=20, placeholder_text="Search by title or notes", width=300)
        self.search_entry.pack(side="left", padx=5)

        self.search_button = ctk.CTkButton(
            center_frame, 
            text="",
            fg_color="#FFD700", 
            corner_radius=20, 
            width=30, 
            height=30, 
            command=self.search_movies, 
            image=icon_search_image, 
            compound="left"
        )
        self.search_button.pack(side="left", padx=5)

        # Right section - Add Custom Movie
        right_frame = ctk.CTkFrame(self.top_frame, fg_color="black")
        right_frame.grid(row=0, column=2, sticky="e")

        self.add_movie_btn = ctk.CTkButton(
            right_frame, 
            text="", 
            command=self.show_add_movie_form,
            fg_color="#28a745",
            hover_color="#218838",
            image=icon_plus_image,
            corner_radius=20,
            width=30,
        )
        self.add_movie_btn.pack(side="right", padx=5)



        self.filter_label = ctk.CTkLabel(right_frame, text="", image=icon_filter_image, text_color="white")
        self.filter_label.pack(side="left", padx=5)

        self.status_var = ctk.StringVar(value="All")
        self.status_dropdown = ctk.CTkOptionMenu(
            right_frame,
            variable=self.status_var,
            values=["All", "Watched", "Not Watched", "Pending"],
            command=self.filter_movies,
            corner_radius=20,
            fg_color="#FFD700",  
            button_color="#FFBF00",
            text_color="black"

        )
        self.status_dropdown.pack(side="left", padx=5)


        # Container for movie posters with scrolling
        self.movies_container_frame = ctk.CTkFrame(self, fg_color="black", border_color="black", border_width=1)
        self.movies_container_frame.pack(fill="both", expand=True, pady=20, padx=20)

        self.canvas = ctk.CTkCanvas(self.movies_container_frame, bg="black", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.movies_container_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="black")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        # Load initial movies
        self.load_saved_movies()

    def calculate_widgets_per_row(self):
        window_width = self.winfo_width()
        return max(1, window_width // 200)

    def display_movies(self, movies):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not movies:
            no_results_label = ctk.CTkLabel(self.scrollable_frame, text="No movies in collection.", text_color="white")
            no_results_label.pack(pady=20)
            return

        row, col = 0, 0
        widgets_per_row = self.calculate_widgets_per_row()

        for movie in movies:
            if col == widgets_per_row:
                col = 0
                row += 1

            # Handle custom movies and TMDB movies
            movie_id = movie.get("movie_id", "Unknown ID")
            custom_data = movie if movie_id == -1 else None


            if movie.get("movie_id") is not None:
                movie_container = MovieContainer(
                    self.scrollable_frame,
                    movie_id=movie.get("movie_id", "Unknown ID"),
                    initial_status=movie.get("status", "To Watch"),
                    initial_rating=movie.get("rating", 0),
                    initial_notes=movie.get("notes", ""),
                    username=self.controller.current_user,
                    show_buttons=["delete", "update"],
                    controller=self.controller,
                    custom_data=custom_data,  # Pass custom data for custom movies
                )
                movie_container.grid(row=row, column=col, padx=18, pady=20)

            col += 1

    def on_resize(self, event=None):
        if self.resize_timer:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(300, self.update_layout)

    def update_layout(self):
        if self.movie_data:
            self.display_movies(self.movie_data)

    def load_saved_movies(self):
        current_user = self.controller.current_user
        if not current_user:
            return

        user_file = os.path.join(USER_DATA_FOLDER, f"{current_user}.json")
        if not os.path.exists(user_file):
            return

        try:
            with open(user_file, "r") as file:
                self.movie_data = json.loads(file.read())
                self.display_movies(self.movie_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


    def search_movies(self):
        """Search movies based on title or notes."""
        search_term = self.search_entry.get().lower()  # Get the text input from the search field
        current_user = self.controller.current_user
        user_file = os.path.join(USER_DATA_FOLDER, f"{current_user}.json")

        if not os.path.exists(user_file):
            print(f"File not found: {user_file}")
            return

        try:
            with open(user_file, "r") as file:
                raw_data = file.read()
                user_data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        # filtered_movies = [movie for movie in user_data if search_term in movie.get("title", "").lower() or search_term in movie.get("notes", "").lower()]
        filtered_movies = [movie for movie in user_data if 
            search_term in movie.get("title", "").lower() or
            search_term in movie.get("notes", "").lower() or
            search_term in movie.get("status", "").lower() or
            search_term in str(movie.get("rating", "")).lower() or
            search_term in movie.get("type", "").lower() or
            any(search_term in genre.get("name", "").lower() for genre in movie.get("genres", []))
        ]
        
        self.display_movies(filtered_movies)

    def filter_movies(self, selected_status):
        """Filter movies based on selected status."""
        filter_criteria = selected_status  # The selected status from the dropdown
        current_user = self.controller.current_user
        user_file = os.path.join(USER_DATA_FOLDER, f"{current_user}.json")

        if not os.path.exists(user_file):
            print(f"File not found: {user_file}")
            return

        try:
            with open(user_file, "r") as file:
                raw_data = file.read()
                user_data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        # If "All" is selected, don't filter
        if filter_criteria == "All":
            self.display_movies(user_data)
        else:
            filtered_movies = [movie for movie in user_data if movie.get("status") == filter_criteria]
            self.display_movies(filtered_movies)

    def refresh_movies(self):
        print("Refreshing movies...")
        self.load_saved_movies()


    def show_add_movie_form(self):
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Add Custom Movie")
        self.form_window.geometry("400x750")

        # Title
        ctk.CTkLabel(self.form_window, text="Title:").pack(pady=5)
        self.title_entry = ctk.CTkEntry(self.form_window,corner_radius=20, width=300)
        self.title_entry.pack()

        self.form_window.attributes('-alpha', 0.95)

        # Type Selection
        ctk.CTkLabel(self.form_window, text="Type:").pack(pady=5)
        self.type_var = ctk.StringVar(value="movie")
        type_frame = ctk.CTkFrame(self.form_window, fg_color="transparent")
        type_frame.pack(pady=5)
        
        movie_radio = ctk.CTkRadioButton(
            type_frame, 
            text="Movie",
            fg_color="#FFD700", 
            variable=self.type_var,
            value="movie"
        )
        series_radio = ctk.CTkRadioButton(
            type_frame,
            text="Series",
            fg_color="#FFD700", 
            variable=self.type_var,
            value="series"
        )
        movie_radio.pack(side="left", padx=10)
        series_radio.pack(side="left", padx=10)

        # Rating
        ctk.CTkLabel(self.form_window, text="Rating (1-5):").pack(pady=5)
        self.rating_var = ctk.IntVar(value=1)
        rating_slider = ctk.CTkSlider(
            self.form_window,
            from_=1,
            to=5,
            number_of_steps=4,
            button_color="#FFD700",
            # progress_color="blue", 
            variable=self.rating_var
        )
        rating_slider.pack(pady=5)
        
        # Rating display label
        self.rating_label = ctk.CTkLabel(self.form_window, text="1")
        self.rating_label.pack()
        
        # Update rating label when slider moves
        def update_rating_label(*args):
            self.rating_label.configure(text=str(self.rating_var.get()))
        self.rating_var.trace_add("write", update_rating_label)

        # Genre
        ctk.CTkLabel(self.form_window, text="Genre:").pack(pady=5)
        self.genre_entry = ctk.CTkEntry(self.form_window, corner_radius=20, width=300)
        self.genre_entry.pack()
        ctk.CTkLabel(
            self.form_window,
            text="(Separate multiple genres with commas)",
            text_color="gray",
            font=("Arial", 10)
        ).pack()

        # Status
        ctk.CTkLabel(self.form_window, text="Status:").pack(pady=5)
        self.status_var = ctk.StringVar(value="To Watch")
        status_dropdown = ctk.CTkOptionMenu(
            self.form_window,
            variable=self.status_var,
            corner_radius=20,
            values=["Watched", "To Watch", "Not Watched"],
            fg_color="#FFD700",  
            button_color="#FFBF00",
            text_color="black"
        )
        status_dropdown.pack(pady=5)

        # User Notes
        ctk.CTkLabel(self.form_window, text="Notes:").pack(pady=5)
        self.notes_text = ctk.CTkTextbox(self.form_window,corner_radius=20, width=300, height=100)
        self.notes_text.pack()

        # Image Upload
        ctk.CTkLabel(self.form_window, text="Movie Poster:").pack(pady=5)
        self.upload_btn = ctk.CTkButton(
            self.form_window,
            text="Choose Image",
            corner_radius=20,
            fg_color="#FFD700",
            text_color="black",
            command=self.choose_image
        )
        self.upload_btn.pack(pady=5)
        
        # Image preview label
        self.image_label = ctk.CTkLabel(self.form_window, text="No image selected")
        self.image_label.pack(pady=5)

        # Submit Button
        submit_btn = ctk.CTkButton(
            self.form_window,
            text="Submit",
            command=self.submit_custom_movie,
            fg_color="#28a745",
            corner_radius=20,
            hover_color="#218838"
        )
        submit_btn.pack(pady=20)

        self.selected_image_path = None

    def submit_custom_movie(self):
        if not self.title_entry.get():
            CTkMessagebox(title="Error", message="Title is required!", icon="warning")
            return

        # Save image if selected
        image_path = None
        if self.selected_image_path:
            filename = f"{self.controller.current_user}_{int(time.time())}_{os.path.basename(self.selected_image_path)}"
            destination = os.path.join(IMAGES_FOLDER, filename)
            shutil.copy2(self.selected_image_path, destination)
            image_path = destination

        # Create custom movie data
        custom_movie = {
            "movie_id": -1,  # Unique negative ID for custom movies
            "status": self.status_var.get(),
            "rating": self.rating_var.get(),
            "notes": self.notes_text.get("1.0", "end-1c"),
            "title": self.title_entry.get(),
            "type": self.type_var.get(),
            "genres": [{"name": genre.strip()} for genre in self.genre_entry.get().split(",")],
            "poster_path": image_path,
        }

        # Save to user's JSON file
        user_file = os.path.join(USER_DATA_FOLDER, f"{self.controller.current_user}.json")
        try:
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    movies = json.load(f)
            else:
                movies = []
            
            movies.append(custom_movie)
            
            with open(user_file, "w") as f:
                json.dump(movies, f, indent=4)

            CTkMessagebox(title="Success", message="Movie added successfully!", icon="check")
            self.form_window.destroy()
            self.refresh_movies()

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to save movie: {str(e)}", icon="error")


    

    def choose_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.image_label.configure(text=os.path.basename(file_path))
