import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # استيراد مكتبتي PIL للتعامل مع الصور و ImageTk لعرض الصور في Tkinter
import subprocess
import threading

# دالة لاختيار الملف المصدر
def choose_source_file():
    file = filedialog.askopenfilename(
        title="اختر ملف",
        filetypes=(
            ("All Files", "*.*"),
            ("Images", "*.png;*.jpg;*.jpeg;*.gif"),
            ("Videos", "*.mp4;*.mkv;*.avi;*.mov"),
            ("Audio", "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a")
        )
    )
    source_folder_var.set(file)

# دالة لاختيار المجلد المصدر
def choose_source_folder():
    folder = filedialog.askdirectory(title="اختر المجلد الذي يحتوي على الملفات الأصلية")
    source_folder_var.set(folder)

# دالة لاختيار المجلد الوجهة
def choose_destination_folder():
    folder = filedialog.askdirectory(title="اختر المجلد الذي تريد حفظ الملفات المحولة فيه")
    destination_folder_var.set(folder)

# دالة للتحويل
def convert_to_webp():
    def task():
        source_folder = source_folder_var.get()
        destination_folder = destination_folder_var.get()

        if not source_folder or not destination_folder:
            messagebox.showerror("خطأ", "يرجى اختيار المجلدات أو الملفات بشكل صحيح.")
            return

        # إذا كان المصدر ملفًا فرديًا
        if os.path.isfile(source_folder):
            files = [source_folder]
        # إذا كان المصدر مجلدًا
        else:
            files = []
            for ext in ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'avi', 'mov']:
                files += [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith(ext)]

        total_files = len(files)
        if total_files == 0:
            messagebox.showerror("خطأ", "لم يتم العثور على ملفات للتحويل في المصدر.")
            return

        # التأكد من أن مجلد الوجهة موجود
        os.makedirs(destination_folder, exist_ok=True)

        progress_bar['value'] = 0
        progress_bar['maximum'] = total_files

        try:
            # البدء في التحويل
            for i, file in enumerate(files, 1):
                filename = os.path.basename(file)
                output_file = os.path.join(destination_folder, f"{os.path.splitext(filename)[0]}.webp")

                 # التحقق من وجود الملف بالفعل
                if os.path.exists(output_file):
                    result = messagebox.askyesno("تأكيد الاستبدال", f"موجود بالفعل. هل تريد إستبداله؟ '{output_file}' الملف")
                    if not result:
                        continue  # تجاوز هذا الملف إذا اختار المستخدم "لا"

                try:
                    if file.endswith(('png', 'jpg', 'jpeg')):
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-vcodec', 'libwebp', '-lossless', '0',
                             '-compression_level', '6', '-q:v', '50', output_file],
                            check=True
                        )
                    elif file.endswith('gif'):
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-vcodec', 'libwebp', '-vf', 'scale=640:-1', '-lossless', '0',
                             '-compression_level', '6', '-q:v', '50', '-loop', '0', output_file],
                            check=True
                        )
                    elif file.endswith(('mp4', 'mkv', 'avi', 'mov')):
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-vcodec', 'libwebp', '-vf', 'scale=640:-1,fps=15', '-lossless', '0',
                             '-compression_level', '6', '-q:v', '50', '-loop', '0', '-an', '-vsync', '0', output_file],
                            check=True
                        )
                    else:
                        messagebox.showerror("خطأ", f".غير مدعومة {str(filename)} صيغة الملف")
                        return

                    # تحديث شريط التقدم
                    progress_bar['value'] = i
                    root.update_idletasks()

                except subprocess.CalledProcessError as e:
                    messagebox.showerror("خطأ", f"فشل معالجة الملف {filename}: {str(e)}")
                    continue

            messagebox.showinfo("نجاح", "! تمت عملية التحويل بنجاح")

            # تفريغ الحقول بعد إتمام التحويل
            source_folder_var.set("")
            destination_folder_var.set("")

        except Exception as e:
            messagebox.showerror("خطأ", f"{str(e)} : حدث خطأ أثناء المعالجة")
        finally:
            progress_bar['value'] = 0

    # إنشاء وتشغيل خيط جديد
    thread = threading.Thread(target=task)
    thread.start()


