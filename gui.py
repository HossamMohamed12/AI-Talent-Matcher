"""
AI Talent Matcher GUI Module

Contains all GUI components and interface logic
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path
import threading
import json
import sys
import os


SETTINGS_FILE = "_internal\\settings.json"


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_settings():
    """Load settings from JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    """Save settings to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save settings: {e}")


class AITalentMatcher(ctk.CTk):
    def __init__(self, on_evaluate_callback=None, on_download_callback=None):
        super().__init__()

        # Callbacks for main app
        self.on_evaluate_callback = on_evaluate_callback
        self.on_download_callback = on_download_callback

        # Settings
        self.settings = load_settings()
        self.api_key = self.settings.get("deepseek_api_key", "")

        # Store uploaded files
        self.job_description_file = None
        self.resume_files = []
        self.candidate_info_files = []
        self.latest_report_file = None

        # Window configuration - nicer default
        self.title("AI Talent Matcher")
        # Set the size first
        window_width = 1150
        window_height = 820
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(1000, 700)
        self.configure(bg="#f0f2f5")

        # NOW center the window on screen using the explicit dimensions
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.winfo_screenheight() // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Color scheme - Using exact client-specified blue
        self.bg_color = "#f5f5f5"
        self.sidebar_color = "#e8e8e8"
        self.primary_blue = "#000435"  # Exact blue from client
        self.secondary_blue = "#E3F2FD"

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create main content
        self.create_main_content()

    def create_sidebar(self):
        """Create left sidebar with logo and new search button"""
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.sidebar_color)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Logo section
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", corner_radius=0)
        logo_frame.pack(fill="x", padx=10, pady=20)

        # Load and display logo
        try:
            logo_image = Image.open(resource_path("logo.png"))
            if logo_image.mode != "RGBA":
                logo_image = logo_image.convert("RGBA")
            logo_image = logo_image.resize((180, 135), Image.Resampling.LANCZOS)
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(180, 135)
            )
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_ctk,
                text="",
                fg_color="transparent"
            )
            logo_label.pack(pady=10)

            # FUSION text - using client's blue
            fusion_label = ctk.CTkLabel(
                logo_frame,
                text="FUSION",
                font=("Arial Bold", 28),
                text_color=self.primary_blue,
                fg_color="transparent"
            )
            fusion_label.pack(pady=(5, 10))
        except Exception as e:
            print(f"Logo not found: {e}")

        # New Search button
        new_search_btn = ctk.CTkButton(
            sidebar,
            text="New Search +",
            fg_color="#d0d0d0",
            text_color="#333",
            hover_color="#c0c0c0",
            height=40,
            corner_radius=8,
            command=self.new_search
        )
        new_search_btn.pack(padx=15, pady=20, fill="x")

        # Settings icon at bottom left
        settings_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        settings_frame.pack(side="bottom", padx=5, pady=20, anchor="w")

        try:
            # Load settings icon from PNG
            settings_icon = Image.open(resource_path("settings_icon.png"))
            if settings_icon.mode != "RGBA":
                settings_icon = settings_icon.convert("RGBA")
            settings_icon = settings_icon.resize((24, 24), Image.Resampling.LANCZOS)
            settings_ctk = ctk.CTkImage(
                light_image=settings_icon,
                dark_image=settings_icon,
                size=(24, 24)
            )
            settings_btn = ctk.CTkButton(
                settings_frame,
                image=settings_ctk,
                text="Settings",
                width=160,
                height=40,
                fg_color="transparent",
                text_color="#666",
                hover_color="#d0d0d0",
                font=("Arial", 13),
                compound="left",
                anchor="w",
                command=self.open_settings
            )
            settings_btn.pack(padx=5)
        except Exception as e:
            print(f"Settings icon error: {e}")
            # Fallback text button
            settings_btn = ctk.CTkButton(
                settings_frame,
                text="⚙ Settings",
                width=160,
                height=40,
                fg_color="transparent",
                text_color="#666",
                hover_color="#d0d0d0",
                font=("Arial", 13),
                anchor="w",
                command=self.open_settings
            )
            settings_btn.pack(padx=5)

    def create_main_content(self):
        """Create main content area with form fields"""
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Content container with padding
        content = ctk.CTkFrame(main_frame, fg_color="white")
        content.pack(fill="both", expand=True, padx=50, pady=30)

        # Title - using client's dark blue
        title = ctk.CTkLabel(
            content,
            text="Multi-Dimensional Evaluation Framework",
            font=("Arial Bold", 32),
            text_color=self.primary_blue
        )
        title.pack(anchor="w", pady=(0, 30))

        # Row 1: Industry and Location
        row1 = ctk.CTkFrame(content, fg_color="white")
        row1.pack(fill="x", pady=(0, 15))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        # Client Industry Designation
        industry_label = ctk.CTkLabel(
            row1,
            text="Client Industry Designation",
            font=("Arial", 12),
            text_color="#333",
            anchor="w"
        )
        industry_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.industry_entry = ctk.CTkEntry(
            row1,
            height=40,
            corner_radius=8,
            border_color="#ccc",
            border_width=1
        )
        self.industry_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Service Region
        location_label = ctk.CTkLabel(
            row1,
            text="Service Region",
            font=("Arial", 12),
            text_color="#333",
            anchor="w"
        )
        location_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.location_entry = ctk.CTkEntry(
            row1,
            height=40,
            corner_radius=8,
            border_color="#ccc",
            border_width=1
        )
        self.location_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        # Role Title
        job_label = ctk.CTkLabel(
            content,
            text="Role Title",
            font=("Arial", 12),
            text_color="#333",
            anchor="w"
        )
        job_label.pack(anchor="w", pady=(10, 5))

        self.job_entry = ctk.CTkEntry(
            content,
            height=40,
            corner_radius=8,
            border_color="#ccc",
            border_width=1
        )
        self.job_entry.pack(fill="x", pady=(0, 15))

        # Upload zones
        self.job_desc_label = self.create_upload_zone(
            content,
            "Job Description",
            "job_desc"
        )
        self.resumes_label = self.create_upload_zone(
            content,
            "Add Candidates' Resumes",
            "resumes"
        )
        self.candidate_info_label = self.create_upload_zone(
            content,
            "Add Additional Candidates' Information",
            "candidate_info"
        )

        # Buttons row
        button_frame = ctk.CTkFrame(content, fg_color="white")
        button_frame.pack(fill="x", pady=(20, 0))

        # Proceed button
        self.get_started_btn = ctk.CTkButton(
            button_frame,
            text="Proceed",
            fg_color=self.primary_blue,
            hover_color="#000226",
            height=40,
            corner_radius=20,
            font=("Arial", 12),
            command=self.get_started
        )
        self.get_started_btn.pack(side="left", padx=(0, 10))

        # Download Report button
        self.download_btn = ctk.CTkButton(
            button_frame,
            text="Download Report",
            fg_color="white",
            hover_color="#f0f0f0",
            text_color=self.primary_blue,
            border_color=self.primary_blue,
            border_width=2,
            height=40,
            corner_radius=20,
            font=("Arial", 12),
            command=self.download_report,
            state="disabled"
        )
        self.download_btn.pack(side="left", padx=10)

    def create_upload_zone(self, parent, label_text, zone_id):
        """Create a drag-and-drop upload zone with cloud icon"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Arial", 12),
            text_color="#333",
            anchor="w"
        )
        label.pack(anchor="w", pady=(10, 5))

        # Upload zone frame
        upload_frame = ctk.CTkFrame(
            parent,
            height=85,
            corner_radius=8,
            border_color="#9DC1E8",
            border_width=2,
            fg_color=self.secondary_blue
        )
        upload_frame.pack(fill="x", pady=(0, 10))
        upload_frame.pack_propagate(False)

        # Cloud upload icon
        try:
            cloud_icon = Image.open(resource_path("cloud_upload_icon.png"))
            if cloud_icon.mode != "RGBA":
                cloud_icon = cloud_icon.convert("RGBA")
            cloud_icon = cloud_icon.resize((50, 40), Image.Resampling.LANCZOS)
            cloud_ctk = ctk.CTkImage(
                light_image=cloud_icon,
                dark_image=cloud_icon,
                size=(50, 40)
            )
            icon_label = ctk.CTkLabel(
                upload_frame,
                image=cloud_ctk,
                text=""
            )
            icon_label.pack(pady=(12, 2))
        except Exception as e:
            print(f"Cloud icon error: {e}")
            # Fallback to text if icon loading fails
            icon_label = ctk.CTkLabel(
                upload_frame,
                text="☁↑",
                font=("Arial", 24),
                text_color="#666"
            )
            icon_label.pack(pady=(10, 0))

        # Upload text
        text_label = ctk.CTkLabel(
            upload_frame,
            text="Upload",
            font=("Arial", 11),
            text_color="#666"
        )
        text_label.pack()

        # Make it clickable
        upload_frame.bind("<Button-1>", lambda e: self.browse_file(zone_id, text_label))
        icon_label.bind("<Button-1>", lambda e: self.browse_file(zone_id, text_label))
        text_label.bind("<Button-1>", lambda e: self.browse_file(zone_id, text_label))

        return text_label

    def browse_file(self, zone_id, label_widget):
        """Open file browser"""
        if zone_id == "resumes":
            filenames = filedialog.askopenfilenames(
                title="Select Resume PDFs",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filenames:
                self.resume_files = list(filenames)
                label_widget.configure(text=f"{len(filenames)} file(s) selected")
        elif zone_id == "job_desc":
            filename = filedialog.askopenfilename(
                title="Select Job Description",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ]
            )
            if filename:
                self.job_description_file = filename
                label_widget.configure(text=Path(filename).name)
        elif zone_id == "candidate_info":
            filenames = filedialog.askopenfilenames(
                title="Select Additional Files",
                filetypes=[("All files", "*.*")]
            )
            if filenames:
                self.candidate_info_files = list(filenames)
                label_widget.configure(text=f"{len(filenames)} file(s) selected")

    # ========= SETTINGS WINDOW (API KEY) =========

    def open_settings(self):
        """Open settings window with API key field."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("420x220")
        settings_window.resizable(True, True)

        # Center on parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 210
        y = self.winfo_y() + (self.winfo_height() // 2) - 110
        settings_window.geometry(f"420x220+{x}+{y}")

        settings_window.grab_set()

        container = ctk.CTkFrame(settings_window, fg_color="transparent", corner_radius=10)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        api_label = ctk.CTkLabel(
            container,
            text="API Key",
            font=("Arial", 12),
            text_color="#333",
            anchor="w"
        )
        api_label.pack(anchor="w", pady=(5, 5))

        api_entry = ctk.CTkEntry(
            container,
            height=36,
            corner_radius=8,
            border_color="#ccc",
            border_width=1,
            show="*"
        )
        api_entry.pack(fill="x")

        # Pre-fill with existing key (if any)
        if self.api_key:
            api_entry.insert(0, self.api_key)

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        def save_and_close():
            new_key = api_entry.get().strip()
            if not new_key:
                if not messagebox.askyesno(
                    "Empty API Key",
                    "API key field is empty. Continue and clear the saved key?"
                ):
                    return
            self.api_key = new_key
            self.settings["deepseek_api_key"] = new_key
            save_settings(self.settings)
            messagebox.showinfo("Saved", "API key saved successfully.")
            settings_window.destroy()

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color=self.primary_blue,
            hover_color="#000226",
            height=36,
            corner_radius=18,
            command=save_and_close,
        )
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            text_color="#333",
            height=36,
            corner_radius=18,
            command=settings_window.destroy,
        )
        cancel_btn.pack(side="right")

    # ========= REST OF LOGIC =========

    def new_search(self):
        """Clear all fields for new search"""
        self.industry_entry.delete(0, "end")
        self.location_entry.delete(0, "end")
        self.job_entry.delete(0, "end")
        self.job_description_file = None
        self.resume_files = []
        self.candidate_info_files = []
        self.latest_report_file = None

        # Reset labels
        self.job_desc_label.configure(text="Upload")
        self.resumes_label.configure(text="Upload")
        self.candidate_info_label.configure(text="Upload")

        # Disable download button
        self.download_btn.configure(state="disabled")
        print("New search initiated")

    def get_started(self):
        """Handle Proceed button - triggers evaluation"""
        # Validate inputs
        if not self.api_key:
            messagebox.showerror(
                "API Key Required",
                "Please set your DeepSeek API key in Settings before proceeding."
            )
            return

        if not self.job_entry.get():
            messagebox.showerror("Error", "Please enter a role title")
            return
        if not self.resume_files:
            messagebox.showerror("Error", "Please upload at least one resume")
            return

        # Disable button during processing
        self.get_started_btn.configure(state="disabled", text="Processing...")

        # Call the evaluation callback
        if self.on_evaluate_callback:
            # Run in daemon thread to prevent GUI freezing
            thread = threading.Thread(target=self._run_evaluation, daemon=True)
            thread.start()

    def _run_evaluation(self):
        """Run evaluation in background thread"""
        try:
            # Get form data
            form_data = {
                "job_title": self.job_entry.get(),
                "company": self.industry_entry.get() or "Company",
                "location": self.location_entry.get() or "",
                "department": "Department",
                "resume_files": self.resume_files,
                "job_description_file": self.job_description_file,
                "api_key": self.api_key,
            }

            # Call callback
            report_file = self.on_evaluate_callback(form_data)

            # Update UI in main thread
            self.after(0, self._evaluation_complete, report_file)
        except Exception as e:
            self.after(0, self._evaluation_error, str(e))

    def _evaluation_complete(self, report_file):
        """Called when evaluation is complete"""
        self.latest_report_file = report_file
        self.get_started_btn.configure(state="normal", text="Proceed")
        self.download_btn.configure(state="normal")
        messagebox.showinfo(
            "Success",
            "CV evaluation complete!\n\nPDF Report generated successfully.\n\nClick 'Download Report' to save."
        )

    def _evaluation_error(self, error_msg):
        """Called when evaluation fails"""
        self.get_started_btn.configure(state="normal", text="Proceed")
        messagebox.showerror("Error", f"Evaluation failed: {error_msg}")

    def download_report(self):
        """Handle Download Report button"""
        if self.on_download_callback and self.latest_report_file:
            self.on_download_callback(self.latest_report_file)
        else:
            messagebox.showwarning("Warning", "No report available to download")
