# ======== Clinical system app prototype. Version 1.2 ========

# A clinic system GUI built with tkinter and customtkinter, 
# using a backend auth.py module for user management and 
# notes.py for patient notes.


import tkinter as tk
from tkinter import messagebox, ttk
import auth
import notes
import theme
import patients
import prescriptions
import customtkinter as ctk
from datetime import datetime, date 
# --- Constants ------------------------------------------------------
STAFF_APPS = [
    {
        "label": "Patients",
        "description": "Search patients and manage their notes",
        "screen": "show_patient_list",
        "roles": ["Nurse", "Medical Officer", "Dr"],
    },
]

# --- Theme ----------------------------------------------------------
BG = CARD = FIELD = FG = MUTED = ACCENT = DANGER = ERROR = None
FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI Semibold", 18)

def _load_theme():
    global BG, CARD, FIELD, FG, MUTED, ACCENT, DANGER, ERROR
    t = theme.get()
    BG, CARD, FIELD = t["bg"], t["card"], t["field"]
    FG, MUTED, ACCENT = t["fg"], t["muted"], t["accent"]
    DANGER, ERROR = t["danger"], t["error"]

_load_theme()
ctk.set_appearance_mode(theme.get()["mode"])  # light/dark/auto

# --- Main application class ----------------------------------------
class ClinicApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clinic System")
        self.configure(bg=BG)
        self._center_window(460, 560)
 
        self.current_user = None
        self.current_role = None
        self._patient_window = None

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
 
        self.show_login()
 
    # --- small helpers ---------------------------------------------
    
    # Center the window on the screen.
    def _center_window(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    # Like center but returns the geometry string instead of applying it. Used for popups.
    def _center_geometry(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        return f"{w}x{h}+{x}+{y}"
    
    # Clear all widgets from the main container.
    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # Configure the window size and resizability, and center it. 
    def _configure_window(self, w, h, resizable=False):
        self.resizable(resizable, resizable)
        self._center_window(w, h)
 
    # Darken a hex colour a little — used for button hover states.
    def _shade(self, hex_color, factor=0.85):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = (int(c * factor) for c in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _format_medicare(self, digits):
        if len(digits) != 10:
            return digits              # fall back to raw if it's not the expected shape
        return f"{digits[0:4]} {digits[4:9]} {digits[9]}"
    
    def _format_dob(self, iso_date):
        try:
            d = date.fromisoformat(iso_date)
        except (ValueError, TypeError):
            return iso_date            # show whatever's there if it won't parse
        return f"{d.day} {d.strftime('%b')} {d.year}" 
    
    # --- widget builders ------------------------------------------
    
    # Build a button with the app's standard style. Returns the button widget.
    def _button(self, parent, text, command, bg=None, fg="#ffffff", width=22):
        if bg is None:
            bg = ACCENT
        
        return ctk.CTkButton(
            parent, text=text, command=command,
            fg_color=bg, text_color=fg, hover_color=self._shade(bg),
            corner_radius=8, width=width * 9, height=34,
            font=FONT, cursor="hand2",
        )
    
    # --- form fields and radio buttons --------------------------------
    
    # Build a labeled entry field. Returns the entry widget.
    def _field(self, parent, label, show=None):
        ctk.CTkLabel(parent, text=label, font=FONT, fg_color="transparent",
                     text_color=MUTED, anchor="w").pack(fill="x", pady=(8, 2), padx=24)
        entry = ctk.CTkEntry(parent, font=FONT, width=240,
                             fg_color=FIELD, text_color=FG,
                             border_width=0, corner_radius=6,
                             show=(show or ""))
        entry.pack(ipady=2, padx=28)
        return entry
    
    # Build a set of radio buttons for role selection. Returns the StringVar that holds the selected value.
    def _role_radios(self, parent, default):
        var = tk.StringVar(value=default)
        for role in auth.VALID_ROLES:
            tk.Radiobutton(parent, text=role, value=role, variable=var,
                           font=FONT, bg=CARD, fg=FG, selectcolor=FIELD,
                           activebackground=CARD, activeforeground=FG,
                           anchor="w").pack(fill="x")
        return var
    
    # --- treeview style -------------------------------------------

    # Ensure the treeview uses the app's standard style.
    def _ensure_tree_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Clinic.Treeview", background=CARD, fieldbackground=CARD,
                        foreground=FG, rowheight=26, borderwidth=0, font=FONT)
        style.configure("Clinic.Treeview.Heading", background=FIELD, foreground=FG,
                        borderwidth=0, font=("Segoe UI Semibold", 10))
        style.map("Clinic.Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", "#ffffff")])

    # --- note formatting -----------------------------------------

    # Format a note's signature for display.
    def _format_signature(self, note):
        dt = datetime.fromisoformat(note["created_at"])
        hour12 = dt.hour % 12 or 12
        ampm = "am" if dt.hour < 12 else "pm"
        when = f"{dt.day} {dt.strftime('%b')} {dt.year}, {hour12}:{dt.minute:02d}{ampm}"
        return f"— {note['author_name']}, {note['author_role']} · {when}"
     

    # --- login ------------------------------------------------------

    # Show the login screen.
    def show_login(self):
        
        self._clear()
        self._configure_window(460, 520)
        self._login_bg = tk.PhotoImage(file="assets/clinic_app_bg_2.png")
        bg_label = tk.Label(self.container, image=self._login_bg, borderwidth=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1) 
        card = ctk.CTkFrame(self.container, fg_color=CARD, corner_radius=8)
        card.place(relx=0.5, rely=0.5, anchor="center")
 
        ctk.CTkLabel(card, text="Clinic Login", font=TITLE_FONT,
                 text_color=ACCENT, fg_color="transparent").pack(pady=(28, 12))
 
        self.username_entry = self._field(card, "Username")
        self.password_entry = self._field(card, "Password", show="*")
 
        self.status_label = ctk.CTkLabel(card, text="", font=("Segoe UI", 10),
                                     fg_color=CARD, text_color=ERROR)
        self.status_label.pack(pady=(8, 8))
 
        self._button(card, "Log In", self.attempt_login).pack(pady=(0, 28))
 
        self.username_entry.focus_set()
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
    
    # attempt to log in with the entered credentials.
    def attempt_login(self):
        result = auth.authenticate(self.username_entry.get(),
                                   self.password_entry.get())
        if result is None:
            self.status_label.configure(text="Invalid username or password.")
            self.password_entry.delete(0, tk.END)
            return
        self.current_user, self.current_role = result
        self.show_home()
    
    # logout
    def logout(self):
        self.current_user = None
        self.current_role = None
        self.show_login()
 
    # routing after login
    def show_home(self):
        if self.current_role == "Admin":
            self.show_admin_panel()
        elif self.current_role in ("Nurse", "Medical Officer", "Dr"):
            self.show_staff_dashboard()
        else:  # Patient
            self.show_role_placeholder()
 
    def show_role_placeholder(self):
        # Temporary -- the Dr/Nurse/MO/Patient panels come next.
        
        self._clear()
        self._configure_window(900, 650, resizable=True) 
        wrap = tk.Frame(self.container, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(wrap, text=f"Logged in as {self.current_user}",
                 font=("Segoe UI Semibold", 16), bg=BG,
                 fg=FG).pack(pady=(0, 4))
        tk.Label(wrap, text=self.current_role, font=FONT,
                 bg=BG, fg=MUTED).pack(pady=(0, 24))
        tk.Label(wrap, text="(role panel coming soon)",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 24))
        self._button(wrap, "Log Out", self.logout, bg=FIELD, fg=FG,
                     width=16).pack()
    
    # Build a tile for an app in the staff dashboard. Each tile has a label, description, and an "Open" button that launches the app's screen.
    def _build_app_tile(self, parent, app):
        tile = tk.Frame(parent, bg=CARD, padx=20, pady=16)
        tile.pack(fill="x", pady=6)

        tk.Label(tile, text=app["label"], font=("Segoe UI Semibold", 14),
                 bg=CARD, fg=FG, anchor="w").pack(fill="x")
        tk.Label(tile, text=app["description"], font=("Segoe UI", 10),
                 bg=CARD, fg=MUTED, anchor="w").pack(fill="x", pady=(2, 10))

        # turn the method-name string into the actual method, and launch it
        launch = getattr(self, app["screen"])
        self._button(tile, "Open", launch, width=10).pack(anchor="w")

    # ----- Staff Dashboard ------------------------------------------------
    def show_staff_dashboard(self):
        
        self._clear()
        self._configure_window(700, 600)

        self._dashboard_bg = tk.PhotoImage(file="assets/clinic_app_bg_med_1.png")
        bg_label = tk.Label(self.container, image=self._dashboard_bg, borderwidth=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        frame = ctk.CTkFrame(self.container, fg_color=CARD, corner_radius=12, width=560, height=380)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)  # prevent the frame from resizing to fit its contents

        # header
        ctk.CTkLabel(frame, text="STAFF DASHBOARD", font=TITLE_FONT,
                     fg_color="transparent", text_color=FG).pack(pady=(28, 2))
        ctk.CTkLabel(frame,
                     text=f"Signed in as {auth.display_name(self.current_user)} ({self.current_role})",
                     font=("Segoe UI", 10), fg_color="transparent",
                     text_color=MUTED).pack(pady=(0, 24))

        # one tile per app this role can access
        for app in STAFF_APPS:
            if self.current_role not in app["roles"]:
                continue          # gated out — don't render it
            self._build_app_tile(frame, app)

        # Log Out lives here now — the hub, not each app
        self._button(frame, "Log Out", self.logout, bg=FIELD, fg=FG,
                     width=16).pack(pady=(24, 28), padx=4)

     # --- clinical: patient list ------------------------------------
    def show_patient_list(self):
        win = ctk.CTkToplevel(self)
        win.title("Patients")
        win.configure(fg_color=BG)
        win.geometry(self._center_geometry(900, 650))
        win.transient(self)     # keep it above the main window
        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())
        frame = tk.Frame(win, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="PATIENTS", font=TITLE_FONT, bg=BG,
                 fg=FG).pack(pady=(0, 2))
        tk.Label(frame,
                 text=f"Signed in as {self.current_user} ({self.current_role})",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 16))

        tk.Label(frame, text="Select a patient  (double-click to open)",
                 font=FONT, bg=BG, fg=MUTED, anchor="w").pack(fill="x")

        self._ensure_tree_style()
        win.search_criterion = tk.StringVar(value="all")
        
        search_row = tk.Frame(frame, bg=BG)
        search_row.pack(fill="x", pady=(0, 8))
        
        tk.Label(search_row, text="Search:", font=FONT, bg=BG,
                 fg=MUTED).pack(side="left", padx=(0, 6))

        win.search_entry = tk.Entry(search_row, font=FONT, bg=FIELD, fg=FG,
                                     insertbackground=FG, relief="flat", width=24)
        win.search_entry.pack(side="left", ipady=3, padx=(0, 12))
        win.search_entry.bind("<KeyRelease>", lambda e: self._on_search(win))
        for label, value in (("All", "all"), ("First", "first"),
                             ("Last", "last"), ("ID", "id")):
            tk.Radiobutton(search_row, text=label, value=value,
                           variable=win.search_criterion,
                           font=FONT, bg=BG, fg=FG, selectcolor=FIELD,
                           activebackground=BG, activeforeground=FG,
                           command=lambda: self._on_search(win)).pack(side="left")

        list_wrap = tk.Frame(frame, bg=BG)
        list_wrap.pack(fill="both", expand=True, pady=(4, 12))
        scroll = tk.Scrollbar(list_wrap)
        scroll.pack(side="right", fill="y")
        
        win.patient_tree = ttk.Treeview(
            list_wrap, style="Clinic.Treeview",
            columns=("name", "id", "dob", "address"), show="headings",
            yscrollcommand=scroll.set)
        win.patient_tree.heading("name", text="Name", anchor="w")
        win.patient_tree.column("name", width=220, anchor="w")
        win.patient_tree.heading("id", text="Patient ID", anchor="center")
        win.patient_tree.column("id", width=160, anchor="center")
        win.patient_tree.heading("dob", text="Date of Birth", anchor="center")
        win.patient_tree.column("dob", width=110, anchor="center")
        win.patient_tree.heading("address", text="Address", anchor="w")
        win.patient_tree.column("address", width=220, anchor="w")
        
        win.patient_tree.tag_configure("Patient",
                                        foreground=FG)
        win.patient_tree.pack(side="left", fill="both", expand=True)
        scroll.config(command=win.patient_tree.yview)

        self._populate_patient_tree(win, patients.list_patients())
        win.patient_tree.bind("<Double-1>",
                               lambda e: self._open_selected_patient(win))
        win.patient_tree.bind("<<TreeviewSelect>>",
                              lambda e: win.patient_status.config(text=""))

        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x")
        
        open_col = tk.Frame(row, bg=BG)
        open_col.pack(side="left")
        self._button(open_col, "Open Patient",
                     lambda: self._open_selected_patient(win),
                     width=14).pack()
        win.patient_status = tk.Label(open_col, text="", font=("Segoe UI", 10),
                                      bg=BG, fg=ERROR)
        win.patient_status.pack(pady=(4, 0))

        self._button(row, "New Patient",
                     lambda: self.show_create_patient(win),
                     width=14).pack(side="left", padx=8, anchor="n")

        self._button(frame, "Close", win.destroy, bg=FIELD, fg=FG,
                     width=12).pack(pady=(12, 0))

    # Populate the patient tree with a list of patients.
    def _populate_patient_tree(self, win, patient_list):
        for item in win.patient_tree.get_children():
            win.patient_tree.delete(item)
        for pid, first, last, dob, address in patient_list:
            display_name = f"{first} {last}".strip()
            win.patient_tree.insert("", tk.END, iid=pid,
                                     values=(display_name, pid, dob, address), tags=("Patient",))
    
    # Handle search input changes by filtering the patient list and updating the treeview.
    def _on_search(self, win):
        query = win.search_entry.get()
        criterion = win.search_criterion.get()
        filtered = patients.filter_patients(patients.list_patients(), query, criterion)
        self._populate_patient_tree(win, filtered)

    # Open the selected patient in a new window. 
    # If no patient is selected, show an error message.
    def _open_selected_patient(self, win):
        selection = win.patient_tree.selection()
        if not selection:
            win.patient_status.config(text="Select a patient first.")
            return
        pid = selection[0]                                    # the iid IS the patient ID
        name = win.patient_tree.item(pid, "values")[0]        # name is the first column
        self.show_patient_view(win, pid, name)

    # --- clinical: patient view (notes) ----------------------------
    def show_patient_view(self, owner, patient_id, patient_name):
        existing_win = getattr(owner, "_patient_window", None)
        if existing_win is not None:
            try:
                existing_win.destroy()
            except tk.TclError:
                pass
        win = ctk.CTkToplevel(self)
        win.after(10, win.lift)
        win.after(10, win.focus_force)
        owner._patient_window = win
        win._owner = owner
        win.title(f"{patient_name}    {patient_id}")
        win.configure(fg_color=BG)
        win.geometry(self._center_geometry(700, 860))
        win.transient(self)     # keep it above the main window
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_patient_window(owner))

        # a body frame we can clear/rebuild to swap notes view <-> new note
        win._body = tk.Frame(win, bg=BG)
        win._body.pack(fill="both", expand=True)
        self._render_patient_notes(win, patient_id, patient_name)

    # Close the patient view window if it's open.
    def _close_patient_window(self, owner):
        win = getattr(owner, "_patient_window", None)
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
            owner._patient_window = None
    
    def show_create_patient(self, owner):
        win = ctk.CTkToplevel(self)
        win.title("New Patient")
        win.configure(fg_color=BG)
        win.geometry(self._center_geometry(460, 620))
        win.transient(owner)          # float over the list window that opened it
        win.lift()
        win.focus_force()

        card = tk.Frame(win, bg=CARD, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="New Patient", font=TITLE_FONT,
                 bg=CARD, fg=FG).pack(pady=(0, 16))
        
        first = self._field(card, "First Name")
        last = self._field(card, "Last Name")
        dob = self._field(card, "Date of Birth (YYYY-MM-DD)")
        address = self._field(card, "Address")
        medicare = self._field(card, "Medicare Number (10 digits)")

        status = tk.Label(card, text="", font=("Segoe UI", 10),
                          bg=CARD, fg=ERROR)
        status.pack(pady=(8, 8))

        def submit():
            ok, msg = patients.create_patient(
                first.get(), last.get(), dob.get(),
                address.get(), medicare.get())
            if ok:
                self._populate_patient_tree(owner, patients.list_patients())
                win.destroy()
            else:
                status.config(text=msg)
        buttons = tk.Frame(card, bg=CARD)
        buttons.pack(pady=(8, 0))
        self._button(buttons, "Create", submit, width=11).pack(side="left", padx=4)
        self._button(buttons, "Cancel", win.destroy, bg=FIELD, fg=FG,
                     width=11).pack(side="left", padx=4)
        first.focus_set()

    # --- clinical: new note ----------------------------------------
    # Render the new note form in the patient view window.

    def _format_prescription(self, rx):
        duration = f"{rx['duration_amount']} {rx['duration_unit']}"
        line = (f"{rx['medication']} — {rx['dosage']}, "
                f"{rx['frequency']} for {duration}")
        if rx.get("instructions"):
            line += f"\n{rx['instructions']}"
        return line

    def _format_rx_signature(self, rx):
        dt = datetime.fromisoformat(rx["created_at"])
        hour12 = dt.hour % 12 or 12
        ampm = "am" if dt.hour < 12 else "pm"
        when = f"{dt.day} {dt.strftime('%b')} {dt.year}, {hour12}:{dt.minute:02d}{ampm}"
        return f"— {rx['prescriber_name']}, {rx['prescriber_role']} · {when}"

    def _render_prescriptions_section(self, parent, win, patient_id, patient_name):
        for w in parent.winfo_children():
            w.destroy()

        rx_wrap = tk.Frame(parent, bg=CARD)
        rx_wrap.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(rx_wrap)
        scroll.pack(side="right", fill="y")
        rx_text = tk.Text(rx_wrap, bg=CARD, fg=FG, font=FONT,
                          relief="flat", wrap="word", padx=16, pady=12,
                          highlightthickness=0, yscrollcommand=scroll.set)
        rx_text.pack(side="left", fill="both", expand=True)
        scroll.config(command=rx_text.yview)
        rx_text.tag_configure("sig", foreground=MUTED,
                              font=("Segoe UI", 9, "italic"))
        rx_text.tag_configure("spacer", font=("Segoe UI", 4))

        rx_list = prescriptions.get_prescriptions(patient_id)
        if not rx_list:
            rx_text.insert("end", "No prescriptions yet.", "sig")
        else:
            for rx in rx_list:
                rx_text.insert("end", self._format_prescription(rx) + "\n")
                rx_text.insert("end", self._format_rx_signature(rx) + "\n", "sig")
                rx_text.insert("end", "\n", "spacer")
        rx_text.config(state="disabled")

    def _render_new_prescription(self, win, patient_id, patient_name):
        for w in win._body.winfo_children():
            w.destroy()
        frame = tk.Frame(win._body, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="New Prescription", font=TITLE_FONT,
                 bg=BG, fg=FG).pack(pady=(0, 2))
        tk.Label(frame, text=f"{patient_name}   {patient_id}",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 16))
        
        card = tk.Frame(frame, bg=CARD, padx=24, pady=16)
        card.pack(fill="x")

        medication = self._field(card, "Medication")
        dosage = self._field(card, "Dosage (e.g. 500mg)")

        tk.Label(card, text="Frequency", font=FONT, bg=CARD, fg=MUTED,
                 anchor="w").pack(fill="x", pady=(8, 2), padx=24)
        frequency = ctk.CTkOptionMenu(card,
                                      values=prescriptions.VALID_FREQUENCIES,
                                      fg_color=FIELD, button_color=FIELD,
                                      text_color=FG, width=240)
        frequency.set(prescriptions.VALID_FREQUENCIES[0])
        frequency.pack(padx=28, pady=(0, 4))

        tk.Label(card, text="Duration", font=FONT, bg=CARD, fg=MUTED,
                 anchor="w").pack(fill="x", pady=(8, 2), padx=24)
        dur_row = tk.Frame(card, bg=CARD)
        dur_row.pack(fill="x", padx=28)

        duration_amount = ctk.CTkEntry(dur_row, width=70, fg_color=FIELD,
                                       text_color=FG, border_width=0)
        duration_amount.pack(side="left")

        duration_unit = ctk.CTkOptionMenu(dur_row,
                                          values=prescriptions.VALID_DURATION_UNITS,
                                          fg_color=FIELD, button_color=FIELD,
                                          text_color=FG, width=110)
        duration_unit.set(prescriptions.VALID_DURATION_UNITS[0])
        duration_unit.pack(side="left", padx=(8, 0))

        tk.Label(card, text="Instructions (optional)", font=FONT, bg=CARD,
                 fg=MUTED, anchor="w").pack(fill="x", pady=(12, 2), padx=24)
        instructions = tk.Text(card, bg=FIELD, fg=FG, insertbackground=FG,
                               font=FONT, relief="flat", wrap="word",
                               height=4, padx=10, pady=8, highlightthickness=0)
        instructions.pack(fill="x", padx=28, pady=(0, 8))


        status = tk.Label(frame, text="", font=("Segoe UI", 10),
                          bg=BG, fg=ERROR)
        status.pack(pady=(8, 4))

        def submit():
            ok, msg = prescriptions.add_prescription(
                patient_id,
                medication.get(),
                dosage.get(),
                frequency.get(),
                duration_amount.get(),
                duration_unit.get(),
                instructions.get("1.0", "end").strip(),
                auth.display_name(self.current_user),
                self.current_role)
            if ok:
                self._render_patient_notes(win, patient_id, patient_name)
            else:
                status.config(text=msg)

        buttons = tk.Frame(frame, bg=BG)
        buttons.pack(pady=(4, 0))
        self._button(buttons, "Prescribe", submit, width=12).pack(side="left", padx=4)
        self._button(buttons, "Cancel",
                     lambda: self._render_patient_notes(win, patient_id, patient_name),
                     bg=FIELD, fg=FG, width=12).pack(side="left", padx=4)
        medication.focus_set()


    def _render_notes_section(self, parent, win, patient_id, patient_name):
        # clear whatever was in this parent
        for w in parent.winfo_children():
            w.destroy()

        notes_wrap = tk.Frame(parent, bg=CARD)
        notes_wrap.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(notes_wrap)
        scroll.pack(side="right", fill="y")
        notes_text = tk.Text(notes_wrap, bg=CARD, fg=FG, font=FONT,
                             relief="flat", wrap="word", padx=16, pady=12,
                             highlightthickness=0, yscrollcommand=scroll.set)
        notes_text.pack(side="left", fill="both", expand=True)
        scroll.config(command=notes_text.yview)
        notes_text.tag_configure("sig", foreground=MUTED,
                                 font=("Segoe UI", 9, "italic"))
        notes_text.tag_configure("spacer", font=("Segoe UI", 4))

        patient_notes = notes.get_notes(patient_id)
        if not patient_notes:
            notes_text.insert("end", "No notes yet.", "sig")
        else:
            for n in patient_notes:
                notes_text.insert("end", n["text"] + "\n")
                notes_text.insert("end", self._format_signature(n) + "\n", "sig")
                notes_text.insert("end", "\n", "spacer")
        notes_text.config(state="disabled")

        # the New Note button belongs with the notes, so it goes here too

    def _render_patient_notes(self, win, patient_id, patient_name):
        for w in win._body.winfo_children():
            w.destroy()
        frame = tk.Frame(win._body, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
        
        record = patients.get_patient(patient_id)
        if record is None:
            record = {}
  
        header = tk.Frame(frame, bg=BG)
        header.pack(fill="x")

        tk.Label(header, text=patient_name, font=TITLE_FONT, bg=BG,
                 fg=FG).pack(side="left")
        tk.Label(header, text=f"   {patient_id}", font=FONT, bg=BG,
                 fg=MUTED).pack(side="left")

        details = tk.Frame(frame, bg=CARD, padx=20, pady=14)
        details.pack(fill="x", pady=(12, 0))

        fields = [
            ("Patient ID",  patient_id),
            ("Date of Birth", self._format_dob(record.get("dob", ""))),
            ("Medicare",    self._format_medicare(record.get("medicare", ""))),
            ("Address",     record.get("address", "")),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(details, text=label, font=("Segoe UI", 9),
                     bg=CARD, fg=MUTED, anchor="w").grid(row=i, column=0,
                                                          sticky="w", pady=2)
            tk.Label(details, text=value or "—", font=FONT,
                     bg=CARD, fg=FG, anchor="w").grid(row=i, column=1,
                                                       sticky="w", padx=(16, 0), pady=2)

        
        tabs = ctk.CTkTabview(
            frame, anchor="nw",
            fg_color=CARD,                              # the tab CONTENT area
            segmented_button_fg_color=FIELD,            # the tab bar background
            segmented_button_selected_color=ACCENT,     # active tab
            segmented_button_selected_hover_color=self._shade(ACCENT),
            segmented_button_unselected_color=FIELD,    # inactive tab
            segmented_button_unselected_hover_color=self._shade(FIELD),
            text_color=FG,                              # tab label text
        )
        tabs.pack(fill="both", expand=True, pady=(0, 0))
        tabs.add("Notes")

        if self.current_role == "Dr":
            tabs.add("Prescriptions")
            self._render_prescriptions_section(tabs.tab("Prescriptions"),
                                               win, patient_id, patient_name)

        self._render_notes_section(tabs.tab("Notes"), win, patient_id, patient_name)
 
        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x", pady=(24, 0))
        self._button(row, "New Note",
                     lambda: self._render_new_note(win, patient_id, patient_name),
                     width=12).pack(side="left")
        if self.current_role == "Dr":
            self._button(row, "New Prescription",
                         lambda: self._render_new_prescription(win, patient_id, patient_name),
                         width=16).pack(side="left", padx=8)
        self._button(row, "Close", win.destroy, bg=FIELD, fg=FG,
                     width=12).pack(side="right")

    # Create a new note for the patient. This is a separate screen in the patient window.
    def _render_new_note(self, win, patient_id, patient_name):
        for w in win._body.winfo_children():
            w.destroy()
        frame = tk.Frame(win._body, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
 
        tk.Label(frame, text="New Note", font=TITLE_FONT, bg=BG,
                 fg=FG).pack(pady=(0, 2))
        tk.Label(frame, text=f"{patient_name}   {patient_id}",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 16))
 
        text_box = tk.Text(frame, bg=FIELD, fg=FG, insertbackground=FG,
                           font=FONT, relief="flat", wrap="word",
                           padx=12, pady=10, height=12, highlightthickness=0)
        text_box.pack(fill="both", expand=True)
        text_box.focus_set()
 
        tk.Label(frame,
                 text=f"Will be signed: {auth.display_name(self.current_user)}, {self.current_role}",
                 font=("Segoe UI", 9, "italic"), bg=BG,
                 fg=MUTED).pack(pady=(8, 4), anchor="w")
        status = tk.Label(frame, text="", font=("Segoe UI", 10), bg=BG, fg=ERROR)
        status.pack(pady=(0, 8))
 
        def submit():
            content = text_box.get("1.0", "end").strip()
            author = auth.display_name(self.current_user)
            ok, msg = notes.add_note(patient_id, content,
                                     author, self.current_role)
            if ok:
                self._render_patient_notes(win, patient_id, patient_name)
            else:
                status.config(text=msg)
 
        buttons = tk.Frame(frame, bg=BG)
        buttons.pack()
        self._button(buttons, "Save", submit, width=11).pack(side="left", padx=4)
        self._button(buttons, "Cancel",
                     lambda: self._render_patient_notes(win, patient_id, patient_name),
                     bg=FIELD, fg=FG, width=11).pack(side="left", padx=4)


    # --- admin panel -----------------------------------------------
    def show_admin_panel(self):
        
        self._clear()
        self._configure_window(680, 680) 
        
        frame = tk.Frame(self.container, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
 
        tk.Label(frame, text="ADMIN PANEL", font=TITLE_FONT, bg=BG,
                 fg=FG).pack(pady=(0, 2))
        tk.Label(frame, text=f"Signed in as {self.current_user}",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 16))
 
        tk.Label(frame, text="Registered users  (click to select)",
                 font=FONT, bg=BG, fg=MUTED, anchor="w").pack(fill="x")
 
        self._ensure_tree_style()

        list_wrap = tk.Frame(frame, bg=BG)
        list_wrap.pack(fill="both", expand=True, pady=(4, 12))
        scroll = tk.Scrollbar(list_wrap)
        scroll.pack(side="right", fill="y")

        self.user_tree = ttk.Treeview(
            list_wrap, style="Clinic.Treeview",
            columns=("username", "name", "role", "id"), show="headings",
            yscrollcommand=scroll.set, height=9)
        for col, text, width in (("username", "Username", 150),
                                 ("name", "Full Name", 150),
                                 ("role", "Role", 130)):
            self.user_tree.heading(col, text=text, anchor="w")
            self.user_tree.column(col, width=width, anchor="w")
        self.user_tree.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.user_tree.yview)

        self._refresh_user_list()
 
        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x")
        self._button(row, "Create User", self.show_create_user,
                     width=10).pack(side="left", expand=True, fill="x",
                                    padx=(0, 4))
        self._button(row, "Assign Role", self._assign_selected, bg=FIELD,
                     fg=FG, width=10).pack(side="left", expand=True,
                                           fill="x", padx=4)
        self._button(row, "Delete User", self._delete_selected, bg=DANGER,
                     width=10).pack(side="left", expand=True, fill="x",
                                    padx=(4, 0))
 
        self.admin_status = tk.Label(frame, text="", font=("Segoe UI", 10),
                                     bg=BG, fg=MUTED)
        self.admin_status.pack(pady=(10, 6))
        self._button(frame, "Log Out", self.logout, bg=FIELD, fg=FG,
                     width=16).pack()
    
    # --- admin panel helpers ----------------------------------------

    # Refresh the user list in the admin panel's treeview.
    def _refresh_user_list(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        for username, full_name, role in auth.list_users():
            self.user_tree.insert("", tk.END, iid=username,
                                  values=(username, full_name, role), tags=(role,))
    
    # Get the username of the currently selected user in the admin panel's treeview, or None if no user is selected.
    def _selected_username(self):
        selection = self.user_tree.selection()
        return selection[0] if selection else None
    
    # Assign the selected user to a new role.
    def _assign_selected(self):
        name = self._selected_username()
        if name is None:
            self.admin_status.config(text="Select a user first.", fg=ERROR)
            return
        self.show_assign_role(name)
    
    # Delete the selected user after confirmation.
    def _delete_selected(self):
        name = self._selected_username()
        if name is None:
            self.admin_status.config(text="Select a user first.", fg=ERROR)
            return
        # messagebox is the natural GUI translation of the CLI yes/no prompt.
        if messagebox.askyesno("Delete user",
                               f"Delete '{name}'?\nThis cannot be undone."):
            ok, msg = auth.delete_user(name)
            self._refresh_user_list()
            self.admin_status.config(text=msg, fg=(MUTED if ok else ERROR))
 
    # --- create user form ------------------------------------------
    def show_create_user(self):
        
        self._clear()
        self._configure_window(560, 700)
        card = tk.Frame(self.container, bg=CARD, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(card, text="Create User", font=TITLE_FONT,
                 bg=CARD, fg=ACCENT).pack(pady=(0, 8))
 
        username = self._field(card, "Username")
        first_name = self._field(card, "First Name")
        last_name = self._field(card, "Last Name")
        password = self._field(card, "Password", show="*")
        confirm = self._field(card, "Confirm Password", show="*")
 
        tk.Label(card, text="Role", font=FONT, bg=CARD, fg=MUTED,
                 anchor="w").pack(fill="x", pady=(10, 2))
        role_var = self._role_radios(card, auth.DEFAULT_ROLE)
 
        status = tk.Label(card, text="", font=("Segoe UI", 10),
                          bg=CARD, fg=ERROR)
        status.pack(pady=(8, 8))
 
        def submit():
            if password.get() != confirm.get():
                status.config(text="Passwords do not match.")
                return
            ok, msg = auth.create_user(username.get(), first_name.get(),
                                       last_name.get(), password.get(),
                                       role_var.get())
            if ok:
                self.show_admin_panel()
                self.admin_status.config(text=msg, fg=MUTED)
            else:
                status.config(text=msg)
 
        buttons = tk.Frame(card, bg=CARD)
        buttons.pack()
        self._button(buttons, "Create", submit, width=11).pack(side="left",
                                                                padx=4)
        self._button(buttons, "Cancel", self.show_admin_panel, bg=FIELD,
                     fg=FG, width=11).pack(side="left", padx=4)
        username.focus_set()
 
    # --- assign role form ------------------------------------------
    def show_assign_role(self, username):
        
        self._clear()
        card = tk.Frame(self.container, bg=CARD, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(card, text="Assign Role", font=TITLE_FONT,
                 bg=CARD, fg=ACCENT).pack(pady=(0, 6))
        tk.Label(card, text=username, font=("Segoe UI Semibold", 13),
                 bg=CARD, fg=FG).pack(pady=(0, 16))
 
        current = next((role for name, _, role in auth.list_users()
                        if name == username), auth.DEFAULT_ROLE)
        role_var = self._role_radios(card, current)
 
        def submit():
            ok, msg = auth.set_role(username, role_var.get())
            self.show_admin_panel()
            self.admin_status.config(text=msg, fg=(MUTED if ok else ERROR))
 
        buttons = tk.Frame(card, bg=CARD)
        buttons.pack(pady=(16, 0))
        self._button(buttons, "Save", submit, width=11).pack(side="left",
                                                              padx=4)
        self._button(buttons, "Cancel", self.show_admin_panel, bg=FIELD,
                     fg=FG, width=11).pack(side="left", padx=4)
 
 
if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()