def compress_files():
    def task():
        source_folder = source_folder_var.get()
        destination_folder = destination_folder_var.get()

        if not source_folder or not destination_folder:
            messagebox.showerror("خطأ", "يرجى اختيار المجلدات أو الملفات بشكل صحيح.")
            return

        # إذا كان المصدر ملفًا فرديًا
        if os.path.isfile(source_folder):
            files = [source_folder]
        # إذا كان المصدر مجلدًا
        else:
            files = []
            for ext in ['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav', 'aac', 'png', 'jpg', 'jpeg', 'gif']:
                files += [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith(ext)]

        total_files = len(files)
        if total_files == 0:
            messagebox.showerror("خطأ", "لم يتم العثور على ملفات للتحويل في المصدر.")
            return

        # التأكد من أن مجلد الوجهة موجود
        os.makedirs(destination_folder, exist_ok=True)

        progress_bar['value'] = 0
        progress_bar['maximum'] = total_files

        try:
            # البدء في ضغط الملفات
            for i, file in enumerate(files, 1):
                filename = os.path.basename(file)
                output_file = os.path.join(destination_folder, f"Safwan_{filename}")

                 # التحقق من وجود الملف بالفعل
                if os.path.exists(output_file):
                    result = messagebox.askyesno("تأكيد الاستبدال", f"موجود بالفعل. هل تريد إستبداله؟ '{output_file}' الملف")
                    if not result:
                        continue  # تجاوز هذا الملف إذا اختار المستخدم "لا"

                try:
                    if file.endswith(('mp4', 'mkv', 'avi', 'mov')):
                        # ضغط الفيديو
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-vcodec', 'libx264', '-acodec', 'aac', '-b:a', '64k', '-crf', '32', '-preset', 'medium', '-tune', 'film', output_file],
                            check=True
                        )
                    elif file.endswith(('mp3', 'wav', 'aac')):
                        # ضغط الصوت
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-acodec', 'aac', '-b:a', '64k', output_file],
                            check=True
                        )
                    elif file.endswith(('png', 'jpg', 'jpeg', 'gif')):
                        # تحويل الصور إلى WebP وضغطها
                        subprocess.run(
                            ['ffmpeg','-y', '-i', file, '-vcodec', 'libwebp', '-lossless', '0', '-compression_level', '6', '-q:v', '50', output_file],
                            check=True
                        )
                    else:
                        messagebox.showerror("خطأ", f".غير مدعومة {str(filename)} صيغة الملف")
                        return

                    # تحديث شريط التقدم
                    progress_bar['value'] = i
                    root.update_idletasks()

                except subprocess.CalledProcessError as e:
                    messagebox.showerror("خطأ", f"فشل معالجة الملف {filename}: {str(e)}")
                    continue

            messagebox.showinfo("نجاح", "! تمت عملية الضغط بنجاح")

            # تفريغ الحقول بعد إتمام الضغط
            source_folder_var.set("")
            destination_folder_var.set("")

        except Exception as e:
            messagebox.showerror("خطأ", f"{str(e)} : حدث خطأ أثناء المعالجة")
        finally:
            progress_bar['value'] = 0

    # إنشاء وتشغيل خيط جديد
    thread = threading.Thread(target=task)
    thread.start()


# إعداد واجهة المستخدم الرسومية
root = tk.Tk()
root.title("WebP تطبيق ضغط الملفات او تحويلها إلى")
root.geometry("1100x650")  # تحديد حجم الواجهة
root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

