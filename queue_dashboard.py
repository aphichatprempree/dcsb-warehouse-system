import customtkinter as ctk
import datetime as dt
import sqlite3
import json
import pyttsx3
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DB_PATH = "desktop_queue_system.db"

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS queue_config (
                id INTEGER PRIMARY KEY,
                current_queue INTEGER DEFAULT 1,
                active_queues TEXT,
                nicknames TEXT,
                custom_names TEXT,
                updated_by TEXT
            )
        """)
        row = con.execute("SELECT id FROM queue_config WHERE id=1").fetchone()
        if not row:
            init_data = {
                "current_queue": 1,
                "active_queues": json.dumps({1:True, 2:True, 3:True, 4:True, 5:True}),
                "nicknames": json.dumps({1:"", 2:"", 3:"", 4:"", 5:""}),
                "custom_names": json.dumps({}),
                "updated_by": "System Init"
            }
            con.execute("""
                INSERT INTO queue_config (id, current_queue, active_queues, nicknames, custom_names, updated_by)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (init_data["current_queue"], init_data["active_queues"], init_data["nicknames"], init_data["custom_names"], init_data["updated_by"]))

init_db()

def get_db_data():
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute("SELECT current_queue, active_queues, nicknames, custom_names, updated_by FROM queue_config WHERE id=1").fetchone()
        if row:
            return {
                "current_queue": row[0],
                "active_queues": json.loads(row[1]),
                "nicknames": json.loads(row[2]),
                "custom_names": json.loads(row[3]),
                "updated_by": row[4]
            }
        return None

