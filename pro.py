import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # استيراد مكتبتي PIL للتعامل مع الصور و ImageTk لعرض الصور في Tkinter
import subprocess
import threading

# دالة لاختيار الملف المصدر
def choose_source_file():
    file = filedialog.askopenfilename(
        title="اختر ملف للتحويل",
        filetypes=(("All Files", "*.*"), ("Images", "*.png;*.jpg;*.jpeg;*.gif"), ("Videos", "*.mp4;*.mkv;*.avi;*.mov"))
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
def convert_files():
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

                try:
                    # فحص مدة الفيديو
                    if file.endswith(('mp4', 'mkv', 'avi', 'mov')):
                        result = subprocess.run(
                            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file],
                            capture_output=True, text=True
                        )
                        duration = float(result.stdout.strip()) if result.returncode == 0 else 0

                        if duration > 90:  # أكثر من دقيقة ونص
                            compressed_file = os.path.join(destination_folder, f"{os.path.splitext(filename)[0]}_Safwan.mp4")
                            subprocess.run(
                                ['ffmpeg', '-i', file, '-vcodec', 'libx264', '-acodec', 'aac', '-b:a', '64k', '-crf', '32', '-preset', 'medium', '-tune', 'film', compressed_file],
                                check=True
                            )
                            continue

                    # أمر ffmpeg للتحويل بناءً على نوع الملف
                    if file.endswith(('png', 'jpg', 'jpeg')):
                        subprocess.run(
                            ['ffmpeg', '-i', file, '-vcodec', 'libwebp', '-lossless', '0',
                             '-compression_level', '6', '-q:v', '50', output_file],
                            check=True
                        )
                    elif file.endswith('gif'):
                        subprocess.run(
                            ['ffmpeg', '-i', file, '-vcodec', 'libwebp', '-vf', 'scale=640:-1', '-lossless', '0',
                             '-compression_level', '6', '-q:v', '50', '-loop', '0', output_file],
                            check=True
                        )
                    elif file.endswith(('mp4', 'mkv', 'avi', 'mov')):
                        subprocess.run(
                            ['ffmpeg', '-i', file, '-vcodec', 'libwebp', '-vf', 'scale=640:-1,fps=15', '-lossless', '0',
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


# إعداد واجهة المستخدم الرسومية
root = tk.Tk()
root.title("WebP تطبيق تحويل الملفات إلى صيغة")
root.geometry("1100x650")  # تحديد حجم الواجهة
root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

# تعيين الأيقونة للتطبيق
root.iconbitmap("logo.ico")

# إضافة صورة خلفية
background_image = Image.open("AI.jpg")  # فتح صورة الخلفية
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
tk.Label(fram, text="webp إختار المجلد أو الملف الذي تريد تحويله إلى صيغة").grid(row=0, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار ملف", font=("Helvetica", 14), command=choose_source_file, width=10, height=1, bg="#3498db", fg="white").grid(row=1, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار مجلد", font=("Helvetica", 14), command=choose_source_folder, width=10, height=1, bg="#3498db", fg="white").grid(row=1, column=1, padx=10, pady=10)
tk.Entry(fram, textvariable=source_folder_var, width=90).grid(row=2, column=0, padx=10, pady=10)

tk.Label(fram, text="حدد المجلد الذي تريد حفظ الملفات المحولة فيه").grid(row=3, column=0, padx=10, pady=10)
tk.Entry(fram, textvariable=destination_folder_var, width=90).grid(row=4, column=0, padx=10, pady=10)
tk.Button(fram, text="تحديد مجلد للحفظ", font=("Helvetica", 14), command=choose_destination_folder, width=10, height=1, bg="#e67e22", fg="white").grid(row=4, column=1, padx=10, pady=10)

# زر التحويل
tk.Button(fram, text="بدء التحويل", font=("Helvetica", 14), width=25, height=1, bg="#2ecc71", fg="white", command=convert_files).grid(row=5, column=0, padx=10, pady=20)

# شريط التقدم
progress_bar = ttk.Progressbar(fram, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, padx=10, pady=20)

# إضافة شريط في أسفل الواجهة (Footer)
footer_label = tk.Label(root, text="تم التطوير بواسطة م/ صفوان سعدان", font=("Helvetica", 15), bg="#2c3e50", fg="white")
footer_label.pack(side="bottom", fill="x", pady=2)

# بدء التطبيق
root.mainloop()
