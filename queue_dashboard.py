<!DOCTYPE html>
<html lang="th" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DATA ENTRY (DCSB) - Dynamic Theme Dashboard</title>
    <!-- Favicon รูปฐานข้อมูลดีไซน์พรีเมียม -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='grad' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%231a1a1a'/%3E%3Cstop offset='50%25' stop-color='%23001f3f'/%3E%3Cstop offset='100%25' stop-color='%23bf9505'/%3E%3C/linearGradient%3E%3Cfilter id='shadow' x='-20%25' y='-20%25' width='140%25' height='140%25'%3E%3CfeDropShadow dx='0' dy='2' stdDeviation='2' flood-opacity='0.8'/%3E%3C/filter%3E%3C/defs%3E%3Crect width='64' height='64' rx='14' fill='url(%23grad)'/%3E%3Cg filter='url(%23shadow)'%3E%3Cellipse cx='32' cy='20' rx='16' ry='6' fill='%23bf9505' stroke='%23e6b800' stroke-width='1.5'/%3E%3Cpath d='M16 20v10c0 3.31 7.16 6 16 6s16-2.69 16-6V20' fill='none' stroke='%23bf9505' stroke-width='1.5'/%3E%3Cellipse cx='32' cy='30' rx='16' ry='6' fill='none' stroke='%23e6b800' stroke-width='1.5'/%3E%3Cpath d='M16 30v10c0 3.31 7.16 6 16 6s16-2.69 16-6V30' fill='none' stroke='%23005f99' stroke-width='1.5'/%3E%3Cellipse cx='32' cy='40' rx='16' ry='6' fill='none' stroke='%23bf9505' stroke-width='1.5'/%3E%3Cpath d='M38 46l8-8m0 0v6m0-6h-6' stroke='%23e6b800' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/g%3E%3C/svg%3E">
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = { darkMode: 'class' }
    </script>
    <!-- Google Fonts (Prompt) -->
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Prompt', sans-serif; }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center p-4 select-none transition-colors duration-300 bg-slate-100 dark:bg-[#0B0F19] text-slate-800 dark:text-slate-100">

    <!-- Popup แจ้งเตือนมุมขวาบน -->
    <div id="toast-notification" class="fixed top-5 right-5 z-50 transform translate-x-full opacity-0 transition-all duration-500 bg-white dark:bg-slate-900 border-l-4 border-indigo-500 dark:border-cyan-400 shadow-2xl rounded-xl p-4 flex items-center gap-3 min-w-[280px]">
        <div class="text-2xl">🔔</div>
        <div>
            <h4 id="toast-title" class="font-bold text-gray-800 dark:text-cyan-300 text-sm">มีการเปลี่ยนคิว!</h4>
            <p id="toast-message" class="text-xs text-gray-500 dark:text-slate-400">กำลังเรียกคิวถัดไป...</p>
        </div>
    </div>

    <!-- หน้าต่างแจ้งเตือนเสียงพูดวนซ้ำ -->
    <div id="stop-alert-container" class="hidden fixed inset-0 bg-black/60 dark:bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="bg-white dark:bg-slate-900 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl border-4 border-red-500">
            <div class="w-20 h-20 bg-red-100 dark:bg-red-950 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl animate-bounce">
                🚨
            </div>
            <h2 class="text-2xl font-bold text-slate-800 dark:text-white mb-2">ประกาศเรียกคิวใหม่!</h2>
            <p id="alert-queue-text" class="text-xl font-extrabold text-indigo-600 dark:text-cyan-300 mb-6">กำลังเรียกคิว...</p>
            <button onclick="stopVoiceAlert()" class="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-2xl shadow-lg text-lg transition cursor-pointer">
                🛑 รับทราบ / หยุดเสียงแจ้งเตือน
            </button>
        </div>
    </div>

    <div class="max-w-[1600px] w-full">
        <!-- หัวข้อหลักด้านบนสุด -->
        <div class="bg-white dark:bg-slate-900/90 px-6 py-4 rounded-2xl shadow-sm dark:shadow-xl border border-slate-200 dark:border-indigo-500/30 mb-4 flex flex-col sm:flex-row justify-between items-center gap-4 transition-colors duration-300">
            
            <div class="flex items-center gap-3.5">
                <div class="w-12 h-12 bg-indigo-50 dark:bg-gradient-to-tr dark:from-indigo-950 dark:via-blue-900 dark:to-purple-900 rounded-2xl flex items-center justify-center text-indigo-600 dark:text-cyan-400 shadow-sm dark:shadow-lg border border-indigo-100 dark:border-cyan-500/40">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
                    </svg>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-lg font-black tracking-wide">DATA ENTRY</h1>
                        <span class="text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-cyan-300 px-2 py-0.5 rounded-md font-extrabold tracking-widest border border-indigo-200 dark:border-indigo-500/40">DCSB</span>
                    </div>
                    <p class="text-xs text-slate-500 dark:text-slate-400">ระบบจัดการคิวและตรวจสอบอายุสินค้า (Real-time Sync)</p>
                </div>
            </div>

            <!-- ส่วนควบคุมเสียง, ผู้ใช้งาน และปุ่มสลับธีมด้านขวา -->
            <div class="flex flex-wrap items-center gap-3">
                <button onclick="toggleTheme()" class="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-cyan-300 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-indigo-500/30 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-sm">
                    <span id="theme-icon">☀️</span> <span id="theme-text">ธีมสว่าง</span>
                </button>

                <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span class="text-sm">🔊</span>
                    <div class="flex flex-col">
                        <span class="text-[10px] text-slate-400 font-semibold leading-none mb-0.5">ระดับเสียง (<span id="volume-val">100</span>%)</span>
                        <input type="range" id="voice-volume" min="0" max="1" step="0.1" value="1.0" oninput="updateVolume(this.value)" class="w-20 accent-indigo-600 dark:accent-cyan-500 cursor-pointer">
                    </div>
                </div>

                <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span class="text-xs font-medium">ผู้ใช้งานระบบ:</span>
                    <input type="text" id="username-input" value="เจ้าหน้าที่ 1" class="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1 text-xs font-semibold w-28 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-cyan-500">
                </div>
            </div>
        </div>

        <!-- ================= โครงสร้างแบ่ง 2 ฝั่ง (Grid 2 Columns) ================= -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- ================= ฝั่งซ้าย (4 ส่วน): ระบบคำนวณอายุสินค้า ================= -->
            <div class="lg:col-span-4 bg-white dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-3xl shadow-xl border border-slate-200 dark:border-indigo-500/30 flex flex-col justify-between transition-colors duration-300">
                <div>
                    <div class="flex items-center justify-between mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
                        <h2 class="text-base font-extrabold flex items-center gap-2">
                            <span>📦</span> คำนวณอายุสินค้า
                        </h2>
                        <button onclick="resetCalculator()" class="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 font-bold px-2.5 py-1 rounded-xl transition text-xs flex items-center gap-1 border border-slate-300 dark:border-slate-700 cursor-pointer shadow-sm" title="รีเซ็ตข้อมูล">
                            🔄 รีเซ็ต
                        </button>
                    </div>

                    <!-- แผงเลือกโหมดการคำนวณ -->
                    <div class="bg-slate-100 dark:bg-slate-950 p-1.5 rounded-2xl mb-4 flex gap-1 border border-slate-200 dark:border-slate-800">
                        <button type="button" id="mode-btn-1" onclick="switchMode(1)" class="flex-1 py-2 px-3 rounded-xl text-xs font-bold transition bg-white dark:bg-gradient-to-r dark:from-cyan-600 dark:to-indigo-600 text-indigo-600 dark:text-white shadow-sm cursor-pointer">
                            🎯 ตรวจสอบเกณฑ์ (Min/Max)
                        </button>
                        <button type="button" id="mode-btn-2" onclick="switchMode(2)" class="flex-1 py-2 px-3 rounded-xl text-xs font-bold transition text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-white cursor-pointer">
                            📅 คำนวณ Product Life
                        </button>
                    </div>

                    <div class="space-y-4 mb-5">
                        <!-- แถบแจ้งเตือนสถานะ -->
                        <div id="status-container">
                            <div id="expiry-status-box" class="w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-slate-50 dark:bg-slate-950 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800 shadow-sm">
                                กรุณากำหนดวันหมดอายุจริงเพื่อตรวจสอบเกณฑ์
                            </div>
                        </div>

                        <!-- แถบแสดงผลลัพธ์ช่วงวันหมดอายุที่รับได้ -->
                        <div id="range-box-container" class="bg-gradient-to-br from-blue-900 to-slate-900 dark:from-indigo-950 dark:via-slate-950 dark:to-purple-950 text-white rounded-2xl p-4 shadow-inner text-center space-y-2 border border-transparent dark:border-indigo-500/40">
                            <p class="text-[11px] text-blue-300 dark:text-cyan-400 uppercase tracking-widest font-semibold">ช่วงวันหมดอายุที่รับได้ (ค.ศ.)</p>
                            <div class="text-sm font-black flex flex-col gap-0.5 items-center justify-center">
                                <span id="result-min-date" class="text-emerald-400 dark:text-cyan-300 text-sm">-</span>
                                <span class="text-slate-400 text-[11px] font-normal">ถึง</span>
                                <span id="result-max-date" class="text-amber-400 dark:text-purple-300 text-sm">-</span>
                            </div>
                            <div class="pt-2 border-t border-white/10 dark:border-indigo-500/20 flex justify-around text-[11px]">
                                <div>Min: <span id="span-min-days" class="font-bold text-emerald-400 dark:text-cyan-400">0</span> วัน</div>
                                <div>Max: <span id="span-max-days" class="font-bold text-amber-400 dark:text-purple-400">0</span> วัน</div>
                            </div>
                        </div>

                        <!-- ฟิลด์วันที่รับสินค้า -->
                        <div id="field-today">
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">วันที่รับสินค้า (Today)</label>
                            <input type="date" id="calc-today" onchange="runCalculation()" class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl px-3 py-2 text-sm font-bold text-slate-700 dark:text-cyan-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-cyan-500">
                        </div>

                        <!-- ฟิลด์วันที่ผลิต (MFG) -->
                        <div id="field-mfg" class="hidden">
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">วันที่ผลิต (MFG Date)</label>
                            <input type="date" id="calc-mfg-date" onchange="runCalculation()" class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl px-3 py-2 text-sm font-bold text-slate-700 dark:text-cyan-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-cyan-500 cursor-pointer">
                        </div>

                        <!-- ฟิลด์วันหมดอายุจริง -->
                        <div>
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">วันหมดอายุจริงของสินค้า (Target Expire Date)</label>
                            <input type="date" id="calc-target-date" onchange="runCalculation()" class="w-full bg-indigo-50 dark:bg-slate-950 border-2 border-indigo-300 dark:border-indigo-500/50 rounded-xl px-3 py-2 text-sm font-bold text-indigo-700 dark:text-cyan-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-cyan-400 cursor-pointer">
                        </div>

                        <!-- ฟิลด์ MIN / MAX Expire -->
                        <div id="field-minmax" class="space-y-4">
                            <div>
                                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">MIN Expire (วันขั้นต่ำ)</label>
                                <input type="number" id="calc-min" oninput="runCalculation()" placeholder="ระบุวันขั้นต่ำ..." class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl px-3 py-2 text-sm font-bold text-slate-700 dark:text-cyan-300 focus:outline-none focus:ring-2 focus:ring-indigo-400">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">MAX Expire (วันสูงสุด)</label>
                                <input type="number" id="calc-max" oninput="runCalculation()" placeholder="ระบุวันสูงสุด..." class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl px-3 py-2 text-sm font-bold text-slate-700 dark:text-cyan-300 focus:outline-none focus:ring-2 focus:ring-indigo-400">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ================= ฝั่งขวา (8 ส่วน): Dashboard ระบบรันคิว ================= -->
            <div class="lg:col-span-8 bg-white dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-3xl shadow-xl border border-slate-200 dark:border-indigo-500/30 flex flex-col justify-between transition-colors duration-300">
                <div>
                    <!-- แสดงสถานะคิวปัจจุบันตัวใหญ่ (ไฮไลต์) พร้อมปุ่ม +/- -->
                    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-950 dark:via-indigo-950 dark:to-purple-950 text-white rounded-2xl p-6 mb-6 text-center shadow-lg transition-all duration-300 relative overflow-hidden flex flex-col items-center border border-transparent dark:border-cyan-500/40">
                        
                        <button onclick="openFloatingWindow()" class="absolute top-4 right-4 bg-white dark:bg-slate-900 hover:bg-blue-50 dark:hover:bg-slate-800 text-indigo-600 dark:text-cyan-300 border border-white dark:border-cyan-500/40 font-bold text-xs px-3.5 py-2 rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-lg z-20">
                            <span>🪟 หน้าต่างลอย</span>
                        </button>

                        <div class="absolute -right-10 -bottom-10 text-white/10 dark:text-white/5 text-9xl font-bold">#<span id="current-bg-num">1</span></div>
                        
                        <p class="text-blue-100 dark:text-cyan-400 text-xs font-semibold uppercase tracking-widest">กำลังเรียกคิวปัจจุบัน</p>
                        <h2 id="current-name" class="text-3xl md:text-4xl font-black my-2 tracking-wide dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-r dark:from-cyan-300 dark:via-white dark:to-purple-300">กำลังโหลด...</h2>
                        <p id="current-number" class="text-sm font-medium opacity-90 dark:text-slate-300 mb-4">คิวที่ - จากทั้งหมดที่เปิดใช้งาน</p>

                        <div class="flex items-center gap-4 bg-white/10 dark:bg-slate-950/60 backdrop-blur-md px-6 py-2 rounded-full border border-white/20 dark:border-indigo-500/30 shadow-inner z-10">
                            <button onclick="changeQueue(-1)" class="w-8 h-8 rounded-full bg-white/20 dark:bg-slate-800 hover:bg-white/40 dark:hover:bg-slate-700 text-white dark:text-cyan-300 font-bold text-lg flex items-center justify-center transition cursor-pointer shadow" title="ลดคิว">
                                ➖
                            </button>
                            <span class="text-[11px] uppercase tracking-wider font-semibold px-2">ปรับลด / เพิ่มคิวถัดไป</span>
                            <button onclick="changeQueue(1)" class="w-8 h-8 rounded-full bg-white/20 dark:bg-slate-800 hover:bg-white/40 dark:hover:bg-slate-700 text-white dark:text-cyan-300 font-bold text-lg flex items-center justify-center transition cursor-pointer shadow" title="เพิ่มคิว">
                                ➕
                            </button>
                        </div>

                        <p id="last-updated-by" class="text-[11px] text-blue-200 dark:text-cyan-400/70 mt-3 font-light">อัปเดตล่าสุดโดย: -</p>
                    </div>

                    <!-- แผงแดชบอร์ดแสดงคิวทั้ง 5 แบบการ์ด -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 mb-6" id="dashboard-grid"></div>
                </div>

                <!-- ปุ่มควบคุมด้านล่าง (มีปุ่มรีเซ็ตชื่อเดิมเพิ่มให้) -->
                <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-200 dark:border-slate-800">
                    <button onclick="nextQueue()" id="next-btn" class="flex-1 bg-emerald-500 hover:bg-emerald-600 dark:bg-gradient-to-r dark:from-emerald-600 dark:to-teal-600 dark:hover:from-emerald-500 dark:hover:to-teal-500 text-white font-bold py-3 px-6 rounded-2xl transition shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2 cursor-pointer text-sm">
                        <span>⏩ ผ่าน / เรียกคิวถัดไป</span>
                    </button>
                    <button onclick="resetDefaultNames()" class="bg-amber-500 hover:bg-amber-600 text-white font-bold px-4 py-3 rounded-2xl transition cursor-pointer text-xs flex items-center justify-center gap-1.5 shadow" title="คืนค่าชื่อคิวเริ่มต้นเดิม">
                        <span>↩️ คืนค่าชื่อเดิม</span>
                    </button>
                    <button onclick="resetQueue()" class="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 font-bold px-5 py-3 rounded-2xl transition cursor-pointer text-sm flex items-center justify-center gap-2 border border-slate-300 dark:border-slate-700">
                        <span>🔄 รีเซ็ตคิว</span>
                    </button>
                </div>
            </div>

        </div>
    </div>

    <!-- Firebase SDK -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js";
        import { getFirestore, doc, getDoc, setDoc, onSnapshot, updateDoc } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore.js";

        const firebaseConfig = {
            apiKey: "AIzaSyCIeoKstwU8o7FUVNMA-2Hj9OOzsVX0baY",
            authDomain: "queue-management-system-9aaf7.firebaseapp.com",
            projectId: "queue-management-system-9aaf7",
            storageBucket: "queue-management-system-9aaf7.appspot.com",
            messagingSenderId: "514453719785",
            appId: "1:514453719785:web:b5e29275f5a0e44faebe78",
            measurementId: "G-Z3CTMZGNT8"
        };

        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);

        const DEFAULT_QUEUE_CONFIG = {
            1: { name: "SAHAPAT", readAs: "สหพัฒน์", color: "from-amber-500 to-orange-500", badge: "bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-600/50" },
            2: { name: "DKSH", readAs: "ดีเคเอสเอช", color: "from-blue-500 to-cyan-500", badge: "bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-600/50" },
            3: { name: "CROSSDOCK", readAs: "ครอสคอร์ส", color: "from-purple-500 to-indigo-500", badge: "bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-600/50" },
            4: { name: "PEPSI", readAs: "เป๊ปซี่", color: "from-red-500 to-rose-600", badge: "bg-red-100 dark:bg-red-950/80 text-red-800 dark:text-red-300 border-red-300 dark:border-red-600/50" },
            5: { name: "SINO", readAs: "ชิโน", color: "from-emerald-500 to-teal-600", badge: "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600/50" }
        };

        const queueDocRef = doc(db, "queues", "dashboard_counter_v12");
        let previousQueue = null;
        let alertInterval = null;
        let activeTypingIndex = null;
        let activeNameEditingIndex = null;
        let currentVolume = 1.0;
        let currentMode = 1;
        let latestLoadedData = null;

        window.onload = function() {
            const savedTheme = localStorage.getItem('dcsb_theme') || 'dark';
            if (savedTheme === 'light') {
                document.documentElement.classList.remove('dark');
                document.getElementById('theme-icon').innerText = '🌌';
                document.getElementById('theme-text').innerText = 'ธีมกาแล็คซี่';
            } else {
                document.documentElement.classList.add('dark');
                document.getElementById('theme-icon').innerText = '☀️';
                document.getElementById('theme-text').innerText = 'ธีมสว่าง';
            }

            const todayStr = new Date().toISOString().split('T')[0];
            document.getElementById('calc-today').value = todayStr;
            document.getElementById('calc-min').value = "730";
            document.getElementById('calc-max').value = "1095";
            switchMode(1);
            initQueueListener();
        };

        window.toggleTheme = function() {
            const htmlEl = document.documentElement;
            if (htmlEl.classList.contains('dark')) {
                htmlEl.classList.remove('dark');
                localStorage.setItem('dcsb_theme', 'light');
                document.getElementById('theme-icon').innerText = '🌌';
                document.getElementById('theme-text').innerText = 'ธีมกาแล็คซี่';
            } else {
                htmlEl.classList.add('dark');
                localStorage.setItem('dcsb_theme', 'dark');
                document.getElementById('theme-icon').innerText = '☀️';
                document.getElementById('theme-text').innerText = 'ธีมสว่าง';
            }
        };

        window.switchMode = function(mode) {
            currentMode = mode;
            const btn1 = document.getElementById('mode-btn-1');
            const btn2 = document.getElementById('mode-btn-2');
            const fieldToday = document.getElementById('field-today');
            const fieldMfg = document.getElementById('field-mfg');
            const fieldMinMax = document.getElementById('field-minmax');
            const statusContainer = document.getElementById('status-container');
            const rangeBoxContainer = document.getElementById('range-box-container');

            if (mode === 1) {
                btn1.className = "flex-1 py-2 px-3 rounded-xl text-xs font-bold transition bg-white dark:bg-gradient-to-r dark:from-cyan-600 dark:to-indigo-600 text-indigo-600 dark:text-white shadow-sm cursor-pointer";
                btn2.className = "flex-1 py-2 px-3 rounded-xl text-xs font-bold transition text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-white cursor-pointer";
                fieldToday.classList.remove('hidden');
                fieldMfg.classList.add('hidden');
                fieldMinMax.classList.remove('hidden');
                statusContainer.classList.remove('hidden');
                rangeBoxContainer.classList.remove('hidden');
            } else {
                btn2.className = "flex-1 py-2 px-3 rounded-xl text-xs font-bold transition bg-white dark:bg-gradient-to-r dark:from-cyan-600 dark:to-indigo-600 text-indigo-600 dark:text-white shadow-sm cursor-pointer";
                btn1.className = "flex-1 py-2 px-3 rounded-xl text-xs font-bold transition text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-white cursor-pointer";
                fieldToday.classList.add('hidden');
                fieldMfg.classList.remove('hidden');
                fieldMinMax.classList.add('hidden');
                statusContainer.classList.add('hidden');
                rangeBoxContainer.classList.add('hidden');
            }
            runCalculation();
        };

        window.resetCalculator = function() {
            const todayStr = new Date().toISOString().split('T')[0];
            document.getElementById('calc-today').value = todayStr;
            document.getElementById('calc-mfg-date').value = "";
            document.getElementById('calc-target-date').value = "";
            document.getElementById('calc-min').value = "730";
            document.getElementById('calc-max').value = "1095";
            
            const statusBox = document.getElementById('expiry-status-box');
            statusBox.className = "w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-slate-50 dark:bg-slate-950 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800 shadow-sm";
            statusBox.innerHTML = `กรุณากำหนดวันหมดอายุจริงเพื่อตรวจสอบเกณฑ์`;

            document.getElementById('result-min-date').innerText = "-";
            document.getElementById('result-max-date').innerText = "-";
            document.getElementById('span-min-days').innerText = "0";
            document.getElementById('span-max-days').innerText = "0";
            runCalculation();
        };

        window.updateVolume = function(val) {
            currentVolume = parseFloat(val);
            document.getElementById('volume-val').innerText = Math.round(currentVolume * 100);
        }

        function formatDateAD(dateObj) {
            let day = String(dateObj.getDate()).padStart(2, '0');
            let month = String(dateObj.getMonth() + 1).padStart(2, '0');
            let year = dateObj.getFullYear();
            return `${day}/${month}/${year}`;
        }

        window.runCalculation = function() {
            if (currentMode === 1) {
                const todayVal = document.getElementById('calc-today').value;
                const targetVal = document.getElementById('calc-target-date').value;
                const minDays = parseInt(document.getElementById('calc-min').value);
                const maxDays = parseInt(document.getElementById('calc-max').value);

                if (!todayVal || isNaN(minDays) || isNaN(maxDays)) {
                    document.getElementById('result-min-date').innerText = "-";
                    document.getElementById('result-max-date').innerText = "-";
                    document.getElementById('span-min-days').innerText = isNaN(minDays) ? "0" : minDays.toLocaleString();
                    document.getElementById('span-max-days').innerText = isNaN(maxDays) ? "0" : maxDays.toLocaleString();
                    return;
                }

                let baseDate = new Date(todayVal);
                let minExpireDate = new Date(baseDate);
                minExpireDate.setDate(baseDate.getDate() + minDays);

                let maxExpireDate = new Date(baseDate);
                maxExpireDate.setDate(baseDate.getDate() + maxDays);

                document.getElementById('result-min-date').innerText = formatDateAD(minExpireDate);
                document.getElementById('result-max-date').innerText = formatDateAD(maxExpireDate);
                document.getElementById('span-min-days').innerText = minDays.toLocaleString();
                document.getElementById('span-max-days').innerText = maxDays.toLocaleString();

                const statusBox = document.getElementById('expiry-status-box');
                if (targetVal) {
                    let targetDate = new Date(targetVal);
                    let diffTime = targetDate - minExpireDate;
                    let diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

                    if (targetDate < minExpireDate) {
                        let shortDays = Math.abs(diffDays);
                        statusBox.className = "w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-red-100 dark:bg-red-950/80 text-red-700 dark:text-red-300 border-red-300 dark:border-red-600 shadow-sm alert-active";
                        statusBox.innerHTML = `❌ ขาด (Short): ${shortDays.toLocaleString()} วัน (Reject)`;
                    } else if (targetDate > maxExpireDate) {
                        let maxTime = targetDate - maxExpireDate;
                        let overDays = Math.round(maxTime / (1000 * 60 * 60 * 24));
                        statusBox.className = "w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-600 shadow-sm";
                        statusBox.innerHTML = `⚠️ เกิน (Over): ${overDays.toLocaleString()} วัน (Check)`;
                    } else {
                        statusBox.className = "w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600 shadow-sm";
                        statusBox.innerHTML = `✔ ผ่านเกณฑ์: อายุสินค้าปกติ (Accept)`;
                    }
                } else {
                    statusBox.className = "w-full p-3.5 rounded-2xl text-center text-sm font-black border transition-all duration-300 bg-slate-50 dark:bg-slate-950 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800";
                    statusBox.innerHTML = `กรุณากำหนดวันหมดอายุจริงเพื่อตรวจสอบเกณฑ์`;
                }
            }
        };

        window.openFloatingWindow = function() {
            const url = window.location.href;
            const width = 850;
            const height = 700;
            const left = (window.screen.width / 2) - (width / 2);
            const top = (window.screen.height / 2) - (height / 2);
            window.open(url, 'QueueFloatingWindow', `width=${width},height=${height},top=${top},left=${left},resizable=yes,scrollbars=yes`);
        };

        function speakQueueName(queueNumber, queueReadName, nickName) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                let textToSpeak = `ขอเชิญคิวที่ ${queueNumber}, บริษัท ${queueReadName}`;
                if (nickName) textToSpeak += `, ${nickName}`;
                const utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.lang = 'th-TH';
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = currentVolume;
                window.speechSynthesis.speak(utterance);
            }
        }

        window.startLoopAlert = function(queueNumber, item, nickName) {
            document.getElementById('alert-queue-text').innerText = `คิวที่ ${queueNumber} : ${item.name} ${nickName ? '(' + nickName + ')' : ''}`;
            document.getElementById('stop-alert-container').classList.remove('hidden');
            speakQueueName(queueNumber, item.readAs, nickName);

            if (alertInterval) clearInterval(alertInterval);
            alertInterval = setInterval(() => {
                speakQueueName(queueNumber, item.readAs, nickName);
            }, 6000);
        }

        window.stopVoiceAlert = function() {
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            if (alertInterval) { clearInterval(alertInterval); alertInterval = null; }
            document.getElementById('stop-alert-container').classList.add('hidden');
        }

        window.resetDefaultNames = async function() {
            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            if (confirm("คุณต้องการคืนค่าชื่อคิวทั้งหมดให้กลับเป็นชื่อเริ่มต้นเดิมหรือไม่?")) {
                await updateDoc(queueDocRef, { 
                    customNames: {}, 
                    updatedBy: `${editorName} (คืนค่าชื่อคิวเดิม)` 
                });
                showToast("🔄 สำเร็จ", "คืนค่าชื่อคิวกลับเป็นค่าเริ่มต้นแล้ว");
            }
        };

        function showToast(title, message) {
            const toast = document.getElementById('toast-notification');
            document.getElementById('toast-title').innerText = title;
            document.getElementById('toast-message').innerText = message;
            toast.classList.remove('translate-x-full', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-x-full', 'opacity-0');
            }, 3500);
        }

        function initQueueListener() {
            onSnapshot(queueDocRef, async (docSnap) => {
                if (!docSnap.exists()) {
                    const initialData = { 
                        current: 1, 
                        activeQueues: {1:true, 2:true, 3:true, 4:true, 5:true},
                        nicknames: {1:"", 2:"", 3:"", 4:"", 5:""},
                        customNames: {},
                        updatedBy: "ระบบเริ่มต้น" 
                    };
                    await setDoc(queueDocRef, initialData);
                } else {
                    const data = docSnap.data();
                    latestLoadedData = data;
                    const current = data.current;
                    const activeQueues = data.activeQueues || {1:true, 2:true, 3:true, 4:true, 5:true};
                    const nicknames = data.nicknames || {1:"", 2:"", 3:"", 4:"", 5:""};
                    const customNames = data.customNames || {};

                    const queueNames = {};
                    for(let i=1; i<=5; i++) {
                        queueNames[i] = {
                            ...DEFAULT_QUEUE_CONFIG[i],
                            name: customNames[i] || DEFAULT_QUEUE_CONFIG[i].name
                        };
                    }

                    if (previousQueue !== null && previousQueue !== current) {
                        const item = queueNames[current];
                        if (item && activeQueues[current]) {
                            showToast(`กำลังเรียกคิว: ${item.name}`, `อัปเดตโดย: ${data.updatedBy || 'เจ้าหน้าที่'}`);
                            startLoopAlert(current, item, nicknames[current] || "");
                        }
                    }

                    previousQueue = current;
                    updateDashboardUI(current, activeQueues, nicknames, queueNames, data.updatedBy || "ระบบ");
                }
            }, (error) => {
                console.error("Firebase error:", error);
                const fallbackData = {
                    current: 1,
                    activeQueues: {1:true, 2:true, 3:true, 4:true, 5:true},
                    nicknames: {1:"", 2:"", 3:"", 4:"", 5:""},
                    customNames: {}
                };
                latestLoadedData = fallbackData;
                updateDashboardUI(1, fallbackData.activeQueues, fallbackData.nicknames, DEFAULT_QUEUE_CONFIG, "โหมดสำรอง");
            });
        }

        function updateDashboardUI(currentQueue, activeQueues, nicknames, queueNames, updatedBy) {
            const currentItem = queueNames[currentQueue] || { name: "ไม่มีคิวที่เปิด" };
            
            document.getElementById('current-name').innerText = currentItem.name;
            document.getElementById('current-number').innerText = `คิวที่ ${currentQueue}`;
            document.getElementById('current-bg-num').innerText = currentQueue;
            document.getElementById('last-updated-by').innerText = `อัปเดตล่าสุดโดย: ${updatedBy}`;

            let gridHtml = "";
            for (let i = 1; i <= 5; i++) {
                let isActive = activeQueues[i] !== false;
                let isCurrent = (i === currentQueue && isActive);
                let isPassed = (i < currentQueue && isActive);
                let item = queueNames[i];
                let currentNick = nicknames[i] || "";

                let cardClasses = "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 shadow-sm";
                let badgeStatus = `<span class="text-[10px] px-2 py-0.5 rounded-full font-semibold border ${item.badge}">รอดำเนินการ</span>`;

                if (!isActive) {
                    cardClasses = "bg-slate-200/60 dark:bg-slate-950/40 border-slate-300 dark:border-slate-900 text-slate-400 dark:text-slate-600 opacity-50 grayscale";
                    badgeStatus = `<span class="text-[10px] bg-slate-300 dark:bg-slate-900 text-slate-600 dark:text-slate-500 px-2 py-0.5 rounded-full font-semibold">❌ ปิด</span>`;
                } else if (isCurrent) {
                    cardClasses = `bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-950 dark:via-slate-900 dark:to-purple-950 border-2 border-indigo-500 dark:border-cyan-400 text-slate-900 dark:text-white shadow-md dark:shadow-xl scale-105 z-10`;
                    badgeStatus = `<span class="text-[10px] bg-indigo-600 dark:bg-cyan-500 text-white dark:text-slate-950 px-2.5 py-0.5 rounded-full font-bold shadow-sm animate-pulse">📢 กำลังเรียก</span>`;
                } else if (isPassed) {
                    cardClasses = "bg-slate-50/80 dark:bg-slate-950/60 border-slate-200 dark:border-slate-800 text-slate-400 dark:text-slate-500 opacity-60";
                    badgeStatus = `<span class="text-[10px] bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800 px-2 py-0.5 rounded-full font-semibold">✔ ผ่าน</span>`;
                }

                let toggleBtnText = isActive ? "🗑️ เอาออก" : "📥 นำเข้า";
                let toggleBtnClass = isActive ? "bg-red-50 dark:bg-red-950/60 hover:bg-red-100 dark:hover:bg-red-900 text-red-600 dark:text-red-300 border-red-200 dark:border-red-800" : "bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900 text-emerald-600 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800";

                let nickInputVal = (activeTypingIndex === i) ? document.getElementById(`nickname-${i}`).value : currentNick;
                let nameDisplay = (activeNameEditingIndex === i) ? 
                    `<input type="text" id="name-edit-${i}" value="${document.getElementById('name-edit-'+i) ? document.getElementById('name-edit-'+i).value : item.name}" onblur="saveQueueName(${i})" onkeydown="if(event.key==='Enter') this.blur()" class="w-24 bg-white dark:bg-slate-950 border border-indigo-400 dark:border-cyan-400 rounded px-1 py-0.5 text-xs font-black text-center text-slate-800 dark:text-cyan-200 focus:outline-none" autofocus>` :
                    `<p class="text-xs font-black tracking-wider text-slate-800 dark:text-white cursor-pointer hover:text-indigo-600 dark:hover:text-cyan-300 transition" onclick="activeNameEditingIndex=${i}; updateDashboardUI(previousQueue, activeQueues, nicknames, window.latestQueueNames || queueNames, '${updatedBy}')" title="คลิกเพื่อแก้ไขชื่อ">${item.name}</p>`;

                gridHtml += `
                    <div class="border rounded-2xl p-3 flex flex-col justify-between items-center transition-all duration-300 ${cardClasses}">
                        <div class="flex justify-between w-full mb-2 items-center">
                            <input type="text" id="nickname-${i}" value="${nickInputVal}" placeholder="ชื่อเล่น..." onfocus="activeTypingIndex=${i}" onblur="activeTypingIndex=null; updateNickname(${i})" class="w-16 bg-slate-100 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg px-1.5 py-0.5 text-[11px] font-bold text-slate-700 dark:text-cyan-300 text-center focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:border-cyan-500">
                            ${badgeStatus}
                        </div>
                        <div class="my-2 text-center w-full">
                            <div class="w-8 h-8 mx-auto mb-1 rounded-lg bg-gradient-to-tr ${item.color} flex items-center justify-center text-white text-xs font-bold shadow-sm">
                                ${i}
                            </div>
                            ${nameDisplay}
                        </div>
                        <div class="w-full mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
                            <span class="text-[9px] text-slate-400 dark:text-slate-500 font-medium">#${i}</span>
                            <button onclick="toggleQueue(${i})" class="text-[10px] px-2 py-0.5 rounded-md border font-semibold transition cursor-pointer shadow-sm ${toggleBtnClass}">
                                ${toggleBtnText}
                            </button>
                        </div>
                    </div>
                `;
            }
            window.latestQueueNames = queueNames;
            document.getElementById('dashboard-grid').innerHTML = gridHtml;
        }

        window.saveQueueName = async function(queueNo) {
            const inputEl = document.getElementById(`name-edit-${queueNo}`);
            if(!inputEl) return;
            const newName = inputEl.value.trim();
            activeNameEditingIndex = null;
            if(!newName) return;

            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            const docSnap = await getDoc(queueDocRef);
            let data = docSnap.exists() ? docSnap.data() : (latestLoadedData || { customNames: {} });
            let customNames = data.customNames || {};
            customNames[queueNo] = newName;
            await updateDoc(queueDocRef, { customNames: customNames, updatedBy: `${editorName} (แก้ไขชื่อคิว #${queueNo})` });
        };

        window.updateNickname = async function(queueNo) {
            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            const val = document.getElementById(`nickname-${queueNo}`).value.trim();
            const docSnap = await getDoc(queueDocRef);
            let data = docSnap.exists() ? docSnap.data() : (latestLoadedData || { nicknames: {} });
            let nicknames = data.nicknames || {1:"", 2:"", 3:"", 4:"", 5:""};
            nicknames[queueNo] = val;
            await updateDoc(queueDocRef, { nicknames: nicknames, updatedBy: `${editorName} (แก้ไขชื่อเล่น)` });
        };

        window.toggleQueue = async function(queueNo) {
            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            const docSnap = await getDoc(queueDocRef);
            let data = docSnap.exists() ? docSnap.data() : (latestLoadedData || { activeQueues: {1:true,2:true,3:true,4:true,5:true}, current:1 });
            let activeQueues = data.activeQueues || {1:true, 2:true, 3:true, 4:true, 5:true};
            activeQueues[queueNo] = !activeQueues[queueNo];
            let current = data.current;
            if (current === queueNo && !activeQueues[queueNo]) {
                for (let i = 1; i <= 5; i++) {
                    if (activeQueues[i]) { current = i; break; }
                }
            }
            await updateDoc(queueDocRef, { activeQueues: activeQueues, current: current, updatedBy: `${editorName} (สลับสถานะคิว #${queueNo})` });
        };

        window.changeQueue = async function(direction) {
            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            const docSnap = await getDoc(queueDocRef);
            let data = docSnap.exists() ? docSnap.data() : (latestLoadedData || { activeQueues: {1:true,2:true,3:true,4:true,5:true}, current:1 });
            let current = data.current;
            let activeQueues = data.activeQueues || {1:true, 2:true, 3:true, 4:true, 5:true};
            let next = current;
            for (let step = 0; step < 5; step++) {
                next += direction;
                if (next > 5) next = 1;
                if (next < 1) next = 5;
                if (activeQueues[next] !== false) { current = next; break; }
            }
            await updateDoc(queueDocRef, { current: current, updatedBy: `${editorName} (ปรับคิว)` });
        };

        window.nextQueue = async function() { window.changeQueue(1); };

        window.resetQueue = async function() {
            const editorName = document.getElementById('username-input').value.trim() || "ไม่ระบุชื่อ";
            if (confirm("คุณต้องการรีเซ็ตคิวกลับไปเริ่มต้นที่คิวแรกสุดที่เปิดใช้งานใช่หรือไม่?")) {
                const docSnap = await getDoc(queueDocRef);
                let data = docSnap.exists() ? docSnap.data() : (latestLoadedData || { activeQueues: {1:true,2:true,3:true,4:true,5:true} });
                let activeQueues = data.activeQueues || {1:true, 2:true, 3:true, 4:true, 5:true};
                let firstActive = 1;
                for (let i = 1; i <= 5; i++) {
                    if (activeQueues[i] !== false) { firstActive = i; break; }
                }
                await updateDoc(queueDocRef, { current: firstActive, updatedBy: `${editorName} (รีเซ็ต)` });
            }
        };
    </script>
</body>
</html>
