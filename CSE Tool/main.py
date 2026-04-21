import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox, ttk
from validator import validate_excel
import os

# App Theme and Settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ValidationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Anchor AI | Validation Dashboard")
        self.geometry("1100x750")
        
        # Colors & Fonts
        self.primary_color = "#1a73e8"
        self.bg_color = "#f8f9fa"
        self.card_bg = "white"
        self.header_font = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.sub_font = ctk.CTkFont(family="Segoe UI", size=14)
        
        # Internal State
        self.df = None
        self.validated_df = None
        self.file_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#f0f2f5")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🛡️ Anchor AI", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.sep = ctk.CTkFrame(self.sidebar, height=2, fg_color="#dee2e6")
        self.sep.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Sidebar Buttons
        self.upload_btn = ctk.CTkButton(self.sidebar, text="Upload Excel", command=self.upload_file, 
                                      corner_radius=10, height=40, font=ctk.CTkFont(weight="bold"))
        self.upload_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.run_btn = ctk.CTkButton(self.sidebar, text="Run Validation", command=self.run_validation, 
                                   corner_radius=10, height=40, font=ctk.CTkFont(weight="bold"), 
                                   fg_color="#28a745", hover_color="#218838", state="disabled")
        self.run_btn.grid(row=3, column=0, padx=20, pady=10)
        
        self.export_btn = ctk.CTkButton(self.sidebar, text="Export Results", command=self.export_report, 
                                      corner_radius=10, height=40, font=ctk.CTkFont(weight="bold"),
                                      fg_color="#6c757d", hover_color="#5a6268", state="disabled")
        self.export_btn.grid(row=5, column=0, padx=20, pady=20)
        
        # File Info Area in Sidebar
        self.file_info_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.file_info_frame.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        self.file_status_label = ctk.CTkLabel(self.file_info_frame, text="No file selected", font=self.sub_font, 
                                            text_color="#6c757d", wraplength=200)
        self.file_status_label.pack(side="top", pady=10)
        
        # 2. Main Dashboard Area
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color=self.bg_color)
        self.main_view.grid(row=0, column=1, sticky="nsew")
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(2, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self.main_view, height=100, fg_color="white", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_title = ctk.CTkLabel(self.header, text="Validation Dashboard", font=self.header_font, 
                                       text_color=self.primary_color)
        self.header_title.pack(side="left", padx=30, pady=25)
        
        # Summary Area
        self.summary_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.summary_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        
        self.valid_card = self.create_summary_card(self.summary_frame, "Valid", "0", "#28a745", "✅")
        self.valid_card.pack(side="left", expand=True, padx=10)
        
        self.invalid_card = self.create_summary_card(self.summary_frame, "Invalid", "0", "#dc3545", "❌")
        self.invalid_card.pack(side="left", expand=True, padx=10)
        
        self.missing_card = self.create_summary_card(self.summary_frame, "Missing", "0", "#ffc107", "⚠️")
        self.missing_card.pack(side="left", expand=True, padx=10)
        
        # Table Area
        self.table_card = ctk.CTkFrame(self.main_view, fg_color="white", corner_radius=15)
        self.table_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 30))
        
        # Progress Bar (Hidden initially)
        self.progress_bar = ctk.CTkProgressBar(self.table_card, height=4, corner_radius=0)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", side="top", padx=15, pady=(15, 0))
        self.progress_bar.pack_forget() 
        
        # Treeview Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10), borderwidth=0, fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f8f9fa", foreground="#495057")
        style.map("Treeview", background=[('selected', '#e8f0fe')], foreground=[('selected', '#1a73e8')])
        
        self.tree = ttk.Treeview(self.table_card, columns=("Question", "Answer", "Status", "Category", "Reason"), 
                                show="headings")
        
        for col in ("Question", "Answer", "Status", "Category", "Reason"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="w")
            
        self.tree.tag_configure("Valid", foreground="#28a745")
        self.tree.tag_configure("Invalid", foreground="#dc3545")
        self.tree.tag_configure("Missing", foreground="#856404")
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(15,0), pady=15)
        self.scrollbar.pack(side="right", fill="y", pady=15, padx=(0, 15))
        
    def create_summary_card(self, parent, title, value, color, icon):
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="white", height=120)
        card.pack_propagate(False) # Keep height fixed
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True)
        
        icon_lbl = ctk.CTkLabel(content, text=icon, font=ctk.CTkFont(size=24))
        icon_lbl.pack()
        
        value_lbl = ctk.CTkLabel(content, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
        value_lbl.pack()
        
        title_lbl = ctk.CTkLabel(content, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6c757d")
        title_lbl.pack()
        
        setattr(self, f"{title.lower()}_val_lbl", value_lbl)
        return card

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if self.file_path:
            try:
                self.file_status_label.configure(text=f"📂 {os.path.basename(self.file_path)}", text_color=self.primary_color)
                self.df = pd.read_excel(self.file_path)
                
                required = ["Question", "Answer"]
                if not all(col in self.df.columns for col in required):
                    messagebox.showerror("Error", f"Excel must contain columns: {', '.join(required)}")
                    return
                
                self.run_btn.configure(state="normal")
                self.update_table(self.df)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def run_validation(self):
        if self.df is not None:
            self.progress_bar.pack(fill="x", side="top", padx=15, pady=(15, 0))
            self.progress_bar.start()
            self.update() 
            
            try:
                self.validated_df = validate_excel(self.df)
                self.update_table(self.validated_df)
                self.update_summary()
                
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.export_btn.configure(state="normal", fg_color=self.primary_color)
                
            except Exception as e:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                messagebox.showerror("Error", f"Validation failed: {str(e)}")

    def update_table(self, df):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for _, row in df.iterrows():
            status = row.get('Status', '')
            values = [str(row.get(col, '')) for col in ("Question", "Answer", "Status", "Category", "Reason")]
            self.tree.insert("", "end", values=values, tags=(status,))
            
        self.resize_columns()

    def resize_columns(self):
        for col in self.tree["columns"]:
            # Better approximation for column width
            max_w = 150
            for item in self.tree.get_children():
                val = str(self.tree.set(item, col))
                w = len(val) * 9
                if w > max_w: max_w = w
            
            max_w = min(max_w, 400)
            self.tree.column(col, width=max_w)

    def update_summary(self):
        if self.validated_df is not None:
            counts = self.validated_df['Status'].value_counts()
            self.valid_val_lbl.configure(text=str(counts.get('Valid', 0)))
            self.invalid_val_lbl.configure(text=str(counts.get('Invalid', 0)))
            self.missing_val_lbl.configure(text=str(counts.get('Missing', 0)))

    def export_report(self):
        if self.validated_df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                    filetypes=[("Excel files", "*.xlsx")])
            if save_path:
                try:
                    self.validated_df.to_excel(save_path, index=False)
                    messagebox.showinfo("Success", f"Report exported successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export: {str(e)}")

if __name__ == "__main__":
    app = ValidationApp()
    app.mainloop()