def save_db_data(data, editor):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            UPDATE queue_config
            SET current_queue=?, active_queues=?, nicknames=?, custom_names=?, updated_by=?
            WHERE id=1
        """, (data["current_queue"], json.dumps(data["active_queues"]), json.dumps(data["nicknames"]), json.dumps(data["custom_names"]), editor))

def speak_queue_text(text):
    def run_speech():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 145)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("Audio error:", e)
    threading.Thread(target=run_speech, daemon=True).start()

class DCSBDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DATA ENTRY (DCSB) - Desktop Queue & Expiry System")
        self.geometry("1200x750")
        self.minsize(1050, 680)

        self.DEFAULT_QUEUES = {
            1: {"name": "SAHAPAT", "readAs": "ขอเชิญคิวที่ 1, บริษัท สหพัฒน์"},
            2: {"name": "DKSH", "readAs": "ขอเชิญคิวที่ 2, บริษัท ดีเคเอสเอช"},
            3: {"name": "CROSSDOCK", "readAs": "ขอเชิญคิวที่ 3, บริษัท ครอสคอร์ส"},
            4: {"name": "PEPSI", "readAs": "ขอเชิญคิวที่ 4, บริษัท เป๊ปซี่"},
            5: {"name": "SINO", "readAs": "ขอเชิญคิวที่ 5, บริษัท ชิโน"}
        }

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ฝั่งซ้าย
        self.left_frame = ctk.CTkFrame(self, width=380, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.left_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self.left_frame, text="📦 คำนวณอายุสินค้า (DCSB)", font=ctk.CTkFont(family="Prompt", size=16, weight="bold")).pack(pady=(15, 10))

        self.calc_mode_var = ctk.StringVar(value="minmax")
        mode_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkRadioButton(mode_frame, text="ตรวจสอบเกณฑ์ Min/Max", variable=self.calc_mode_var, value="minmax", font=ctk.CTkFont(family="Prompt", size=12)).pack(side="left", expand=True)
        ctk.CTkRadioButton(mode_frame, text="คำนวณ Product Life", variable=self.calc_mode_var, value="prolife", font=ctk.CTkFont(family="Prompt", size=12)).pack(side="right", expand=True)

        self.minmax_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.minmax_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(self.minmax_frame, text="วันหมดอายุจริง (Target Expire Date):", font=ctk.CTkFont(family="Prompt", size=12)).pack(anchor="w", pady=2)
        
        # แก้ไขจุดนี้เป็น placeholder_text เรียบร้อยแล้ว
        self.target_date_entry = ctk.CTkEntry(self.minmax_frame, placeholder_text="YYYY-MM-DD", font=ctk.CTkFont(family="Prompt", size=12))
        self.target_date_entry.insert(0, dt.date.today().strftime('%Y-%m-%d'))
        self.target_date_entry.pack(fill="x", pady=2)

        ctk.CTkLabel(self.minmax_frame, text="MIN Days / MAX Days:", font=ctk.CTkFont(family="Prompt", size=12)).pack(anchor="w", pady=(8, 2))
        minmax_inputs = ctk.CTkFrame(self.minmax_frame, fg_color="transparent")
        minmax_inputs.pack(fill="x", pady=2)
        self.min_days_entry = ctk.CTkEntry(minmax_inputs, width=130, font=ctk.CTkFont(family="Prompt", size=12))
        self.min_days_entry.insert(0, "730")
        self.min_days_entry.pack(side="left")
        self.max_days_entry = ctk.CTkEntry(minmax_inputs, width=130, font=ctk.CTkFont(family="Prompt", size=12))
        self.max_days_entry.insert(0, "1095")
        self.max_days_entry.pack(side="right")

        self.calc_btn = ctk.CTkButton(self.minmax_frame, text="🔍 ตรวจสอบเกณฑ์อายุสินค้า", command=self.run_expiry_check, font=ctk.CTkFont(family="Prompt", size=13, weight="bold"), fg_color="#4F46E5", hover_color="#4338CA")
        self.calc_btn.pack(fill="x", pady=(15, 5))

        self.result_box = ctk.CTkTextbox(self.minmax_frame, height=110, font=ctk.CTkFont(family="Prompt", size=12))
        self.result_box.pack(fill="x", pady=5)
        self.result_box.insert("0.0", "ผลลัพธ์การตรวจสอบจะแสดงที่นี่...")
        self.result_box.configure(state="disabled")

        # ฝั่งขวา
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.right_frame.grid_rowconfigure(3, weight=1)

        top_bar = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top_bar, text="📢 Dashboard ระบบรันคิว (DCSB)", font=ctk.CTkFont(family="Prompt", size=18, weight="bold")).pack(side="left")
        
        user_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        user_frame.pack(side="right")
        ctk.CTkLabel(user_frame, text="ผู้ใช้งาน:", font=ctk.CTkFont(family="Prompt", size=12)).pack(side="left", padx=5)
        self.username_entry = ctk.CTkEntry(user_frame, width=110, font=ctk.CTkFont(family="Prompt", size=12))
        self.username_entry.insert(0, "เจ้าหน้าที่ 1")
        self.username_entry.pack(side="left")

        self.current_q_frame = ctk.CTkFrame(self.right_frame, corner_radius=12, fg_color=("#3B82F6", "#1E3A8A"))
        self.current_q_frame.pack(fill="x", padx=20, pady=10)

        self.curr_title_lbl = ctk.CTkLabel(self.current_q_frame, text="กำลังเรียกคิวปัจจุบัน", font=ctk.CTkFont(family="Prompt", size=12, weight="bold"), text_color="#E0E7FF")
        self.curr_title_lbl.pack(pady=(10, 0))
        self.curr_num_lbl = ctk.CTkLabel(self.current_q_frame, text="#1", font=ctk.CTkFont(family="Prompt", size=48, weight="bold"), text_color="#FFFFFF")
        self.curr_num_lbl.pack(pady=0)
        self.curr_name_lbl = ctk.CTkLabel(self.current_q_frame, text="SAHAPAT", font=ctk.CTkFont(family="Prompt", size=20, weight="bold"), text_color="#FFFFFF")
        self.curr_name_lbl.pack(pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(ctrl_frame, text="➖ ลดคิว", command=lambda: self.change_queue(-1), font=ctk.CTkFont(family="Prompt", size=13, weight="bold"), width=150, fg_color="#64748B", hover_color="#475569").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(ctrl_frame, text="🔄 รีเซ็ตคิว", command=self.reset_queue, font=ctk.CTkFont(family="Prompt", size=13, weight="bold"), width=150, fg_color="#D97706", hover_color="#B45309").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(ctrl_frame, text="⏩ ผ่าน / เพิ่มคิวถัดไป", command=lambda: self.change_queue(1), font=ctk.CTkFont(family="Prompt", size=13, weight="bold"), width=180, fg_color="#059669", hover_color="#047857").pack(side="left", expand=True, padx=5)

        self.grid_cards_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.grid_cards_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.grid_cards_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.grid_cards_frame.grid_rowconfigure(0, weight=1)

        self.card_widgets = {}
        for i in range(1, 6):
            c_frame = ctk.CTkFrame(self.grid_cards_frame, corner_radius=10, border_width=1, border_color="#CBD5E1")
            c_frame.grid(row=0, column=i-1, sticky="nsew", padx=4, pady=4)
            
            lbl_num = ctk.CTkLabel(c_frame, text=f"#{i}", font=ctk.CTkFont(family="Prompt", size=14, weight="bold"))
            lbl_num.pack(pady=(8, 2))
            lbl_name = ctk.CTkLabel(c_frame, text="-", font=ctk.CTkFont(family="Prompt", size=13, weight="bold"))
            lbl_name.pack(pady=2)
            lbl_status = ctk.CTkLabel(c_frame, text="รอ", font=ctk.CTkFont(family="Prompt", size=11))
            lbl_status.pack(pady=2)

            btn_toggle = ctk.CTkButton(c_frame, text="เปิด/ปิด", width=70, height=24, font=ctk.CTkFont(family="Prompt", size=10), command=lambda q=i: self.toggle_queue_status(q))
            btn_toggle.pack(pady=(5, 8))

            self.card_widgets[i] = {"frame": c_frame, "name": lbl_name, "status": lbl_status, "toggle": btn_toggle}

    def run_expiry_check(self):
        try:
            target_str = self.target_date_entry.get().strip()
            min_d = int(self.min_days_entry.get().strip())
            max_d = int(self.max_days_entry.get().strip())
            
            target_date = dt.datetime.strptime(target_str, "%Y-%m-%d").date()
            today = dt.date.today()
            
            min_expire = today + dt.timedelta(days=min_d)
            max_expire = today + dt.timedelta(days=max_d)
            diff_days = (target_date - min_expire).days

            res_text = f"ช่วงรับได้: {min_expire.strftime('%d/%m/%Y')} ถึง {max_expire.strftime('%d/%m/%Y')}\n"
            if target_date < min_expire:
                res_text += f"❌ Reject: อายุสั้นกว่าเกณฑ์ MIN อยู่ {abs(diff_days):,} วัน"
            elif target_date > max_expire:
                over_days = (target_date - max_expire).days
                res_text += f"⚠️ Check: อายุเกินเกณฑ์ MAX อยู่ {over_days:,} วัน"
            else:
                res_text += "✔ Accept: อายุสินค้าผ่านเกณฑ์ปกติ"

            self.result_box.configure(state="normal")
            self.result_box.delete("0.0", "end")
            self.result_box.insert("0.0", res_text)
            self.result_box.configure(state="disabled")
        except Exception as ex:
            self.result_box.configure(state="normal")
            self.result_box.delete("0.0", "end")
            self.result_box.insert("0.0", "เกิดข้อผิดพลาด:\nรูปแบบวันที่ต้องเป็น YYYY-MM-DD")
            self.result_box.configure(state="disabled")

    def load_data(self):
        data = get_db_data()
        if data:
            curr = data["current_queue"]
            active = data["active_queues"]
            nicknames = data["nicknames"]
            custom_names = data["custom_names"]
            
            cfg = self.DEFAULT_QUEUES.get(curr, self.DEFAULT_QUEUES[1])
            comp_name = custom_names.get(str(curr), cfg["name"])
            nick = nicknames.get(str(curr), "")
            full_display = f"{comp_name} {f'({nick})' if nick else ''}"

            self.curr_num_lbl.configure(text=f"#{curr}")
            self.curr_name_lbl.configure(text=full_display)

            for i in range(1, 6):
                is_act = active.get(str(i), True)
                c_name = custom_names.get(str(i), self.DEFAULT_QUEUES[i]["name"])
                w = self.card_widgets[i]
                w["name"].configure(text=c_name)
                
                if not is_act:
                    w["status"].configure(text="❌ ปิดใช้งาน", text_color="gray")
                    w["frame"].configure(fg_color=("#F1F5F9", "#0F172A"))
                elif i == curr:
                    w["status"].configure(text="📢 กำลังเรียก", text_color="#2563EB")
                    w["frame"].configure(fg_color=("#DBEAFE", "#1E3A8A"))
                elif i < curr:
                    w["status"].configure(text="✔ ผ่านแล้ว", text_color="#10B981")
                    w["frame"].configure(fg_color=("#ECFDF5", "#064E3B"))
                else:
                    w["status"].configure(text="⏳ รอคิว", text_color="#D97706")
                    w["frame"].configure(fg_color=("#FEF3C7", "#78350F"))

    def change_queue(self, direction):
        data = get_db_data()
        if not data: return
        
        curr = data["current_queue"]
        active = data["active_queues"]
        nxt = curr + direction
        
        for _ in range(5):
            if nxt > 5: nxt = 1
            if nxt < 1: nxt = 5
            if active.get(str(nxt), True):
                break
            nxt += direction

        data["current_queue"] = nxt
        editor = self.username_entry.get().strip() or "เจ้าหน้าที่"
        save_db_data(data, f"{editor} (เปลี่ยนคิว)")
        
        q_info = self.DEFAULT_QUEUES.get(nxt, self.DEFAULT_QUEUES[1])
        speak_queue_text(q_info["readAs"])
        self.load_data()

    def reset_queue(self):
        data = get_db_data()
        if not data: return
        active = data["active_queues"]
        
        first_act = 1
        for i in range(1, 6):
            if active.get(str(i), True):
                first_act = i
                break
        
        data["current_queue"] = first_act
        editor = self.username_entry.get().strip() or "เจ้าหน้าที่"
        save_db_data(data, f"{editor} (รีเซ็ตคิว)")
        self.load_data()

    def toggle_queue_status(self, q_no):
        data = get_db_data()
        if not data: return
        active = data["active_queues"]
        current_status = active.get(str(q_no), True)
        active[str(q_no)] = not current_status
        
        data["active_queues"] = active
        editor = self.username_entry.get().strip() or "เจ้าหน้าที่"
        save_db_data(data, f"{editor} (สลับสถานะคิว #{q_no})")
        self.load_data()

if __name__ == "__main__":
    app = DCSBDesktopApp()
    app.mainloop()
