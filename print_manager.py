"""
Image generation and printing utilities for Kriyaban Meditation Sangha application
"""

from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
from datetime import datetime
from pathlib import Path


class PrintManager:
    """Manages receipt image generation and printing"""

    ORG_NAME = "Kriyaban Meditation Sangha"
    HEADER_COLOR = (30, 58, 138)
    TEXT_COLOR = (33, 33, 33)
    ACCENT_COLOR = (70, 114, 196)
    BG_COLOR = (255, 255, 255)
    SEP_COLOR = (150, 150, 150)
    STAMP_COLOR = (160, 40, 40)
    VALUE_COLOR = (20, 60, 160)

    A4_W = 1240
    A4_H = 1754

    def __init__(self):
        self.generated_images = []
        self.temp_dir = Path(tempfile.gettempdir()) / "KriyabanSangha"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Font loading (regular + bold)
    # ------------------------------------------------------------------
    def _load_fonts(self):
        regular = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
        bold = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arial.ttf",   # fallback to regular
        ]

        def try_font(size, paths=regular):
            for path in paths:
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
            return ImageFont.load_default()

        return {
            "org_name":  try_font(26, bold),
            "receipt":   try_font(20, bold),
            "body":      try_font(18, regular),
            "body_bold": try_font(18, bold),
            "small":     try_font(14, regular),
            "stamp":     try_font(17, bold),
        }

    # ------------------------------------------------------------------
    # Text / drawing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _text_center(draw, cx, cy, text, font, fill):
        try:
            bb = draw.textbbox((0, 0), text, font=font)
            w, h = bb[2] - bb[0], bb[3] - bb[1]
            draw.text((cx - w // 2, cy - h // 2), text, fill=fill, font=font)
        except Exception:
            draw.text((cx, cy), text, fill=fill, font=font)

    @staticmethod
    def _text_right(draw, rx, y, text, font, fill):
        try:
            bb = draw.textbbox((0, 0), text, font=font)
            w = bb[2] - bb[0]
            draw.text((rx - w, y), text, fill=fill, font=font)
        except Exception:
            draw.text((rx, y), text, fill=fill, font=font)

    @staticmethod
    def _get_text_width(draw, text, font):
        try:
            bb = draw.textbbox((0, 0), text, font=font)
            return bb[2] - bb[0]
        except Exception:
            return len(text) * 11

    @staticmethod
    def _get_text_height(draw, font):
        try:
            bb = draw.textbbox((0, 0), "Ay", font=font)
            return bb[3] - bb[1]
        except Exception:
            return 20

    @staticmethod
    def _draw_dotted_line(draw, x1, y, x2, color=(190, 190, 190)):
        """Draw a horizontal dotted line from x1 to x2 at row y."""
        dash, gap = 7, 5
        x = x1
        while x < x2:
            draw.line([(x, y), (min(x + dash, x2), y)], fill=color, width=1)
            x += dash + gap

    # ------------------------------------------------------------------
    # Amount → words (Indian system)
    # ------------------------------------------------------------------
    @staticmethod
    def _num_to_words(n):
        try:
            n = int(float(str(n)))
        except (ValueError, TypeError):
            return str(n)
        if n == 0:
            return "Zero Only"
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
                'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen',
                'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens_w = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                  'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def below_100(m):
            if m < 20: return ones[m]
            return tens_w[m // 10] + (' ' + ones[m % 10] if ones[m % 10] else '')

        def below_1000(m):
            if m < 100: return below_100(m)
            r = below_100(m % 100)
            return ones[m // 100] + ' Hundred' + (' ' + r if r else '')

        parts = []
        if n >= 10000000:
            parts.append(below_1000(n // 10000000) + ' Crore'); n %= 10000000
        if n >= 100000:
            parts.append(below_1000(n // 100000) + ' Lakh'); n %= 100000
        if n >= 1000:
            parts.append(below_1000(n // 1000) + ' Thousand'); n %= 1000
        if n > 0:
            parts.append(below_1000(n))
        return ' '.join(parts) + ' Only'

    @staticmethod
    def _receipt_number():
        """8-digit receipt number: DDHHMMS (Day + Hour + Min + Sec)."""
        return datetime.now().strftime('%d%H%M%S')

    # ------------------------------------------------------------------
    # Draw one receipt half  — styled like the physical Kriyaban receipt
    # ------------------------------------------------------------------
    def _draw_receipt_half(self, draw, fonts, x0, y0, w, h, receipt_data, stamp_text):
        PAD = 26
        cx = x0 + w // 2

        body_h  = self._get_text_height(draw, fonts['body'])
        small_h = self._get_text_height(draw, fonts['small'])

        # ---- nested helper: field row with dotted extension ---------
        def draw_field(label, value, y_pos):
            lw = self._get_text_width(draw, label, fonts['body'])
            draw.text((x0 + PAD, y_pos), label, fill=self.TEXT_COLOR, font=fonts['body'])
            if value:
                draw.text((x0 + PAD + lw, y_pos), value,
                          fill=self.VALUE_COLOR, font=fonts['body_bold'])
                vw = self._get_text_width(draw, value, fonts['body_bold'])
            else:
                vw = 0
            line_x1 = x0 + PAD + lw + vw + (10 if value else 4)
            line_y  = y_pos + body_h + 4
            if line_x1 < x0 + w - PAD - 10:
                self._draw_dotted_line(draw, line_x1, line_y, x0 + w - PAD)
            return y_pos + body_h + 24
        # ---------------------------------------------------------------

        cy = y0 + PAD

        # ORIGINAL / COPY stamp (top-right)
        self._text_right(draw, x0 + w - PAD, cy, stamp_text, fonts['stamp'], self.STAMP_COLOR)

        # Org name — centred
        org_bb = draw.textbbox((0, 0), self.ORG_NAME, font=fonts['org_name'])
        org_w  = org_bb[2] - org_bb[0]
        org_h  = org_bb[3] - org_bb[1]
        draw.text((cx - org_w // 2, cy), self.ORG_NAME,
                  fill=self.HEADER_COLOR, font=fonts['org_name'])
        cy += org_h + 12

        # "RECEIPT" in a bordered box — centred
        r_txt  = "RECEIPT"
        r_bb   = draw.textbbox((0, 0), r_txt, font=fonts['receipt'])
        r_w, r_h = r_bb[2] - r_bb[0], r_bb[3] - r_bb[1]
        r_x    = cx - r_w // 2
        draw.rectangle([(r_x - 14, cy - 8), (r_x + r_w + 14, cy + r_h + 8)],
                       outline=self.HEADER_COLOR, width=2)
        draw.text((r_x, cy), r_txt, fill=self.HEADER_COLOR, font=fonts['receipt'])
        cy += r_h + 20

        # Divider
        draw.line([(x0 + PAD, cy), (x0 + w - PAD, cy)], fill=self.HEADER_COLOR, width=2)
        cy += 14

        # No. and Date row
        draw.text((x0 + PAD, cy), f"No.   {receipt_data['receipt_no']}",
                  fill=self.TEXT_COLOR, font=fonts['body'])
        self._text_right(draw, x0 + w - PAD, cy,
                         f"Date :   {receipt_data['date_str']}",
                         fonts['body'], self.TEXT_COLOR)
        cy += body_h + 14

        # Thick divider
        draw.line([(x0 + PAD, cy), (x0 + w - PAD, cy)], fill=self.HEADER_COLOR, width=2)
        cy += 22

        # ---- Field rows ----
        cy = draw_field("Received with thanks from :   ", receipt_data.get('name', ''), cy)
        cy = draw_field("for Level / Event :   ",         receipt_data.get('event', ''), cy)
        cy = draw_field("Rupees :   ", self._num_to_words(receipt_data.get('amount', 0)), cy)
        cy += 8

        # Payment / Cheque line
        payment = receipt_data.get('payment_method', '')
        if payment.lower() == 'cash':
            pay_txt = "by  Cash   /   vide Cheque / Draft / Pay Order No. ______________________"
        elif payment.lower() == 'online':
            pay_txt = "by  Online / UPI   /   vide Cheque / Draft / Pay Order No. ______________"
        else:
            pay_txt = "by  Cash / Online   /   vide Cheque / Draft / Pay Order No. _____________"
        draw.text((x0 + PAD, cy), pay_txt, fill=self.TEXT_COLOR, font=fonts['small'])
        cy += small_h + 8

        draw.text((x0 + PAD, cy),
                  "Drawn on _________________________________   Dated _____________________",
                  fill=self.TEXT_COLOR, font=fonts['small'])
        cy += small_h + 12

        # Optional details (phone / email / aadhar / pan / address)
        row1 = []
        if receipt_data.get('phone'):  row1.append(f"Phone: {receipt_data['phone']}")
        if receipt_data.get('email'):  row1.append(f"Email: {receipt_data['email']}")
        if receipt_data.get('aadhar'): row1.append(f"Aadhar: {receipt_data['aadhar']}")
        if row1:
            draw.text((x0 + PAD, cy), "   |   ".join(row1),
                      fill=(90, 90, 90), font=fonts['small'])
            cy += small_h + 6

        row2 = []
        if receipt_data.get('pan'):     row2.append(f"PAN: {receipt_data['pan']}")
        if receipt_data.get('address'): row2.append(f"Addr: {receipt_data['address']}")
        if row2:
            draw.text((x0 + PAD, cy), "   |   ".join(row2),
                      fill=(90, 90, 90), font=fonts['small'])
            cy += small_h + 6

        cy += 16

        # Divider before footer
        draw.line([(x0 + PAD, cy), (x0 + w - PAD, cy)], fill=self.ACCENT_COLOR, width=1)
        cy += 22

        # "For Kriyaban Meditation Sangha" (right-aligned)
        self._text_right(draw, x0 + w - PAD, cy,
                         f"For {self.ORG_NAME}", fonts['body'], self.TEXT_COLOR)
        cy += body_h + 40

        # Signature line + "Auth. Signatory"
        sig_end_x   = x0 + w - PAD
        sig_start_x = sig_end_x - 280
        draw.line([(sig_start_x, cy), (sig_end_x, cy)], fill=self.TEXT_COLOR, width=1)
        cy += 8
        self._text_right(draw, sig_end_x, cy, "Auth. Signatory", fonts['small'], self.TEXT_COLOR)

        # Rs. box — bottom right, anchored to bottom of receipt
        rs_box_h = 52
        rs_box_w = 195
        rs_box_x = x0 + w - PAD - rs_box_w
        rs_box_y = y0 + h - PAD - rs_box_h
        draw.rectangle([(rs_box_x, rs_box_y), (rs_box_x + rs_box_w, rs_box_y + rs_box_h)],
                       outline=self.TEXT_COLOR, width=2)
        rs_y = rs_box_y + (rs_box_h - body_h) // 2
        draw.text((rs_box_x + 10, rs_y), "Rs.", fill=self.TEXT_COLOR, font=fonts['body'])
        self._text_right(draw, rs_box_x + rs_box_w - 10, rs_y,
                         f"{receipt_data.get('amount', '')} /-",
                         fonts['body_bold'], self.VALUE_COLOR)

        # Outer border (drawn last so it's on top)
        draw.rectangle([(x0 + 2, y0 + 2), (x0 + w - 2, y0 + h - 2)],
                       outline=self.HEADER_COLOR, width=3)

    # ------------------------------------------------------------------
    # Build full A4 image  (Original on top, Copy on bottom)
    # ------------------------------------------------------------------
    def _build_a4_image(self, receipt_data, filename_prefix):
        try:
            margin = 38
            sep_h  = 64
            half_h = (self.A4_H - 2 * margin - sep_h) // 2
            receipt_w = self.A4_W - 2 * margin

            img  = Image.new("RGB", (self.A4_W, self.A4_H), self.BG_COLOR)
            draw = ImageDraw.Draw(img)
            fonts = self._load_fonts()

            # Top — ORIGINAL
            self._draw_receipt_half(draw, fonts, margin, margin,
                                    receipt_w, half_h, receipt_data, "ORIGINAL")

            # Dashed cut-line
            sep_y = margin + half_h + sep_h // 2
            dash, gap = 22, 10
            x = margin
            while x < self.A4_W - margin:
                draw.line([(x, sep_y), (min(x + dash, self.A4_W - margin), sep_y)],
                          fill=self.SEP_COLOR, width=2)
                x += dash + gap
            self._text_center(draw, self.A4_W // 2, sep_y - 18,
                              "- - - - - - - - - - - - -  cut here  - - - - - - - - - - - - -",
                              fonts["small"], self.SEP_COLOR)

            # Bottom — COPY
            y_bottom = margin + half_h + sep_h
            self._draw_receipt_half(draw, fonts, margin, y_bottom,
                                    receipt_w, half_h, receipt_data, "COPY")

            fname = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img_path = self.temp_dir / fname
            img.save(str(img_path), dpi=(150, 150))
            self.generated_images.append(img_path)
            return img_path
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Receipt generation error: {e}")
            return None

    # ------------------------------------------------------------------
    # Public receipt generators
    # ------------------------------------------------------------------
    def generate_donation_receipt(self, name, email, phone, amount,
                                  aadhar="", address="", pan="", receipt_no=None):
        data = {
            'receipt_no':     str(receipt_no) if receipt_no is not None else self._receipt_number(),
            'date_str':       datetime.now().strftime('%d/%m/%Y'),
            'name':           name,
            'event':          'Donation',
            'amount':         amount,
            'phone':          phone,
            'email':          email,
            'aadhar':         '',       # never printed — kept private
            'pan':            '',       # never printed — kept private
            'address':        address,
            'payment_method': '',
        }
        return self._build_a4_image(data, "donation")

    def generate_meditation_receipt(self, name, email, phone, referral_source,
                                    meditation_level, course_fee,
                                    aadhar="", address="", pan="", receipt_no=None):
        data = {
            'receipt_no':     str(receipt_no) if receipt_no is not None else self._receipt_number(),
            'date_str':       datetime.now().strftime('%d/%m/%Y'),
            'name':           name,
            'event':          meditation_level,
            'amount':         course_fee,
            'phone':          phone,
            'email':          email,
            'aadhar':         '',       # never printed — kept private
            'pan':            '',       # never printed — kept private
            'address':        address,
            'payment_method': '',
        }
        return self._build_a4_image(data, "meditation")

    def generate_boutique_receipt(self, item_name, price, payment_method, receipt_no=None):
        data = {
            'receipt_no':     str(receipt_no) if receipt_no is not None else self._receipt_number(),
            'date_str':       datetime.now().strftime('%d/%m/%Y'),
            'name':           '',
            'event':          item_name,
            'amount':         price,
            'phone':          '',
            'email':          '',
            'aadhar':         '',
            'pan':            '',
            'address':        '',
            'payment_method': payment_method,
        }
        return self._build_a4_image(data, "boutique")

    # ------------------------------------------------------------------
    # Printing
    # ------------------------------------------------------------------
    def print_receipt(self, image_path):
        """Send to default printer via Windows shell 'print' verb."""
        try:
            os.startfile(str(image_path), "print")
            return True
        except Exception as e:
            print(f"Print error: {e}")
            return False

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self):
        for img_path in list(self.generated_images):
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass
        self.generated_images.clear()
