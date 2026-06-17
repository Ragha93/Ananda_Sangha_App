"""
Kriyaban Meditation Sangha - Main Application
A tkinter-based application for managing donations, meditation enrollment,
boutique purchases, books, and inventory.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os
import sys
import atexit

from excel_manager import ExcelManager
from print_manager import PrintManager
from ui_components import DonationWindow, MeditationWindow, BoutiqueWindow


class AnandaWestDelhi:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Kriyaban Meditation Sangha")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        # Initialize managers
        self.excel_manager = ExcelManager()
        self.print_manager = PrintManager()

        # Application state
        self.current_frame = None
        self.file_loaded = False
        self.file_path = None

        # Register cleanup
        atexit.register(self.on_close)

        # Start file loading dialog
        self.show_file_load_dialog()

    def show_file_load_dialog(self):
        """Show dialog to load or skip Excel file"""
        result = messagebox.askyesno(
            "Load Excel File",
            "Do you want to load an existing Excel file?\n\n"
            "Yes - Select an existing file\n"
            "No - Skip and create/use default file"
        )

        if result:
            file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            if file_path:
                if self.excel_manager.load_file(file_path):
                    self.file_path = file_path
                    self.file_loaded = True
                    messagebox.showinfo("Success", f"File loaded: {file_path}")
                    self.show_main_window()
                else:
                    messagebox.showerror("Error", "Could not load the selected file")
                    self.show_file_load_dialog()
            else:
                self.setup_default_file()
        else:
            self.setup_default_file()

    def setup_default_file(self):
        """Setup default file on Desktop"""
        desktop_path = Path.home() / "Desktop"
        file_name = "Kriyaban_Meditation_Sangha.xlsx"
        self.file_path = desktop_path / file_name

        if not self.excel_manager.create_new_file(str(self.file_path)):
            messagebox.showerror("Error", "Could not create default file")
            self.root.quit()
            return

        self.file_loaded = True
        messagebox.showinfo("Success", f"New file created: {self.file_path}")
        self.show_main_window()

    def show_main_window(self):
        """Show main application window"""
        if self.current_frame:
            self.current_frame.destroy()

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(main_frame, bg="#1e3a8a", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Kriyaban Meditation Sangha",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#1e3a8a"
        ).pack(pady=10)

        # File info
        tk.Label(
            main_frame,
            text=f"File: {os.path.basename(self.file_path)} | Loaded",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=5)

        # Content row: Notebook (left) + QR panel (right)
        content_row = tk.Frame(main_frame, bg="#f0f0f0")
        content_row.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

        # QR panel — fixed width on the right
        qr_panel = tk.Frame(content_row, bg="#f5f8ff", bd=2, relief=tk.GROOVE, width=195)
        qr_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        qr_panel.pack_propagate(False)
        self._populate_qr_panel(qr_panel)

        # Notebook fills the remaining left space
        self.notebook = ttk.Notebook(content_row)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_donation_tab()
        self.create_meditation_tab()
        self.create_boutique_tab()
        self.create_books_tab()
        self.create_inventory_tab()

        footer = tk.Frame(main_frame, bg="#f0f0f0")
        footer.pack(fill=tk.X, padx=20, pady=(0, 15))

        tk.Button(
            footer, text="Save & Exit", command=self.save_and_exit,
            font=("Arial", 12), bg="#4472C4", fg="white", width=20
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            footer, text="Load Different File", command=self.load_different_file,
            font=("Arial", 12), bg="#808080", fg="white", width=20
        ).pack(side=tk.RIGHT, padx=5)

        self.current_frame = main_frame

    def _populate_qr_panel(self, panel):
        """Load and display the QR code image inside the side panel."""
        # When frozen (exe), PyInstaller extracts bundled files to sys._MEIPASS.
        # Fall back to the folder next to the exe, then next to the script.
        if getattr(sys, 'frozen', False):
            candidates = [
                Path(getattr(sys, '_MEIPASS', '')) / "qr_code.jpeg",  # bundled inside exe
                Path(sys.executable).parent / "qr_code.jpeg",         # next to exe
                Path(getattr(sys, '_MEIPASS', '')) / "qr_code.png",
                Path(sys.executable).parent / "qr_code.png",
            ]
        else:
            app_dir = Path(__file__).parent
            candidates = [
                app_dir / "qr_code.jpeg",
                app_dir / "qr_code.png",
            ]

        qr_path = next((p for p in candidates if p.exists()), None)

        tk.Label(panel, text="Scan & Pay", font=("Arial", 11, "bold"),
                 bg="#f5f8ff", fg="#1e3a8a").pack(pady=(14, 6))

        if qr_path and qr_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(str(qr_path))
                img.thumbnail((175, 175), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(panel, image=photo, bg="#f5f8ff")
                lbl.image = photo          # keep reference
                lbl.pack(pady=4, padx=8)
            except Exception as ex:
                tk.Label(panel, text=f"QR load error:\n{ex}",
                         font=("Arial", 8), bg="#f5f8ff", fg="red",
                         wraplength=175, justify="center").pack(pady=10)
        else:
            tk.Label(panel,
                     text="Place  qr_code.png\nin app folder\nto show QR here",
                     font=("Arial", 9), bg="#f5f8ff", fg="#888",
                     justify="center").pack(pady=20, padx=8)

        tk.Label(panel, text="Kriyaban\nMeditation Sangha",
                 font=("Arial", 9, "bold"), bg="#f5f8ff", fg="#1e3a8a",
                 justify="center").pack(pady=(8, 14))

    def create_donation_tab(self):
        """Create donation entry tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Donation")

        content = DonationWindow(
            tab,
            on_submit=self.process_donation,
            on_cancel=self.cancel_donation
        )
        content.pack(fill=tk.BOTH, expand=True)
        self.donation_widget = content

    def create_meditation_tab(self):
        """Create meditation entry tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Meditation")

        content = MeditationWindow(
            tab,
            excel_manager=self.excel_manager,
            print_manager=self.print_manager,   # share the app-level print manager
            on_cancel=self.cancel_meditation
        )
        content.pack(fill=tk.BOTH, expand=True)
        self.meditation_widget = content

    def create_boutique_tab(self):
        """Create boutique tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Boutique")

        content = BoutiqueWindow(
            tab,
            excel_manager=self.excel_manager,
            print_manager=self.print_manager,
        )
        content.pack(fill=tk.BOTH, expand=True)
        self.boutique_widget = content

    def create_books_tab(self):
        """Create books tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Books")

        label = tk.Label(tab, text="Books Section - Coming Soon", font=("Arial", 14))
        label.pack(pady=50)

    def create_inventory_tab(self):
        """Create inventory tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventory")

        label = tk.Label(tab, text="Inventory Section - Coming Soon", font=("Arial", 14))
        label.pack(pady=50)

    def process_donation(self, data):
        """Show receipt preview first — saves only when user confirms."""
        from ui_components import _show_receipt_preview_window

        # Predict receipt number (same value add_donation will assign)
        predicted_receipt_no = None
        try:
            predicted_receipt_no = self.excel_manager.workbook['Donations'].max_row
        except Exception:
            pass

        img_path = self.print_manager.generate_donation_receipt(
            data['name'], data.get('email', ''), data['phone'], data['amount'],
            aadhar=data.get('aadhar', ''), address=data.get('address', ''),
            pan=data.get('pan', ''), receipt_no=predicted_receipt_no,
        )

        if not img_path:
            messagebox.showerror("Error", "Could not generate receipt")
            return

        def _save():
            success, result = self.excel_manager.add_donation(
                data['name'], data.get('email', ''), data['phone'], data['amount'],
                aadhar=data.get('aadhar', ''), address=data.get('address', ''),
                pan=data.get('pan', ''),
            )
            if success:
                messagebox.showinfo("Saved", "Donation recorded successfully!")
            else:
                messagebox.showerror("Save Error", f"Could not save:\n{result}")

        def on_print_save():
            _save()
            ok = self.print_manager.print_receipt(img_path)
            if ok:
                messagebox.showinfo("Printing", "Print job sent to your printer!")
            else:
                messagebox.showerror("Print Error", "Could not send to printer.")
            self.donation_widget.clear_form()
            self.show_main_window()

        def on_save_only():
            _save()
            self.donation_widget.clear_form()
            self.show_main_window()

        _show_receipt_preview_window(self.root, img_path, on_print_save, on_save_only)

    def cancel_donation(self):
        """Cancel donation"""
        self.donation_widget.clear_form()
        messagebox.showinfo("Cancelled", "Donation entry cancelled")

    def cancel_meditation(self):
        """Cancel meditation enrollment — reset the form"""
        if hasattr(self, 'meditation_widget'):
            self.meditation_widget.reset_form()


    def load_different_file(self):
        """Load a different Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )

        if file_path:
            if self.excel_manager.load_file(file_path):
                self.file_path = file_path
                self.file_loaded = True
                messagebox.showinfo("Success", f"File loaded: {file_path}")
                self.show_main_window()
            else:
                messagebox.showerror("Error", "Could not load the selected file")

    def save_and_exit(self):
        """Save and exit the application"""
        if self.excel_manager.save_file():
            messagebox.showinfo("Success", "File saved successfully!")
        self.root.quit()

    def on_close(self):
        """Handle application close"""
        if self.file_loaded:
            self.excel_manager.save_file()
        self.print_manager.cleanup()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AnandaWestDelhi(root)
    root.mainloop()


if __name__ == "__main__":
    main()
