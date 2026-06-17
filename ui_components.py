"""
UI Components and Windows for Kriyaban Meditation Sangha application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from print_manager import PrintManager


# ---------------------------------------------------------------------------
# Helper: shared preview window
# ---------------------------------------------------------------------------
def _show_receipt_preview_window(parent_root, img_path, on_print_save, on_save_only):
    """
    Open a Toplevel print-preview window with Print & Save / Save Only buttons.
    on_print_save() and on_save_only() are zero-argument callables.
    """
    win = tk.Toplevel(parent_root)
    win.title("Print Preview")
    win.geometry("920x820")

    tk.Label(win, text="Print Preview", font=("Arial", 18, "bold")).pack(pady=12)

    img_frame = tk.Frame(win, bg="white", relief=tk.SUNKEN, bd=2)
    img_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    try:
        img = Image.open(img_path)
        img.thumbnail((860, 620), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(img_frame, image=photo, bg="white")
        lbl.image = photo  # keep reference
        lbl.pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        tk.Label(img_frame, text=f"Preview error: {e}").pack(pady=20)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=14)

    def _do_print_save():
        on_print_save()
        win.destroy()

    def _do_save_only():
        on_save_only()
        win.destroy()

    tk.Button(btn_frame, text="Print & Save", command=_do_print_save,
              font=("Arial", 12), bg="#4472C4", fg="white", width=16).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_frame, text="Save Only", command=_do_save_only,
              font=("Arial", 12), bg="#808080", fg="white", width=14).pack(side=tk.LEFT, padx=6)


# ---------------------------------------------------------------------------
# Donation Window
# ---------------------------------------------------------------------------
class DonationWindow(tk.Frame):
    """Frame for donation entry"""

    def __init__(self, parent, on_submit=None, on_cancel=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.form_data = {}
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Donation Entry", font=("Arial", 20, "bold")).pack(pady=14)

        # Button row at the bottom (pack before form so it stays visible)
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, pady=14)
        tk.Button(btn_frame, text="Submit", command=self.submit_form,
                  font=("Arial", 12), bg="#4472C4", fg="white", width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self._cancel,
                  font=("Arial", 12), bg="#C5504C", fg="white", width=14).pack(side=tk.LEFT, padx=5)

        # Scrollable canvas
        canvas = tk.Canvas(self, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        form = tk.Frame(canvas, padx=30, pady=10)
        cw = canvas.create_window((0, 0), window=form, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_resize(e):
            canvas.itemconfig(cw, width=e.width)
        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        form.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind("<MouseWheel>", _on_wheel)
        form.bind("<MouseWheel>", _on_wheel)

        # --- Required fields ---
        r = 0
        tk.Label(form, text="Name: *", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form, font=("Arial", 12), width=40)
        self.name_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        tk.Label(form, text="Phone: *", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.phone_entry = tk.Entry(form, font=("Arial", 12), width=30)
        self.phone_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        tk.Label(form, text="Donation Amount (Rs.): *", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.amount_entry = tk.Entry(form, font=("Arial", 12), width=20)
        self.amount_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        # --- Optional separator ---
        ttk.Separator(form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=14); r += 1
        tk.Label(form, text="Optional Information", font=("Arial", 10, "italic"), fg="#888"
                 ).grid(row=r, column=0, columnspan=2, sticky="w"); r += 1

        tk.Label(form, text="Email:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.email_entry = tk.Entry(form, font=("Arial", 12), width=40)
        self.email_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        tk.Label(form, text="Aadhar No.:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.aadhar_entry = tk.Entry(form, font=("Arial", 12), width=25)
        self.aadhar_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        tk.Label(form, text="PAN:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.pan_entry = tk.Entry(form, font=("Arial", 12), width=20)
        self.pan_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8); r += 1

        tk.Label(form, text="Address:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=8)
        self.address_entry = tk.Entry(form, font=("Arial", 12), width=50)
        self.address_entry.grid(row=r, column=1, sticky="w", padx=12, pady=8)

    def submit_form(self):
        name   = self.name_entry.get().strip()
        phone  = self.phone_entry.get().strip()
        amount = self.amount_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Name is required"); return
        if not phone or not phone.isdigit():
            messagebox.showerror("Validation Error", "Phone must be a valid number"); return
        if not amount or not amount.replace('.', '', 1).isdigit():
            messagebox.showerror("Validation Error", "Amount must be a valid number"); return

        self.form_data = {
            'name':    name,
            'email':   self.email_entry.get().strip(),
            'phone':   phone,
            'amount':  amount,
            'aadhar':  self.aadhar_entry.get().strip(),
            'pan':     self.pan_entry.get().strip(),
            'address': self.address_entry.get().strip(),
        }
        if self.on_submit:
            self.on_submit(self.form_data)

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()

    def clear_form(self):
        for e in [self.name_entry, self.phone_entry, self.amount_entry,
                  self.email_entry, self.aadhar_entry, self.pan_entry, self.address_entry]:
            e.delete(0, tk.END)


# ---------------------------------------------------------------------------
# Print Preview Window  (used by donation flow in main.py)
# ---------------------------------------------------------------------------
class PrintPreviewWindow(tk.Frame):
    """Frame for print preview — used inside a Toplevel by main.py"""

    def __init__(self, parent, image_path, on_print=None, on_close=None):
        super().__init__(parent)
        self.image_path = image_path
        self.on_print   = on_print
        self.on_close   = on_close
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Print Preview", font=("Arial", 20, "bold")).pack(pady=18)

        # Buttons at bottom first
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, pady=18)
        tk.Button(btn_frame, text="Print", command=self._print,
                  font=("Arial", 12), bg="#4472C4", fg="white", width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back", command=self._close,
                  font=("Arial", 12), bg="#808080", fg="white", width=14).pack(side=tk.LEFT, padx=5)

        # Image
        img_frame = tk.Frame(self, bg="white")
        img_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        try:
            img = Image.open(self.image_path)
            img.thumbnail((740, 580), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(img_frame, image=photo, bg="white")
            lbl.image = photo
            lbl.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            tk.Label(img_frame, text=f"Error loading image: {e}").pack()

    def _print(self):
        """Print using Windows shell — NOT notepad."""
        try:
            os.startfile(str(self.image_path), "print")
            messagebox.showinfo("Printing", "Print job sent to your default printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print:\n{e}")
        if self.on_print:
            self.on_print()

    def _close(self):
        if self.on_close:
            self.on_close()

    # Keep old names so main.py still works
    def print_document(self): self._print()
    def close_preview(self):  self._close()


# ---------------------------------------------------------------------------
# Meditation Window
# ---------------------------------------------------------------------------
class MeditationWindow(tk.Frame):
    """Frame for meditation enrollment — self-contained (saves + prints internally)."""

    MEDITATION_LEVELS = [
        ('Level 1 - Meditation for Starters', 1500),
        ('Level 2 - Raja Yoga',               1500),
        ('Level 3 - Discipleship',            1500),
        ('Level 4 - Kriya Yoga',              1500),
        ('Kriya Initiation',                  2500),
        ('Miscellaneous',                     None),   # price entered by user
    ]

    def __init__(self, parent, excel_manager=None, print_manager=None,
                 on_submit=None, on_cancel=None):
        super().__init__(parent)
        self.excel_manager = excel_manager
        self.print_manager = print_manager or PrintManager()
        self.on_submit     = on_submit
        self.on_cancel     = on_cancel
        self.form_data     = {}
        self._create_layout()

    def _create_layout(self):
        """One-time layout: title, persistent btn_frame, scrollable form_frame."""
        tk.Label(self, text="Meditation Enrollment",
                 font=("Arial", 20, "bold")).pack(pady=10)

        # Persistent button row (bottom)
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(side=tk.BOTTOM, pady=10)

        # Scrollable form area
        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._sb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.form_frame = tk.Frame(self._canvas, padx=25, pady=8)
        self._cw = self._canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind("<Configure>",
                             lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._cw, width=e.width))

        def _wheel(e): self._canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        self._canvas.bind("<MouseWheel>", _wheel)
        self.form_frame.bind("<MouseWheel>", _wheel)

        self._show_personal_info_form()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()

    def _clear_btns(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()
        # Reset scroll to top
        self._canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Step 1 — Personal Information
    # ------------------------------------------------------------------
    def _show_personal_info_form(self):
        self._clear_form()
        self._clear_btns()
        form = self.form_frame
        r = 0

        # Required fields
        tk.Label(form, text="Name: *", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.name_entry = tk.Entry(form, font=("Arial", 12), width=38)
        self.name_entry.insert(0, self.form_data.get('name', ''))
        self.name_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7); r += 1

        tk.Label(form, text="Phone: *", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.phone_entry = tk.Entry(form, font=("Arial", 12), width=28)
        self.phone_entry.insert(0, self.form_data.get('phone', ''))
        self.phone_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7); r += 1

        # Referral
        tk.Label(form, text="How did you hear about us?", font=("Arial", 12)).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(12, 2)); r += 1
        self.referral_var = tk.StringVar(value=self.form_data.get('referral_source', 'Friends'))
        ref_frame = tk.Frame(form)
        ref_frame.grid(row=r, column=0, columnspan=2, sticky="w", pady=4); r += 1
        for opt in ['Friends', 'Newspaper', 'Social Media', 'Others']:
            tk.Radiobutton(ref_frame, text=opt, variable=self.referral_var,
                           value=opt, font=("Arial", 11)).pack(side=tk.LEFT, padx=8)

        tk.Label(form, text="Additional Details: (Optional)", font=("Arial", 12)).grid(
            row=r, column=0, sticky="w", pady=(10, 2))
        self.referral_details = tk.Entry(form, font=("Arial", 12), width=38)
        self.referral_details.insert(0, self.form_data.get('referral_details', ''))
        self.referral_details.grid(row=r, column=1, sticky="w", padx=10, pady=(10, 2)); r += 1

        # Optional separator
        ttk.Separator(form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=14); r += 1
        tk.Label(form, text="Optional Information", font=("Arial", 10, "italic"), fg="#888"
                 ).grid(row=r, column=0, columnspan=2, sticky="w"); r += 1

        tk.Label(form, text="Email:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.email_entry = tk.Entry(form, font=("Arial", 12), width=38)
        self.email_entry.insert(0, self.form_data.get('email', ''))
        self.email_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7); r += 1

        tk.Label(form, text="Aadhar No.:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.aadhar_entry = tk.Entry(form, font=("Arial", 12), width=25)
        self.aadhar_entry.insert(0, self.form_data.get('aadhar', ''))
        self.aadhar_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7); r += 1

        tk.Label(form, text="PAN:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.pan_entry = tk.Entry(form, font=("Arial", 12), width=20)
        self.pan_entry.insert(0, self.form_data.get('pan', ''))
        self.pan_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7); r += 1

        tk.Label(form, text="Address:", font=("Arial", 12)).grid(row=r, column=0, sticky="w", pady=7)
        self.address_entry = tk.Entry(form, font=("Arial", 12), width=50)
        self.address_entry.insert(0, self.form_data.get('address', ''))
        self.address_entry.grid(row=r, column=1, sticky="w", padx=10, pady=7)

        # Buttons
        tk.Button(self.btn_frame, text="Next →", command=self._submit_personal_info,
                  font=("Arial", 12), bg="#4472C4", fg="white", width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Cancel", command=self._cancel,
                  font=("Arial", 12), bg="#C5504C", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    def _submit_personal_info(self):
        name  = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Name is required"); return
        if not phone or not phone.isdigit():
            messagebox.showerror("Validation Error", "Phone must be a valid number"); return

        self.form_data.update({
            'name':             name,
            'phone':            phone,
            'email':            self.email_entry.get().strip(),
            'referral_source':  self.referral_var.get(),
            'referral_details': self.referral_details.get().strip(),
            'aadhar':           self.aadhar_entry.get().strip(),
            'pan':              self.pan_entry.get().strip(),
            'address':          self.address_entry.get().strip(),
        })
        self._show_level_selection()

    # ------------------------------------------------------------------
    # Step 2 — Level Selection
    # ------------------------------------------------------------------
    def _show_level_selection(self):
        self._clear_form()
        self._clear_btns()
        form = self.form_frame

        tk.Label(form, text="Select Meditation Level", font=("Arial", 14, "bold")).pack(pady=10)

        self.level_var = tk.StringVar()

        for level, price in self.MEDITATION_LEVELS:
            display = (f"{level}   —   Rs. {price}" if price is not None
                       else f"{level}   (enter details below)")
            tk.Radiobutton(
                form, text=display, variable=self.level_var, value=level,
                font=("Arial", 12), command=self._on_level_change
            ).pack(anchor="w", padx=30, pady=6)

        # Miscellaneous extra fields (hidden until selected)
        self.misc_frame = tk.Frame(form, bd=1, relief=tk.GROOVE, padx=12, pady=8)
        tk.Label(self.misc_frame, text="Description:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.misc_desc_entry = tk.Entry(self.misc_frame, font=("Arial", 11), width=36)
        self.misc_desc_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.misc_frame, text="Amount (Rs.):", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.misc_price_entry = tk.Entry(self.misc_frame, font=("Arial", 11), width=16)
        self.misc_price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        tk.Button(self.btn_frame, text="Submit", command=self._submit_level,
                  font=("Arial", 12), bg="#4472C4", fg="white", width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="← Back", command=self._show_personal_info_form,
                  font=("Arial", 12), bg="#808080", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    def _on_level_change(self):
        if self.level_var.get() == 'Miscellaneous':
            self.misc_frame.pack(anchor="w", padx=42, pady=6)
        else:
            self.misc_frame.pack_forget()

    def _submit_level(self):
        level = self.level_var.get()
        if not level:
            messagebox.showerror("Validation Error", "Please select a meditation level"); return

        if level == 'Miscellaneous':
            desc      = self.misc_desc_entry.get().strip()
            price_str = self.misc_price_entry.get().strip()
            if not desc:
                messagebox.showerror("Validation Error", "Please enter a description"); return
            if not price_str or not price_str.replace('.', '', 1).isdigit():
                messagebox.showerror("Validation Error", "Please enter a valid amount"); return
            self.form_data['meditation_level'] = f"Miscellaneous - {desc}"
            self.form_data['course_fee']       = price_str
        else:
            self.form_data['meditation_level'] = level
            self.form_data['course_fee'] = next(
                (p for l, p in self.MEDITATION_LEVELS if l == level), 0)

        self._show_receipt_preview()

    # ------------------------------------------------------------------
    # Step 3 — Receipt Preview
    # ------------------------------------------------------------------
    def _show_receipt_preview(self):
        d = self.form_data

        # Predict the sequential receipt number (ws.max_row before appending = next record no.)
        predicted_receipt_no = None
        if self.excel_manager and self.excel_manager.workbook:
            try:
                ws = self.excel_manager.workbook['Meditation']
                predicted_receipt_no = ws.max_row   # consistent with what add_meditation will assign
            except Exception:
                pass

        img_path = self.print_manager.generate_meditation_receipt(
            name=d.get('name', ''),
            email=d.get('email', ''),
            phone=d.get('phone', ''),
            referral_source=d.get('referral_source', 'N/A'),
            meditation_level=d.get('meditation_level', ''),
            course_fee=d.get('course_fee', 0),
            aadhar=d.get('aadhar', ''),
            address=d.get('address', ''),
            pan=d.get('pan', ''),
            receipt_no=predicted_receipt_no,
        )

        if not img_path:
            messagebox.showerror("Error", "Failed to generate receipt"); return

        def _on_print_save():
            ok = self.print_manager.print_receipt(img_path)
            if ok:
                messagebox.showinfo("Printing", "Print job sent to your printer!")
            else:
                messagebox.showerror("Print Error", "Could not send to printer.")
            self._save_to_excel()
            self._reset()

        def _on_save_only():
            self._save_to_excel()
            self._reset()

        _show_receipt_preview_window(
            self.winfo_toplevel(), img_path, _on_print_save, _on_save_only)

    # ------------------------------------------------------------------
    # Save & Reset
    # ------------------------------------------------------------------
    def _save_to_excel(self):
        if not self.excel_manager:
            messagebox.showinfo("Info", "Enrollment recorded (no Excel file linked).")
            return
        d = self.form_data
        success, result = self.excel_manager.add_meditation(
            name=d.get('name', ''),
            email=d.get('email', ''),
            phone=d.get('phone', ''),
            referral_source=d.get('referral_source', ''),
            referral_details=d.get('referral_details', ''),
            meditation_level=d.get('meditation_level', ''),
            course_fee=d.get('course_fee', 0),
            aadhar=d.get('aadhar', ''),
            address=d.get('address', ''),
            pan=d.get('pan', ''),
        )
        if success:
            messagebox.showinfo("Saved", f"Enrollment saved successfully!")
        else:
            messagebox.showerror("Save Error", f"Could not save:\n{result}")

    def _reset(self):
        self.form_data = {}
        self._show_personal_info_form()

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()

    # Public alias kept for backward compat
    def reset_form(self): self._reset()


# ---------------------------------------------------------------------------
# Boutique Window
# ---------------------------------------------------------------------------
class BoutiqueWindow(tk.Frame):
    """Simple frame for boutique sales: item + price + payment method."""

    def __init__(self, parent, excel_manager=None, print_manager=None):
        super().__init__(parent)
        self.excel_manager = excel_manager
        self.print_manager = print_manager or PrintManager()
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Boutique", font=("Arial", 20, "bold")).pack(pady=16)

        # Buttons at bottom
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, pady=16)
        tk.Button(btn_frame, text="Submit & Preview", command=self._submit,
                  font=("Arial", 12), bg="#4472C4", fg="white", width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear", command=self._clear,
                  font=("Arial", 12), bg="#808080", fg="white", width=10).pack(side=tk.LEFT, padx=5)

        # Form
        form = tk.Frame(self)
        form.pack(padx=50, pady=30)

        tk.Label(form, text="Item Name:", font=("Arial", 13)).grid(
            row=0, column=0, sticky="w", pady=16, padx=6)
        self.item_entry = tk.Entry(form, font=("Arial", 13), width=36)
        self.item_entry.grid(row=0, column=1, pady=16, padx=12, sticky="w")

        tk.Label(form, text="Price (Rs.):", font=("Arial", 13)).grid(
            row=1, column=0, sticky="w", pady=16, padx=6)
        self.price_entry = tk.Entry(form, font=("Arial", 13), width=20)
        self.price_entry.grid(row=1, column=1, pady=16, padx=12, sticky="w")

        tk.Label(form, text="Payment Method:", font=("Arial", 13)).grid(
            row=2, column=0, sticky="w", pady=16, padx=6)
        self.payment_var = tk.StringVar(value="Cash")
        pay_frame = tk.Frame(form)
        pay_frame.grid(row=2, column=1, pady=16, padx=12, sticky="w")
        tk.Radiobutton(pay_frame, text="Cash",   variable=self.payment_var,
                       value="Cash",   font=("Arial", 13)).pack(side=tk.LEFT, padx=14)
        tk.Radiobutton(pay_frame, text="Online", variable=self.payment_var,
                       value="Online", font=("Arial", 13)).pack(side=tk.LEFT, padx=14)

    def _submit(self):
        item      = self.item_entry.get().strip()
        price_str = self.price_entry.get().strip()
        payment   = self.payment_var.get()

        if not item:
            messagebox.showerror("Validation Error", "Item name is required"); return
        if not price_str or not price_str.replace('.', '', 1).isdigit():
            messagebox.showerror("Validation Error", "Please enter a valid price"); return

        receipt_no = None
        if self.excel_manager:
            success, result = self.excel_manager.add_boutique(item, price_str, payment)
            if not success:
                messagebox.showerror("Save Error", f"Could not save:\n{result}"); return
            receipt_no = result   # sequential receipt number

        img_path = self.print_manager.generate_boutique_receipt(
            item, price_str, payment, receipt_no=receipt_no)
        if not img_path:
            messagebox.showerror("Error", "Could not generate receipt"); return

        def _on_print_save():
            ok = self.print_manager.print_receipt(img_path)
            if ok:
                messagebox.showinfo("Printing", "Print job sent!")
            else:
                messagebox.showerror("Print Error", "Could not send to printer.")
            self._clear()

        def _on_save_only():
            self._clear()
            messagebox.showinfo("Saved", f"'{item}' recorded successfully!")

        _show_receipt_preview_window(
            self.winfo_toplevel(), img_path, _on_print_save, _on_save_only)

    def _clear(self):
        self.item_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.payment_var.set("Cash")
