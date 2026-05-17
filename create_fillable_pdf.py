"""
Generate a fillable PDF for Culver City Surgical Patient Intake Form.
Matches the HTML design with bilingual EN/ES labels and all fields.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ----- Brand colors -----
PELOROUS = HexColor("#4bbec6")
PELOROUS_DARKER = HexColor("#1e4c4f")
TAN = HexColor("#d4af8a")
SPRING_WOOD = HexColor("#f9f7f4")
NEUTRAL_DARK = HexColor("#4d4e4f")
NEUTRAL_DARKEST = HexColor("#020304")
BORDER_LIGHT = HexColor("#cccccc")

# ----- Page setup -----
PAGE_W, PAGE_H = letter  # 612 x 792 pts
MARGIN_L = 0.4 * inch
MARGIN_R = 0.4 * inch
MARGIN_T = 0.4 * inch
MARGIN_B = 0.4 * inch
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# ----- Font registration (try real fonts, fall back to Helvetica) -----
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "Design System", "fonts")
DISPLAY_FONT = "Helvetica-Bold"
DISPLAY_ITALIC = "Helvetica-Oblique"
BODY_FONT = "Helvetica"
BODY_BOLD = "Helvetica-Bold"

OUTPUT_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "CCS-Patient-Intake-Fillable.pdf")


class PDFBuilder:
    def __init__(self, output):
        self.c = canvas.Canvas(output, pagesize=letter)
        self.c.setTitle("Culver City Surgical — Patient Intake Form")
        self.y = PAGE_H - MARGIN_T
        self.page_num = 1
        self.field_counter = 0

    def new_field_name(self, base):
        self.field_counter += 1
        return f"{base}_{self.field_counter}"

    def check_page_break(self, needed_height):
        if self.y - needed_height < MARGIN_B + 20:
            self.c.showPage()
            self.page_num += 1
            self.y = PAGE_H - MARGIN_T
            return True
        return False

    # ---------- Header ----------
    def draw_header(self):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "Design System", "assets", "logo",
                                 "culver-city-logo.png")
        if os.path.exists(logo_path):
            try:
                self.c.drawImage(logo_path, MARGIN_L, self.y - 50,
                                 width=130, height=50, mask='auto',
                                 preserveAspectRatio=True)
            except Exception:
                pass

        # Title centered
        self.c.setFillColor(PELOROUS_DARKER)
        self.c.setFont(DISPLAY_FONT, 18)
        title = "Patient Intake Form"
        tw = self.c.stringWidth(title, DISPLAY_FONT, 18)
        self.c.drawString((PAGE_W - tw) / 2, self.y - 20, title)

        self.c.setFillColor(TAN)
        self.c.setFont(DISPLAY_ITALIC, 11)
        sub = "Formulario de Admisión del Paciente"
        sw = self.c.stringWidth(sub, DISPLAY_ITALIC, 11)
        self.c.drawString((PAGE_W - sw) / 2, self.y - 35, sub)

        # Right contact
        self.c.setFillColor(NEUTRAL_DARK)
        self.c.setFont(BODY_BOLD, 8)
        right_x = PAGE_W - MARGIN_R
        contact = ["Culver City Surgical", "3831 Hughes Ave # 702",
                   "Culver City, CA 90232", "(310) 837-3834"]
        for i, line in enumerate(contact):
            font = BODY_BOLD if i == 0 else BODY_FONT
            self.c.setFont(font, 8)
            cw = self.c.stringWidth(line, font, 8)
            self.c.drawString(right_x - cw, self.y - 15 - i * 10, line)

        # Teal underline
        self.y -= 60
        self.c.setStrokeColor(PELOROUS)
        self.c.setLineWidth(1.5)
        self.c.line(MARGIN_L, self.y, PAGE_W - MARGIN_R, self.y)
        self.y -= 10

    # ---------- Section ----------
    def draw_section(self, en, es):
        self.check_page_break(40)
        self.y -= 6
        self.c.setFillColor(PELOROUS_DARKER)
        self.c.setFont(DISPLAY_FONT, 12)
        self.c.drawString(MARGIN_L, self.y - 12, f"{en} / {es}")
        self.y -= 16
        self.c.setStrokeColor(BORDER_LIGHT)
        self.c.setLineWidth(0.5)
        self.c.line(MARGIN_L, self.y, PAGE_W - MARGIN_R, self.y)
        self.y -= 4

    # ---------- Field row ----------
    def draw_field_row(self, fields):
        """fields = [(label_en, label_es, field_type), ...] up to 3 per row."""
        n = len(fields)
        if n == 0:
            return
        gap = 6
        col_w = (CONTENT_W - gap * (n - 1)) / n
        row_h = 30
        self.check_page_break(row_h + 5)

        for i, (en, es, ftype) in enumerate(fields):
            x = MARGIN_L + i * (col_w + gap)
            # Label
            self.c.setFillColor(NEUTRAL_DARKEST)
            self.c.setFont(BODY_BOLD, 7)
            label = f"{en} / {es}".upper()
            # Truncate if too long
            max_chars = int(col_w / 3.2)
            if len(label) > max_chars:
                label = label[:max_chars - 1] + "…"
            self.c.drawString(x, self.y - 8, label)

            # Field
            field_y = self.y - 24
            field_h = 14
            field_name = self.new_field_name(self._slug(en))
            self.c.setFillColor(SPRING_WOOD)
            self.c.setStrokeColor(BORDER_LIGHT)
            self.c.rect(x, field_y, col_w, field_h, stroke=0, fill=1)

            self.c.acroForm.textfield(
                name=field_name,
                tooltip=f"{en} / {es}",
                x=x, y=field_y, width=col_w, height=field_h,
                borderStyle='solid',
                borderColor=BORDER_LIGHT,
                fillColor=SPRING_WOOD,
                textColor=NEUTRAL_DARKEST,
                forceBorder=True,
                fontSize=9,
            )
        self.y -= row_h

    def draw_full_field(self, en, es):
        self.check_page_break(35)
        self.c.setFillColor(NEUTRAL_DARKEST)
        self.c.setFont(BODY_BOLD, 7)
        self.c.drawString(MARGIN_L, self.y - 8, f"{en} / {es}".upper())
        field_y = self.y - 24
        field_h = 14
        name = self.new_field_name(self._slug(en))
        self.c.acroForm.textfield(
            name=name, tooltip=f"{en} / {es}",
            x=MARGIN_L, y=field_y, width=CONTENT_W, height=field_h,
            borderStyle='solid', borderColor=BORDER_LIGHT,
            fillColor=SPRING_WOOD, textColor=NEUTRAL_DARKEST,
            forceBorder=True, fontSize=9,
        )
        self.y -= 30

    def draw_checkboxes(self, items, columns=4):
        """items = list of (en, es) labels."""
        col_w = CONTENT_W / columns
        rows = (len(items) + columns - 1) // columns
        for r in range(rows):
            self.check_page_break(16)
            for c_idx in range(columns):
                idx = r * columns + c_idx
                if idx >= len(items):
                    break
                en, es = items[idx]
                x = MARGIN_L + c_idx * col_w
                name = self.new_field_name("chk_" + self._slug(en))
                self.c.acroForm.checkbox(
                    name=name, tooltip=f"{en} / {es}",
                    x=x, y=self.y - 11, size=9,
                    borderColor=PELOROUS, fillColor=white,
                    textColor=PELOROUS_DARKER,
                )
                self.c.setFillColor(NEUTRAL_DARKEST)
                self.c.setFont(BODY_FONT, 8)
                lbl = f"{en} / {es}"
                if len(lbl) > 22:
                    lbl = lbl[:21] + "…"
                self.c.drawString(x + 12, self.y - 9, lbl)
            self.y -= 14

    def draw_table(self, headers, rows):
        """Medications-style table."""
        n_cols = len(headers)
        col_w = CONTENT_W / n_cols
        # Header
        self.check_page_break(20 + rows * 16)
        self.c.setFillColor(PELOROUS_DARKER)
        self.c.rect(MARGIN_L, self.y - 14, CONTENT_W, 14, stroke=0, fill=1)
        self.c.setFillColor(white)
        self.c.setFont(BODY_BOLD, 8)
        for i, h in enumerate(headers):
            self.c.drawString(MARGIN_L + i * col_w + 4, self.y - 10, h)
        self.y -= 14
        # Body rows
        for r in range(rows):
            for i in range(n_cols):
                x = MARGIN_L + i * col_w
                self.c.setStrokeColor(BORDER_LIGHT)
                self.c.setFillColor(SPRING_WOOD)
                self.c.rect(x, self.y - 14, col_w, 14, stroke=1, fill=1)
                name = self.new_field_name(f"tblcell_{r}_{i}")
                self.c.acroForm.textfield(
                    name=name, tooltip=headers[i],
                    x=x + 1, y=self.y - 13, width=col_w - 2, height=12,
                    borderStyle='solid', borderColor=SPRING_WOOD,
                    fillColor=SPRING_WOOD, textColor=NEUTRAL_DARKEST,
                    forceBorder=False, fontSize=8,
                )
            self.y -= 14

    def draw_signature_pair(self):
        self.check_page_break(40)
        gap = 20
        w = (CONTENT_W - gap) / 2
        # signature
        name1 = self.new_field_name("signature")
        self.c.acroForm.textfield(
            name=name1, tooltip="Patient Signature",
            x=MARGIN_L, y=self.y - 18, width=w, height=18,
            borderStyle='underlined', borderColor=NEUTRAL_DARKEST,
            fillColor=white, forceBorder=True, fontSize=10,
        )
        self.c.setFillColor(NEUTRAL_DARK)
        self.c.setFont(BODY_FONT, 7)
        self.c.drawCentredString(MARGIN_L + w / 2, self.y - 28,
                                 "Patient Signature / Firma del Paciente")
        # date
        x2 = MARGIN_L + w + gap
        name2 = self.new_field_name("date")
        self.c.acroForm.textfield(
            name=name2, tooltip="Date",
            x=x2, y=self.y - 18, width=w, height=18,
            borderStyle='underlined', borderColor=NEUTRAL_DARKEST,
            fillColor=white, forceBorder=True, fontSize=10,
        )
        self.c.drawCentredString(x2 + w / 2, self.y - 28, "Date / Fecha")
        self.y -= 40

    def draw_paragraph(self, text, font=BODY_FONT, size=8, color=NEUTRAL_DARK,
                       line_height=10):
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        words = text.split()
        line, lines = [], []
        max_w = CONTENT_W
        for w_ in words:
            test = " ".join(line + [w_])
            if self.c.stringWidth(test, font, size) > max_w:
                lines.append(" ".join(line))
                line = [w_]
            else:
                line.append(w_)
        if line:
            lines.append(" ".join(line))
        for ln in lines:
            self.check_page_break(line_height + 2)
            self.c.drawString(MARGIN_L, self.y - 8, ln)
            self.y -= line_height

    @staticmethod
    def _slug(s):
        return ''.join(ch.lower() if ch.isalnum() else '_' for ch in s)[:40]

    def save(self):
        self.c.save()


def build():
    p = PDFBuilder(OUTPUT_PDF)
    p.draw_header()

    # Personal Information
    p.draw_section("Personal Information", "Información Personal")
    p.draw_field_row([
        ("Name", "Nombre (Last, First, Middle)", "text"),
        ("Date of Birth", "Fecha de nacimiento", "date"),
    ])
    p.draw_field_row([
        ("Sex", "Sexo", "text"),
        ("Age", "Edad", "text"),
        ("Marital Status", "Estado civil", "text"),
    ])
    p.draw_full_field("Home Address", "Dirección")
    p.draw_field_row([
        ("Cell Phone", "Teléfono celular", "text"),
        ("Email", "Correo electrónico", "text"),
        ("Social Security", "Seguro Social", "text"),
    ])
    p.draw_field_row([
        ("Preferred Language", "Idioma Preferido", "text"),
    ])

    # Employment
    p.draw_section("Employment", "Empleo")
    p.draw_field_row([
        ("Occupation", "Ocupación", "text"),
        ("Employer", "Nombre del empleador", "text"),
        ("Work Phone", "Teléfono de trabajo", "text"),
    ])
    p.draw_full_field("Work Address", "Dirección de empleador")

    # Emergency Contact
    p.draw_section("Emergency Contact", "Contacto de Emergencia")
    p.draw_field_row([
        ("Name", "Nombre", "text"),
        ("Relationship", "Relación", "text"),
        ("Phone", "Teléfono", "text"),
    ])

    # Insurance
    p.draw_section("Insurance", "Seguro")
    p.draw_field_row([
        ("Insurance", "Seguro", "text"),
        ("Name of Insured", "Nombre del asegurado", "text"),
    ])
    p.draw_field_row([
        ("Insured SSN", "Seguro Social", "text"),
        ("Insured DOB", "Fecha de nacimiento", "text"),
        ("Relationship to Insured", "Relación con el Asegurado", "text"),
    ])
    p.draw_field_row([
        ("Primary Doctor", "Doctor de cabecera", "text"),
        ("Referred By", "Referido por", "text"),
    ])

    # Assignment of Benefits
    p.draw_section("Assignment of Benefits", "Asignación de Beneficios")
    p.draw_paragraph(
        "I hereby irrevocably assign the insurance benefit payment, both basic and major medical, to which I am entitled to the doctor rendering service. I understand that I am financially responsible for the charges not covered by the assignment. I authorize the doctor rendering service to release information required in the course of my examination."
    )
    p.draw_paragraph(
        "Por la presente asigno irrevocablemente el pago de prestaciones de seguro, tanto básico como médico importante, al médico que presta el servicio. Entiendo que soy financieramente responsable de los cargos no cubiertos por la asignación. Autorizo al médico que presta el servicio a divulgar la información requerida durante mi examen.",
        font=DISPLAY_ITALIC,
    )
    p.draw_signature_pair()

    # Medications
    p.draw_section("Current Medications", "Medicamentos Actuales")
    p.draw_table(
        ["Prescription", "Dose/Frequency", "OTC/Vitamins", "Dose/Frequency"],
        rows=6,
    )

    # Vital Signs
    p.draw_section("Vital Signs", "Signos Vitales")
    p.draw_field_row([
        ("Height", "Estatura", "text"),
        ("Weight", "Peso", "text"),
    ])

    # Allergies
    p.draw_section("Allergies", "Alergias")
    p.draw_checkboxes([
        ("No allergies", "No alergias"),
        ("Penicillin", "Penicilina"),
        ("Sulfa", "Sulfa"),
        ("Aspirin", "Aspirina"),
        ("Iodine", "Yodo"),
        ("Latex", "Látex"),
        ("Soy", "Soya"),
        ("Eggs", "Huevos"),
        ("Other", "Otra"),
    ], columns=4)
    p.draw_full_field("If allergies, describe reactions",
                      "Si tiene alergias, describa reacciones")

    # Medical History
    p.draw_section("Medical History", "Historia Médica")
    p.draw_checkboxes([
        ("Acid reflux", "Reflujo"),
        ("Anemia", "Anemia"),
        ("Arthritis", "Artritis"),
        ("Asthma", "Asma"),
        ("Bleeding disorder", "Trast. hemorrág."),
        ("Blood clots", "Coágulos"),
        ("Blood transfusion", "Transfusión"),
        ("Cancer", "Cáncer"),
        ("Chest pain", "Dolor torácico"),
        ("Chronic anxiety", "Ansiedad crónica"),
        ("Chronic cough", "Tos crónica"),
        ("Chronic lung disease", "Enf. pulm. crón."),
        ("Chronic sinusitis", "Sinusitis crón."),
        ("Cirrhosis", "Cirrosis"),
        ("Colon cancer", "Cáncer de colon"),
        ("Colon polyps", "Pólipos"),
        ("Crohn's disease", "Crohn"),
        ("Diabetes", "Diabetes"),
        ("Diverticulitis", "Diverticulitis"),
        ("Emphysema", "Enfisema"),
        ("Glaucoma", "Glaucoma"),
        ("Gout", "Gota"),
        ("Heart attack", "Ataque cardíaco"),
        ("Heart failure", "Insuf. cardíaca"),
        ("Heart murmur", "Soplo cardíaco"),
        ("Hepatitis", "Hepatitis"),
        ("Hernia", "Hernia"),
        ("High blood pressure", "Hipertensión"),
        ("HIV or AIDS", "VIH"),
        ("Irregular heartbeat", "Arritmia"),
        ("Irritable bowel", "Intestino irrit."),
        ("Kidney disease", "Enf. renal"),
        ("Kidney infection", "Infección renal"),
        ("Kidney stones", "Cálculos renales"),
        ("Liver disease", "Enf. hepática"),
        ("Lupus", "Lupus"),
        ("Multiple sclerosis", "Esclerosis múlt."),
        ("Pancreatitis", "Pancreatitis"),
        ("Parkinson's", "Parkinson"),
        ("Phlebitis", "Flebitis"),
        ("Polio", "Polio"),
        ("Radiation therapy", "Radioterapia"),
        ("Seizures", "Convulsiones"),
        ("Sleep apnea", "Apnea del sueño"),
        ("Stroke", "Accidente cereb."),
        ("Thyroid disease", "Tiroides"),
        ("Tuberculosis", "Tuberculosis"),
        ("Ulcerative colitis", "Colitis ulcer."),
        ("Other", "Otro"),
    ], columns=4)
    p.draw_full_field("Other conditions or comments",
                      "Otras condiciones o comentarios")

    # Serious Illnesses & Injuries
    p.draw_section("Serious Illnesses & Injuries",
                   "Enfermedades y Lesiones Graves")
    p.draw_table(
        ["Name / Nombre", "Date / Fecha", "Outcome / Resultado"],
        rows=4,
    )

    # Health Habits
    p.draw_section("Health Habits", "Hábitos de Salud")
    p.draw_full_field("Caffeine", "Cafeína")
    p.draw_full_field("Tobacco", "Tabaco")
    p.draw_full_field("Alcohol Use", "Uso de Alcohol")
    p.draw_full_field("Drugs (cocaine, marijuana, etc.)",
                      "Drogas (cocaína, marihuana, etc.)")

    # Hospitalizations
    p.draw_section("Hospitalizations", "Hospitalizaciones")
    p.draw_table(
        ["Date / Fecha", "Hospital", "Reason & Outcome / Razón y Resultado"],
        rows=4,
    )

    # HIPAA / Consent Acknowledgement
    p.draw_section("Patient Consent & Privacy Acknowledgement",
                   "Consentimiento del Paciente y Aviso de Privacidad")
    p.draw_paragraph(
        "I acknowledge receipt of the Notice of Privacy Practices and consent to the use and disclosure of my health information for treatment, payment, and healthcare operations. As a patient or legal guardian, I agree to pay for all services rendered and verify that the information on this form is true and correct."
    )
    p.draw_paragraph(
        "Reconozco haber recibido el Aviso de Prácticas de Privacidad y consiento al uso y divulgación de mi información médica para tratamiento, pago y operaciones de atención médica. Como paciente o tutor legal, acepto pagar todos los servicios prestados y verifico que la información de este formulario es verdadera y correcta.",
        font=DISPLAY_ITALIC,
    )
    p.draw_full_field("Restrictions requested, if any",
                      "Restricciones solicitadas, si hay")
    p.draw_signature_pair()

    p.save()
    print(f"Created: {OUTPUT_PDF}")


if __name__ == "__main__":
    build()
