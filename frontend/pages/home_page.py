import customtkinter as ctk
from PIL import ImageTk
from backend.api_handler import APIHandler
from frontend.components.movie_card import MovieContainer
from pytablericons import TablerIcons, OutlineIcon


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller



        self.movie_data = []  # Cache for movie data
        self.resize_timer = None  # Timer for throttling resize events

        # Initialize APIHandler (no need to pass arguments anymore)
        self.api_handler = APIHandler

        self.left_line = ctk.CTkCanvas(self, width=1, bg="white", highlightthickness=0)
        self.left_line.pack(side="left", fill="y")
        self.left_line.create_line(0, 0, 1, 800, fill="black", width=1)

        # Top frame for search bar and buttons
        self.top_frame = ctk.CTkFrame(self, fg_color="black")
        self.top_frame.pack(pady=10, padx=10, anchor='n', fill='x')

        # Configure grid columns
        self.top_frame.grid_columnconfigure(0, weight=1)  # Left space
        self.top_frame.grid_columnconfigure(1, weight=0)  # Center (search)
        self.top_frame.grid_columnconfigure(2, weight=1)  # Right space

        # Create center frame for search
        center_frame = ctk.CTkFrame(self.top_frame, fg_color="black")
        center_frame.grid(row=0, column=1)

        # Search bar
        icon_search = TablerIcons.load(OutlineIcon.WORLD_SEARCH, size=24, color="#FFFFFF", stroke_width=2.0)
        icon_search_image = ImageTk.PhotoImage(icon_search)

        self.search_entry = ctk.CTkEntry(center_frame, corner_radius=20, placeholder_text="Search...", width=300)
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

        self.setup_media_tabs()

        # Container for movie posters
        self.movies_container_frame = ctk.CTkFrame(self, fg_color="black", border_color="black", border_width=1)
        self.movies_container_frame.pack(fill="both", expand=True, pady=20, padx=20)

        # Adding a canvas and scrollbar
        self.canvas = ctk.CTkCanvas(self.movies_container_frame, bg="black", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.movies_container_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="black")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Fetch and display top movies by default
        self.fetch_and_display_top_movies()

        # Bind resizing event with throttling
        self.bind("<Configure>", self.on_resize)



    def setup_media_tabs(self):
        """Create and configure the media type tabs using CTkTabview."""
        # Create the tabview
        self.media_tabs = ctk.CTkTabview(
            self.top_frame,
            width=200,
            height=40,
            # corner_radius=20,
            fg_color="transparent",
            segmented_button_fg_color="#2b2b2b",  # Dark background for tabs
            segmented_button_selected_color="#FFD700",  # Green for selected tab
            segmented_button_unselected_color="#2b2b2b",  # Dark for unselected tabs
            text_color="white"  # Text color for tabs
        )
        # self.media_tabs.grid(row=0, column=5, padx=5, pady= 15, sticky="w")
        self.media_tabs.grid(row=0, column=2, padx=5, pady=15, sticky="e")  # Changed to column 2 and sticky="e"


        # Add the tabs
        self.media_tabs.add("Movies")
        self.media_tabs.add("TV Series")

        # Configure tab change event
        def on_tab_change(event=None):
            current_tab = self.media_tabs.get()
            if current_tab == "Movies":
                self.show_movies()
            else:
                self.show_tv_series()

        # Bind the tab change event
        self.media_tabs.configure(command=on_tab_change)

        # Set default tab
        self.media_tabs.set("Movies")


    def fetch_and_display_top_movies(self):
        self.movie_data = self.api_handler.fetch_movies_by_query("movie")  # Fetch top movies
        self.display_movies(self.movie_data)

    def search_movies(self):
        search_query = self.search_entry.get()
        if search_query:  # Only perform search if query is not empty
            self.movie_data = self.api_handler.fetch_movies_by_query(search_query)  # Fetch search results
            self.display_movies(self.movie_data)

    def show_movies(self):
        self.movie_data = self.api_handler.fetch_movies_by_query("movie")  # Fetch top movies
        self.display_movies(self.movie_data)

    def show_tv_series(self):
        self.movie_data = self.api_handler.fetch_movies_by_query("series")  # Fetch TV series
        self.display_movies(self.movie_data)

    def display_movies(self, movies):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not movies:
            no_results_label = ctk.CTkLabel(self.scrollable_frame, text="No results found.", text_color="white")
            no_results_label.pack(pady=20)
            return

        row, col = 0, 0
        widgets_per_row = self.calculate_widgets_per_row()

        for movie in movies:
            if col == widgets_per_row:
                col = 0
                row += 1
            if movie.get('id') is not None:
            # Create MovieContainer for each movie instead of basic display
                movie_container = MovieContainer(self.scrollable_frame, movie_id=movie.get('id'), username=self.controller.current_user, show_buttons=["save"], controller=self.controller )
                movie_container.grid(row=row, column=col, padx=18, pady=20)

            col += 1

    def calculate_widgets_per_row(self):
        window_width = self.winfo_width()
        return max(1, window_width // 220)

    def on_resize(self, event=None):
        if self.resize_timer:
            self.after_cancel(self.resize_timer)  # Cancel previous timer

        self.resize_timer = self.after(300, self.update_layout)  # Delay layout update by 300ms

    def update_layout(self):
        if self.movie_data:  # Use cached movie data
            self.display_movies(self.movie_data)

