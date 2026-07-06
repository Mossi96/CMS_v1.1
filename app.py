# ======== Clinical system app prototype. Version 1.2 ========

# A clinic system GUI built with tkinter and customtkinter, 
# using a backend auth.py module for user management and 
# notes.py for patient notes.


import tkinter as tk
from tkinter import messagebox, ttk
import auth
import notes
import theme
import customtkinter as ctk
from datetime import datetime
 
 
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
        self._active_screen = None
        self._patient_window = None

        self._build_chrome()
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
        tk.Label(parent, text=label, font=FONT, bg=CARD, fg=MUTED,
                 anchor="w").pack(fill="x", pady=(8, 2))
        entry = tk.Entry(parent, font=FONT, width=28, bg=FIELD, fg=FG,
                         insertbackground=FG, relief="flat",
                         show=(show or ""))
        entry.pack(ipady=4)
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

    # --- chrome (theme picker) --------------------------------------

    # Build the theme picker chrome at the bottom of the window.
    def _build_chrome(self):
        self._chrome = tk.Frame(self, bg=BG)
        self._chrome.pack(fill="x", side="bottom")
        self._theme_label = tk.Label(self._chrome, text="Theme:",
                                     font=("Segoe UI", 10), bg=BG, fg=MUTED)
        self._theme_label.pack(side="left", padx=(12, 6), pady=6)
        self._theme_menu = ctk.CTkOptionMenu(
            self._chrome, values=theme.names(), command=self._change_theme,
            width=170, height=28, corner_radius=8,
            fg_color=FIELD, button_color=FIELD,
            button_hover_color=self._shade(FIELD), text_color=FG,
            font=("Segoe UI", 10))
        self._theme_menu.set(theme.current_name())
        self._theme_menu.pack(side="left", pady=6)

    # Switch the active theme and refresh the UI to apply it.
    def _change_theme(self, name):
        theme.apply(name)
        _load_theme()
        ctk.set_appearance_mode(theme.get()["mode"])
        self.configure(bg=BG)
        self.container.configure(bg=BG)
        self._chrome.configure(bg=BG)
        self._theme_label.configure(bg=BG, fg=MUTED)
        self._theme_menu.configure(fg_color=FIELD, button_color=FIELD,
                                   button_hover_color=self._shade(FIELD),
                                   text_color=FG)
        if self._active_screen:  # refresh the current screen to apply new colours
            self._active_screen()

    # --- login ------------------------------------------------------

    # Show the login screen.
    def show_login(self):
        self._active_screen = self.show_login
        self._clear()
        self._configure_window(460, 560) 
        card = tk.Frame(self.container, bg=CARD, padx=32, pady=28)
        card.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(card, text="Clinic Login", font=TITLE_FONT,
                 bg=CARD, fg=ACCENT).pack(pady=(0, 12))
 
        self.username_entry = self._field(card, "Username")
        self.password_entry = self._field(card, "Password", show="*")
 
        self.status_label = tk.Label(card, text="", font=("Segoe UI", 10),
                                     bg=CARD, fg=ERROR)
        self.status_label.pack(pady=(8, 8))
 
        self._button(card, "Log In", self.attempt_login).pack()
 
        self.username_entry.focus_set()
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
    
    # attempt to log in with the entered credentials.
    def attempt_login(self):
        result = auth.authenticate(self.username_entry.get(),
                                   self.password_entry.get())
        if result is None:
            self.status_label.config(text="Invalid username or password.")
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
            self.show_patient_list()
        else:  # Patient
            self.show_role_placeholder()
 
    def show_role_placeholder(self):
        # Temporary -- the Dr/Nurse/MO/Patient panels come next.
        self._active_screen = self.show_role_placeholder
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
    

     # --- clinical: patient list ------------------------------------
    def show_patient_list(self):
        self._active_screen = self.show_patient_list
        self._clear()
        self._configure_window(900, 650, resizable=True)
        frame = tk.Frame(self.container, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="PATIENTS", font=TITLE_FONT, bg=BG,
                 fg=FG).pack(pady=(0, 2))
        tk.Label(frame,
                 text=f"Signed in as {self.current_user} ({self.current_role})",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(pady=(0, 16))

        tk.Label(frame, text="Select a patient  (double-click to open)",
                 font=FONT, bg=BG, fg=MUTED, anchor="w").pack(fill="x")

        self._ensure_tree_style()
        list_wrap = tk.Frame(frame, bg=BG)
        list_wrap.pack(fill="both", expand=True, pady=(4, 12))
        scroll = tk.Scrollbar(list_wrap)
        scroll.pack(side="right", fill="y")
        self.patient_tree = ttk.Treeview(
            list_wrap, style="Clinic.Treeview",
            columns=("name", "id"), show="headings",
            yscrollcommand=scroll.set)
        self.patient_tree.heading("name", text="Name", anchor="w")
        self.patient_tree.column("name", width=220, anchor="w")
        self.patient_tree.heading("id", text="Patient ID", anchor="center")
        self.patient_tree.column("id", width=160, anchor="center")
        self.patient_tree.tag_configure("Patient",
                                        foreground=FG)
        self.patient_tree.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.patient_tree.yview)

        for name, display_name, pid in auth.list_patients():
            self.patient_tree.insert("", tk.END, iid=name,
                                     values=(display_name, pid), tags=("Patient",))
        self.patient_tree.bind("<Double-1>",
                               lambda e: self._open_selected_patient())

        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x")
        self._button(row, "Open Patient", self._open_selected_patient,
                     width=14).pack(side="left")
        self.patient_status = tk.Label(row, text="", font=("Segoe UI", 10),
                                       bg=BG, fg=ERROR)
        self.patient_status.pack(side="left", padx=12)
        self._button(frame, "Log Out", self.logout, bg=FIELD, fg=FG,
                     width=16).pack(pady=(12, 0))

    # Open the selected patient in a new window. 
    # If no patient is selected, show an error message.
    def _open_selected_patient(self):
        selection = self.patient_tree.selection()
        if not selection:
            self.patient_status.config(text="Select a patient first.")
            return
        name, pid = self.patient_tree.item(selection[0], "values")
        self.show_patient_view(pid, name)

    # --- clinical: patient view (notes) ----------------------------
    def show_patient_view(self, patient_id, patient_name):
        self._close_patient_window()
 
        win = ctk.CTkToplevel(self)
        self._patient_window = win
        win.title(f"{patient_name}    {patient_id}")
        win.configure(fg_color=BG)
        win.geometry(self._center_geometry(640, 720))
        win.transient(self)     # keep it above the main window
        win.protocol("WM_DELETE_WINDOW", self._close_patient_window)
 
        # a body frame we can clear/rebuild to swap notes view <-> new note
        win._body = tk.Frame(win, bg=BG)
        win._body.pack(fill="both", expand=True)
        self._render_patient_notes(win, patient_id, patient_name)

    # Close the patient view window if it's open.
    def _close_patient_window(self):
        win = getattr(self, "_patient_window", None)
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
            self._patient_window = None
    
    # --- clinical: new note ----------------------------------------
    # Render the new note form in the patient view window.
    def _render_patient_notes(self, win, patient_id, patient_name):
        for w in win._body.winfo_children():
            w.destroy()
        frame = tk.Frame(win._body, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)
 
        header = tk.Frame(frame, bg=BG)
        header.pack(fill="x")
        tk.Label(header, text=patient_name, font=TITLE_FONT, bg=BG,
                 fg=FG).pack(side="left")
        tk.Label(header, text=f"   {patient_id}", font=FONT, bg=BG,
                 fg=MUTED).pack(side="left")
 
        tk.Label(frame, text="Notes", font=FONT, bg=BG, fg=MUTED,
                 anchor="w").pack(fill="x", pady=(16, 4))
 
        notes_wrap = tk.Frame(frame, bg=CARD)
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
        notes_text.config(state="disabled")   # read-only
 
        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x", pady=(12, 0))
        self._button(row, "New Note",
                     lambda: self._render_new_note(win, patient_id, patient_name),
                     width=12).pack(side="left")
        self._button(row, "Close", self._close_patient_window, bg=FIELD, fg=FG,
                     width=10).pack(side="right")

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
        self._active_screen = self.show_admin_panel
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
        self.user_tree.heading("id", text="Patient ID", anchor="center")
        self.user_tree.column("id", width=120, anchor="center")
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
        for username, full_name, role, pid in auth.list_users():
            self.user_tree.insert("", tk.END, iid=username,
                                  values=(username, full_name, role, pid), tags=(role,))
    
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
        self._active_screen = self.show_create_user
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
        self._active_screen = lambda: self.show_assign_role(username)
        self._clear()
        card = tk.Frame(self.container, bg=CARD, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(card, text="Assign Role", font=TITLE_FONT,
                 bg=CARD, fg=ACCENT).pack(pady=(0, 6))
        tk.Label(card, text=username, font=("Segoe UI Semibold", 13),
                 bg=CARD, fg=FG).pack(pady=(0, 16))
 
        current = next((role for name, _, role, _ in auth.list_users()
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
