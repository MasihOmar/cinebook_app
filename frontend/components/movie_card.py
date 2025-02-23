import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import requests
import json
import io
import os
from tkinter import StringVar, IntVar
from pytablericons import TablerIcons, OutlineIcon
from backend.api_handler import APIHandler

IMAGES_FOLDER = "backend/database/movie_images"

class MovieContainer(ctk.CTkFrame):
    def __init__(self, parent, movie_id, username=None, initial_status="To Watch", initial_rating=0, initial_notes="", show_buttons=None, controller=None, custom_data=None):
        super().__init__(parent, fg_color="#1E1E1E", corner_radius=10, width=200, height=380)

         # Force the widget to maintain its size
        self.grid_propagate(False)
        self.pack_propagate(False)

        
        self.movie_id = movie_id
        self.username = username
        self.status_var = StringVar(value=initial_status)
        self.rating_var = IntVar(value=initial_rating)
        self.notes_var = StringVar(value=initial_notes)
        self.show_buttons = show_buttons or []  # Default to an empty list if None is passed
        self.movie_data = None
        self.controller = controller
        self.custom_data = custom_data
        self.liked_var = IntVar(value=0) 
        if custom_data:
            self.custom_movie_title= custom_data.get("title", "")

        self.fetch_and_display_movie()

        rating_frame = ctk.CTkFrame(self, fg_color="transparent")
        rating_frame.pack(fill="x", padx=10)

     
        # Add star rating display
        if "update" in self.show_buttons:
            self.create_star_rating(rating_frame)
            



        # Flag to track if the dropdown window is already open
        self.dropdown_window = None
        self.details_dropdown_window = None 

       


    def fetch_and_display_movie(self):
        if self.custom_data:  # Just check for custom_data
            self.movie_data = self.custom_data
            self.display_custom_movie()
            return
            
        self.fetch_movie_data()
        if self.movie_data:
            self.display_tmdb_movie()

    def display_custom_movie(self):
        # Display custom movie poster (if provided) or placeholder
        if not self.custom_data:
            print("No custom data available")
            return
        

        poster_path = self.custom_data.get("poster_path", "") 
        full_poster_path = None # Initialize to a default value


        if poster_path:
            full_poster_path = os.path.join(IMAGES_FOLDER, os.path.basename(poster_path))
        
        if full_poster_path and  os.path.exists(full_poster_path):
            self.add_movie_image(full_poster_path)
        else:
            self.add_placeholder_image()

        # Display movie title and year
        title = self.custom_data.get("title", "Unknown Title")
        # release_date = self.custom_data.get("release_date", "Unknown")
        self.title_label = ctk.CTkLabel(
            self, 
            text=f"{title}",
            text_color="white",
            wraplength=200,
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(pady=(5, 5))

        
        

        self.create_details_menu()
        self.create_dropdown_menu()


    def display_tmdb_movie(self):
        self.add_movie_image(self.movie_data.get("poster_path"))

        title = self.movie_data.get("title", "Unknown Title")
        self.title_label = ctk.CTkLabel(
            self,
            text=f"{title}",
            text_color="white",
            wraplength=200,
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(pady=(5, 5))

        self.create_details_menu()
        self.create_dropdown_menu()


    def add_placeholder_image(self):
        placeholder = ctk.CTkFrame(self, width=180, height=270, fg_color="#2E2E2E")
        placeholder.pack(pady=(10, 5))
        placeholder_text = ctk.CTkLabel(
            placeholder,
            text="No Image\nAvailable",
            text_color="white",
            font=("Arial", 12)
        )
        placeholder_text.place(relx=0.5, rely=0.5, anchor="center")


    def fetch_movie_data(self):
        """Fetch movie details using the updated APIHandler."""
        self.movie_data = APIHandler.fetch_movie_details(self.movie_id)
        if not self.movie_data:
            print(f"Failed to fetch data for movie ID {self.movie_id}.")


    def add_movie_image(self, poster_path):
        """Load and display the movie poster."""
        try:
            if poster_path.startswith("/"):
                # Remote URL
                image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = response.content
            else:
                # Local file
                print(poster_path)
                if not os.path.exists(poster_path):
                    print(f"Local file not found: {poster_path}")
                    self.add_placeholder_image()
                    return
                with open(poster_path, "rb") as file:
                    image_data = file.read()

            # Process and display the image
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((180, 270), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label = ctk.CTkLabel(self, image=photo, text="")
            self.image_label.image = photo
            self.image_label.pack(pady=(10, 5))
        except Exception as e:
            print(f"Error loading image: {e}")
            self.add_placeholder_image()


    def create_details_menu(self):
        """Create a button to display a dropdown menu for details."""
        details_icon = TablerIcons.load(OutlineIcon.INFO_CIRCLE, size=24, color="#FFD700", stroke_width=2.0)
        details_icon_image = ImageTk.PhotoImage(details_icon)

        details_button = ctk.CTkButton(
            self, text="", image=details_icon_image, width=40, fg_color="#2E2E2E",
            command=self.show_details_dropdown
        )
        details_button.image = details_icon_image
        details_button.pack(side="left", padx=(5, 5), pady=(5,5))  # Side by side, with some horizontal padding


    def show_details_dropdown(self):
        """Display comprehensive dropdown menu for movie/TV show details."""
        if self.details_dropdown_window and self.details_dropdown_window.winfo_exists():
            self.details_dropdown_window.lift()
            return

        self.details_dropdown_window = ctk.CTkToplevel(self)
        self.details_dropdown_window.geometry("400x400")
        self.details_dropdown_window.title("Movie Details")
        self.details_dropdown_window.transient(self)
        self.details_dropdown_window.attributes('-alpha', 0.95)

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            master=self.details_dropdown_window,
            width=380,
            height=580
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Content frame inside scrollable frame
        content_frame = ctk.CTkFrame(master=scroll_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Determine media type and specific details
        is_tv = self.movie_data.get("genre") == "tv"
        title = self.movie_data.get("name" if is_tv else "title", "Unknown")
        date = self.movie_data.get("first_air_date" if is_tv else "release_date", "Unknown")
        duration = (f"{self.movie_data.get('number_of_seasons', '?')} Seasons, "
                f"{self.movie_data.get('number_of_episodes', '?')} Episodes") if is_tv else \
                f"{self.movie_data.get('runtime', '?')} minutes"

        # Collect all details
        details = {
            "Title": title,
            # "Type": "TV Show" if is_tv else "Movie",
            "Release Date": date,
            "Duration": duration,
            "Status": self.movie_data.get("status", "Unknown"),
            "Rating": f"{self.movie_data.get('vote_average', '?')}/10 ({self.movie_data.get('vote_count', 0)} votes)",
            "Popularity": f"{self.movie_data.get('popularity', '?')} points",
            "Genres": ', '.join(g['name'] for g in self.movie_data.get("genres", [])),
            "Language": self.movie_data.get("original_language", "Unknown").upper(),
            "Overview": self.movie_data.get("overview", "No description available."),
            "Production": ', '.join(c['name'] for c in self.movie_data.get("production_companies", [])),
            "Countries": ', '.join(c['name'] for c in self.movie_data.get("production_countries", [])),
            "Budget": f"${self.movie_data.get('budget', 0):,}" if self.movie_data.get('budget') else "N/A",
            "Revenue": f"${self.movie_data.get('revenue', 0):,}" if self.movie_data.get('revenue') else "N/A"
        }

        # Add cast if available
        if credits := self.movie_data.get("credits", {}):
            if cast := credits.get("cast", []):
                details["Cast"] = ', '.join(
                    f"{actor['name']} as {actor.get('character', 'Unknown')}"
                    for actor in cast[:5]
                )

        # Add streaming providers if available
        if providers := self.movie_data.get("watch/providers", {}).get("results", {}).get("US", {}):
            for provider_type in ["flatrate", "free", "ads", "rent", "buy"]:
                if provider_list := providers.get(provider_type):
                    details[f"Available to {provider_type.title()}"] = ', '.join(
                        p['provider_name'] for p in provider_list
                    )

        # Display all details
        for label, value in details.items():
            section_frame = ctk.CTkFrame(content_frame)
            section_frame.pack(fill="x", padx=5, pady=3)

            header = ctk.CTkLabel(
                section_frame,
                text=f"{label}:",
                font=("Arial", 12, "bold"),
                text_color="lightgray"
            )
            header.pack(anchor="w", padx=8, pady=(5, 0))

            content = ctk.CTkLabel(
                section_frame,
                text=str(value),
                font=("Arial", 11),
                wraplength=340,
                justify="left",
                text_color="lightgray"
            )
            content.pack(anchor="w", padx=8, pady=(0, 1))

    def create_dropdown_menu(self):
        """Create a dropdown menu for actions like rating, status, and notes."""
        icon_dots = TablerIcons.load(OutlineIcon.DOTS, size=24, color="#FFD700", stroke_width=2.0)
        icon_dots_image = ImageTk.PhotoImage(icon_dots)

        dropdown_button = ctk.CTkButton(
            self, text="", image=icon_dots_image, width=40, fg_color="#2E2E2E",
            command=self.open_actions_dropdown
        )
        dropdown_button.image = icon_dots_image
        dropdown_button.pack(side="right", padx=(5, 5), pady=(5,5))  # Side by side, with some horizontal padding



    def create_star_rating(self, parent):
        """Create and display the star rating."""
        rating_label = ctk.CTkLabel(
            parent,
            text="★" * self.rating_var.get() + "☆" * (5 - self.rating_var.get()),
            text_color="#FFD700",  # Gold color for stars
            font=("Arial", 16)
        )
        rating_label.pack(side="left", pady=5)

        # Update star display when rating changes
        def update_stars(*args):
            rating_label.configure(
                text="★" * self.rating_var.get() + "☆" * (5 - self.rating_var.get())
            )
        
        self.rating_var.trace_add("write", update_stars)


    def open_actions_dropdown(self):
        """Display dropdown menu for actions only if it's not already open."""
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.dropdown_window.lift()
            return

        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.geometry("250x520")
        self.dropdown_window.title("Actions")
        self.dropdown_window.transient(self)
        self.dropdown_window.attributes('-alpha', 0.95)

        # Add title editing for custom data
        if self.custom_data:
            title_label = ctk.CTkLabel(self.dropdown_window, text="Title:", text_color="white")
            title_label.pack(pady=(10, 5))
            
            title_entry = ctk.CTkEntry(self.dropdown_window, corner_radius=20)
            title_entry.insert(0, self.custom_data.get("title", ""))
            title_entry.pack(pady=(2, 10), padx=10)
            
            def update_title():
                new_title = title_entry.get()
                self.custom_data["title"] = new_title
                self.title_label.configure(text=new_title)

                print("Title updated:", new_title)
                
            title_entry.bind("<FocusOut>", lambda _: update_title())
            title_entry.bind("<KeyRelease>", lambda _: update_title())

        # Rating slider
        ctk.CTkLabel(self.dropdown_window, text="Rating (1-5):").pack(pady=5)
        rating_slider = ctk.CTkSlider(
            self.dropdown_window,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.rating_var,
            button_color="#FFD700",
            corner_radius=20,
        )
        rating_slider.pack(pady=(5, 10), padx=10)

        # Rating display label
        self.rating_label = ctk.CTkLabel(self.dropdown_window, text="1")
        self.rating_label.pack()
        
        def update_rating_label(*args):
            self.rating_label.configure(text=str(self.rating_var.get()))
        self.rating_var.trace_add("write", update_rating_label)

        # Watch status
        status_label = ctk.CTkLabel(self.dropdown_window, text="Status:", text_color="white")
        status_label.pack(pady=(10, 5))

        self.status_dropdown = ctk.CTkOptionMenu(
            self.dropdown_window,
            variable=self.status_var,
            values=["Watched", "Not Watched", "Pending"],
            fg_color="#FFD700",  
            button_color="#FFBF00",
            text_color="black",
            corner_radius=20,
            command=self.on_status_change
        )
        self.status_dropdown.pack(pady=(2, 2), padx=10)

        # Notes
        notes_label = ctk.CTkLabel(self.dropdown_window, text="Notes:", text_color="white")
        notes_label.pack(pady=(10, 5))

        notes_entry = ctk.CTkTextbox(self.dropdown_window, corner_radius=20, scrollbar_button_color="#FFD700")
        notes_entry.insert("1.0", self.notes_var.get())
        notes_entry.pack(pady=(5, 10), padx=10)

        def update_notes_var():
            self.notes_var.set(notes_entry.get("1.0", "end-1c").strip())

        notes_entry.bind("<FocusOut>", lambda _: update_notes_var())
        notes_entry.bind("<KeyRelease>", lambda _: update_notes_var())

        # Conditional Buttons
        if "save" in self.show_buttons:
            save_button = ctk.CTkButton(
                self.dropdown_window, text="Save", command=self.save_data, corner_radius=20,
                fg_color="#28a745", hover_color="#218838", text_color="white"
            )
            save_button.pack(pady=(10, 5))

        if "update" in self.show_buttons:
            update_button = ctk.CTkButton(
                self.dropdown_window, text="Update", command=self.update_data,
                fg_color="#FFA500", hover_color="#FF8C00", text_color="white", corner_radius=20
            )
            update_button.pack(pady=(10, 5))

        if "delete" in self.show_buttons:
            delete_button = ctk.CTkButton(
                self.dropdown_window, text="Delete Movie", command=self.delete_movie_data,
                fg_color="#FF6347", hover_color="#FF4500", text_color="white", corner_radius=20
            )
            delete_button.pack(pady=(10, 5))

        


    def save_data(self):
        """Save the movie data to the JSON file and show a confirmation message."""
        if not self.username:
            CTkMessagebox(
                title="Error",
                    message="No username provided!",
                    icon="error",
                    option_1="Close"
            )
            return

        # Ensure directory exists
        user_data_dir = os.path.join("backend/database/user_movie_data")
        os.makedirs(user_data_dir, exist_ok=True)
            
        user_file = os.path.join(user_data_dir, f"{self.username}.json")

        try:
                # Load current data
                user_data = []
                if os.path.exists(user_file):
                    with open(user_file, "r") as file:
                        try:
                            user_data = json.load(file)
                            if not isinstance(user_data, list):
                                user_data = []
                        except json.JSONDecodeError:
                            print(f"Error reading JSON file: {user_file}")
                            user_data = []

                # Update or add movie data
                movie_data = {
                    "movie_id": self.movie_id,
                    "status": self.status_var.get(),
                    "rating": self.rating_var.get(),
                    "notes": self.notes_var.get(),
                }

                # Find and update existing movie or append new one
                updated = False
                for i, movie in enumerate(user_data):
                    if movie.get("movie_id") == self.movie_id:
                        user_data[i] = movie_data
                        updated = True
                        break

                if not updated:
                    user_data.append(movie_data)

                # Save updated data
                with open(user_file, "w") as file:
                    json.dump(user_data, file, indent=4)

                print(f"Data saved for movie {self.movie_id}")

                # Show the confirmation message
                CTkMessagebox(
                    title="Save Confirmation",
                    message="Movie data saved successfully!",
                    icon="check",
                    option_1="Close"
                )

                # Refresh the collection page if controller exists
                if hasattr(self, 'controller') and self.controller is not None:
                    if "MyCollectionsPage" in self.controller.frames:
                        self.controller.frames["MyCollectionsPage"].refresh_movies()
                    else:
                        print("MyCollectionsPage not found in controller frames")
                else:
                    print("Controller not properly initialized")

        except Exception as e:
                print(f"Failed to save data: {e}")
                CTkMessagebox(
                    title="Error",
                    message=f"Failed to save data: {str(e)}",
                    icon="error",
                    option_1="Close"
        )
    
    def delete_movie_data(self):
        """Show confirmation dialog before deleting movie data."""
        msg = CTkMessagebox(
            title="Delete Movie",
            message="Are you sure you want to delete this movie?",
            icon="warning",
            option_1="Delete",
            option_2="Cancel"
        )

        if msg.get() == "Delete":
            user_file = os.path.join("backend/database/user_movie_data", f"{self.username}.json")
            
            try:
                with open(user_file, "r") as file:
                    user_data = json.load(file)
                
                # For custom movies (movie_id == -1), check by title
                if self.movie_id == -1:
                    user_data = [movie for movie in user_data 
                            if not (movie.get("movie_id") == -1 and 
                                    movie.get("title") == self.movie_data.get("title"))]
                else:
                    # For regular movies, check by movie_id
                    user_data = [movie for movie in user_data 
                            if movie.get("movie_id") != self.movie_id]
                
                # Save the updated data
                with open(user_file, "w") as file:
                    json.dump(user_data, file, indent=4)
                
              
                
                self.controller.frames["MyCollectionsPage"].refresh_movies()

                success_msg = CTkMessagebox(
                    title="Deleted",
                    message="Movie data has been deleted successfully.",
                    icon="check"
                )
                success_msg.get()
            
            except Exception as e:
                error_msg = CTkMessagebox(
                    title="Error",
                    message=f"Failed to delete movie: {str(e)}",
                    icon="error"
                )
                error_msg.get()


    def update_data(self):
        """Update the movie data in the JSON file."""
        # Retrieve the latest values directly from the UI elements
        updated_status = self.status_var.get()
        updated_rating = self.rating_var.get()
        updated_notes = self.notes_var.get()
        updated_title = self.custom_data.get("title", "") if self.custom_data else None

        print(f"Updated Status: {updated_status}") 
        print(f"Updated Rating: {updated_rating}") 
        print(f"Updated Notes: {updated_notes}") 
        print(f"Updated Title: {updated_title}")

        user_file = os.path.join("backend/database/user_movie_data", f"{self.username}.json")

        # Load current data
        if os.path.exists(user_file):
            with open(user_file, "r") as file:
                try:
                    user_data = json.load(file)
                except json.JSONDecodeError:
                    user_data = []
        else:
            CTkMessagebox(title="Error", message="No data found to update!", icon="warning")
            return

        # Check if movie exists and update its data
        updated = False
        for movie in user_data:
             # For custom movies (movie_id == -1), check by title
            if self.movie_id == -1:
                if movie.get("movie_id") == -1 and movie.get("title") == self.custom_movie_title:
                    movie.update({
                        "status": updated_status,
                        "rating": updated_rating,
                        "notes": updated_notes,
                        "title": updated_title,
                    })
                    updated = True
                    break
            else:
                # For regular movies, check by movie_id
                if movie.get("movie_id") == self.movie_id:
                    movie.update({
                        "status": updated_status,
                        "rating": updated_rating,
                        "notes": updated_notes
                    })
                    updated = True
                    break


        if updated:
            # Save the updated data to the JSON file
            with open(user_file, "w") as file:
                json.dump(user_data, file, indent=4)
            
            # Refresh the collection page
            self.controller.frames["MyCollectionsPage"].refresh_movies()

            CTkMessagebox(title="Updated", message="Movie data updated successfully!", icon="check")
        else:
            CTkMessagebox(title="Error", message="Movie not found to update!", icon="warning")
        

    def on_status_change(self, selected_status):
        print(f"Selected status: {selected_status}")





