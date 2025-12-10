"""
Main Application Entry Point

Connects GUI and API modules
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from datetime import datetime

# Import modules
from gui import AITalentMatcher
from api_evaluator import CVEvaluator
from pdf_generator import PDFReportGenerator


class TalentMatcherApp:
    def __init__(self):
        """Initialize the main application"""

        # Initialize PDF generator
        self.pdf_generator = PDFReportGenerator()

        # Create GUI with callbacks
        self.gui = AITalentMatcher(
            on_evaluate_callback=self.evaluate_candidates,
            on_download_callback=self.download_report,
        )

        # Store latest report data
        self.latest_report_data = None
        self.latest_report_file = None
        self.latest_pdf_file = None

    def evaluate_candidates(self, form_data):
        """
        Handle candidate evaluation request from GUI

        Args:
            form_data: Dictionary with job details and file paths

        Returns:
            Path to generated report file
        """
        try:
            api_key = form_data.get("api_key", "").strip()
            if not api_key:
                raise ValueError("DeepSeek API key is missing.")

            # Read job description if provided
            job_description = None
            if form_data.get("job_description_file"):
                try:
                    with open(
                        form_data["job_description_file"],
                        "r",
                        encoding="utf-8",
                    ) as f:
                        job_description = f.read()
                except Exception:
                    print("Note: Could not read job description file")

            # Initialize evaluator with API key
            evaluator = CVEvaluator(
                api_key=api_key,
                job_description=job_description,
            )

            # Run evaluation
            print("\nStarting evaluation...")
            report_data = evaluator.evaluate_candidates(
                cv_files=form_data["resume_files"],
                job_title=form_data["job_title"],
                company=form_data["company"],
                department=form_data.get("department", "Department"),
                location=form_data.get("location", ""),
                work_mode="",
            )

            # Save JSON report
            report_file = "evaluation_report.json"
            evaluator.save_json_report(report_data, report_file)

            # Generate PDF report
            print("\n→ Generating PDF report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"evaluation_report_{timestamp}.pdf"
            pdf_path = self.pdf_generator.generate_pdf(report_data, pdf_filename)

            # Store for later use
            self.latest_report_data = report_data
            self.latest_report_file = report_file
            self.latest_pdf_file = pdf_path

            print("✅ Evaluation complete!")
            print(f"✅ PDF Report: {pdf_path}")

            return report_file

        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            import traceback

            traceback.print_exc()
            raise

    def download_report(self, report_file):
        """
        Handle report download request from GUI

        Args:
            report_file: Path to the JSON report file
        """
        try:
            # Download PDF only
            if not self.latest_pdf_file or not os.path.exists(self.latest_pdf_file):
                messagebox.showerror("Error", "PDF report not found")
                return

            # Ask user where to save the PDF
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="talent_evaluation_report.pdf",
            )

            if save_path:
                # Copy PDF to selected location
                shutil.copy(self.latest_pdf_file, save_path)
                print(f"✅ PDF saved to: {save_path}")

                # Ask if user wants to open it
                if messagebox.askyesno(
                    "Open PDF", "Do you want to open the PDF report?"
                ):
                    try:
                        if os.name == "nt":  # Windows
                            os.startfile(save_path)
                        else:  # Mac/Linux
                            import subprocess

                            subprocess.call(
                                [
                                    "open"
                                    if os.name == "darwin"
                                    else "xdg-open",
                                    save_path,
                                ]
                            )
                    except Exception:
                        print("Could not auto-open PDF")

                messagebox.showinfo(
                    "Success", f"PDF Report saved to:\n{save_path}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")
            print(f"❌ Download error: {e}")

    def run(self):
        """Start the application"""
        print("=" * 60)
        print("AI Talent Matcher - Powered by DeepSeek")
        print("=" * 60)
        print("\n✓ GUI initialized")
        print("✓ API module loaded")
        print("✓ PDF generator loaded")
        print("\nStarting application...\n")

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Run GUI
        self.gui.mainloop()


if __name__ == "__main__":
    app = TalentMatcherApp()
    app.run()