# تحديد المسار الصحيح للملفات عند تشغيل التطبيق بشكل مستقل
def resource_path(relative_path):
    """تحديد المسار للملفات المضمنة عند استخدام PyInstaller
    pyinstaller --onefile --noconsole --add-data "logo.ico;." --add-data "AI.jpg;." --icon=logo.ico Data_Augmentation.py
    """
    try:
        # إذا كان التطبيق يعمل من داخل PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # إذا كان يعمل في بيئة التطوير
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# تعيين الأيقونة للتطبيق إذا كانت موجودة
icon_path = resource_path("logo.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# إضافة صورة خلفية إذا كانت موجودة
background_path = resource_path("AI.jpg")
if os.path.exists(background_path):
    background_image = Image.open(background_path)  # فتح صورة الخلفية
    background_image = background_image.resize((1100, 650), Image.BICUBIC)  # تغيير حجم الصورة
    background_photo = ImageTk.PhotoImage(background_image)  # تحويل الصورة إلى PhotoImage لعرضها في Tkinter
    background_label = tk.Label(root, image=background_photo)  # إنشاء علامة (Label) لعرض الصورة
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # تحديد مكان وحجم الصورة في النافذة

# الحصول على حجم الشاشة
screen_width = root.winfo_screenwidth()

# حساب موقع النافذة المركزية
x_position = (screen_width - 1100) // 2
y_position = 0

# تحديد موقع النافذة المركزية
root.geometry(f"1100x650+{x_position}+{y_position}")

# متغيرات لحفظ المسارات المختارة
source_folder_var = tk.StringVar()
destination_folder_var = tk.StringVar()

# إنشاء مكان لعرض لتقسيم الواجهة  
fram = tk.Label(root)  # تعيين خلفية شفافة للإطار
fram.pack(pady=3)

# تسميات ومربعات الإدخال
tk.Label(fram, text="webp إختار المجلد أو الملف الذي تريد تقليل حجمه او تحويله إلى صيغة").grid(row=0, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار ملف", font=("Helvetica", 14), command=choose_source_file, width=10, height=1, bg="#3498db", fg="white").grid(row=1, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار مجلد", font=("Helvetica", 14), command=choose_source_folder, width=10, height=1, bg="#3498db", fg="white").grid(row=1, column=1, padx=10, pady=10)
tk.Entry(fram, textvariable=source_folder_var, width=90).grid(row=2, column=0, padx=10, pady=10)

tk.Label(fram, text="حدد المجلد الذي تريد حفظ الملفات المحولة فيه").grid(row=3, column=0, padx=10, pady=10)
tk.Entry(fram, textvariable=destination_folder_var, width=90).grid(row=4, column=0, padx=10, pady=10)
tk.Button(fram, text="تحديد مجلد للحفظ", font=("Helvetica", 14), command=choose_destination_folder, width=10, height=1, bg="#e67e22", fg="white").grid(row=4, column=1, padx=10, pady=10)

framButtons = tk.Label(fram)
framButtons.grid(row=5, column=0,columnspan=3, padx=10, pady=10)

tk.Label(framButtons, text="قم بالضغط على زر العملية التي تريد تطبيقها").grid(row=1, column=0,columnspan=3, padx=10, pady=10)
# زر التحويل
tk.Button(framButtons, text="webp التحويل الى", font=("Helvetica", 14), width=15, height=1, bg="#2ecc71", fg="white", command=convert_to_webp).grid(row=2, column=0, padx=10, pady=20)
# زر لضغط الملفات
tk.Button(framButtons, text="تقليل الحجم", font=("Helvetica", 14), width=15, height=1, bg="#2ecc71", fg="white", command=compress_files).grid(row=2, column=1, padx=10, pady=20)

# شريط التقدم
progress_bar = ttk.Progressbar(fram, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, padx=10, pady=20)

# إضافة شريط في أسفل الواجهة (Footer)
footer_label = tk.Label(root, text="تم التطوير بواسطة م/ صفوان سعدان", font=("Helvetica", 15), bg="#2c3e50", fg="white")
footer_label.pack(side="bottom", fill="x", pady=2)

# بدء التطبيق
root.mainloop()
