import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageSequence
import math
import os

# Define translations
translations = {
    "en": {
        "select_gif": "Select GIF File:",
        "original_fps": "Original FPS:",
        "new_fps": "New FPS Value:",
        "size": "Size (power of two):",
        "start": "Start",
        "success": "Success",
        "success_message": "Process completed successfully.",
        "error": "Error",
        "file_selection_error": "Please select a GIF file.",
        "duration_error": "Unable to determine GIF duration.",
        "fps_error": "Please enter a value less than the original FPS and greater than or equal to 1.",
        "size_error": "Please enter a power of two value."
    },
    "tr": {
        "select_gif": "GIF Dosyası Seç:",
        "original_fps": "Original FPS:",
        "new_fps": "Yeni FPS Değeri:",
        "size": "Boyut (ikinin üssü):",
        "start": "Başlat",
        "success": "Başarılı",
        "success_message": "İşlem başarıyla tamamlandı.",
        "error": "Hata",
        "file_selection_error": "Lütfen bir GIF dosyası seçin.",
        "duration_error": "GIF dosyasının süresi belirlenemedi.",
        "fps_error": "Lütfen orijinal FPS değerinden düşük ve 1 veya daha fazla bir değer girin.",
        "size_error": "Lütfen ikinin üssü bir değer girin."
    },
    "es": {
        "select_gif": "Seleccionar archivo GIF:",
        "original_fps": "FPS original:",
        "new_fps": "Nuevo valor de FPS:",
        "size": "Tamaño (potencia de dos):",
        "start": "Iniciar",
        "success": "Éxito",
        "success_message": "Proceso completado con éxito.",
        "error": "Error",
        "file_selection_error": "Por favor seleccione un archivo GIF.",
        "duration_error": "No se puede determinar la duración del GIF.",
        "fps_error": "Ingrese un valor menor que el FPS original y mayor o igual a 1.",
        "size_error": "Ingrese un valor que sea potencia de dos."
    },
    "ru": {
        "select_gif": "Выбрать файл GIF:",
        "original_fps": "Оригинальный FPS:",
        "new_fps": "Новое значение FPS:",
        "size": "Размер (степень двойки):",
        "start": "Начать",
        "success": "Успех",
        "success_message": "Процесс успешно завершен.",
        "error": "Ошибка",
        "file_selection_error": "Пожалуйста, выберите файл GIF.",
        "duration_error": "Не удается определить продолжительность GIF.",
        "fps_error": "Введите значение меньше оригинального FPS и больше или равно 1.",
        "size_error": "Введите значение степени двойки."
    },
    "zh": {
        "select_gif": "选择 GIF 文件：",
        "original_fps": "原始 FPS:",
        "new_fps": "新 FPS 值：",
        "size": "大小（二的幂）：",
        "start": "开始",
        "success": "成功",
        "success_message": "处理成功完成。",
        "error": "错误",
        "file_selection_error": "请选择一个 GIF 文件。",
        "duration_error": "无法确定 GIF 的持续时间。",
        "fps_error": "请输入小于原始 FPS 且大于或等于 1 的值。",
        "size_error": "请输入二的幂值。"
    }
}

# Set default language
current_language = "tr"

def set_language(lang):
    global current_language
    current_language = lang
    update_texts()

def update_texts():
    labels = translations[current_language]
    select_gif_label.config(text=labels["select_gif"])
    original_fps_label.config(text=f"{labels['original_fps']}: {original_fps_var.get()}")
    new_fps_label.config(text=labels["new_fps"])
    size_label.config(text=labels["size"])
    start_button.config(text=labels["start"])

def is_power_of_two(n):
    return (n > 0) and (n & (n - 1)) == 0

def process_gif(gif_path, new_fps, size_input):
    try:
        # Open the GIF file
        gif = Image.open(gif_path)
        frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]

        # Get FPS (frames per second) of the GIF
        try:
            duration = gif.info['duration']
            if duration > 0:
                original_fps = 1000 / duration
            else:
                original_fps = 0
        except KeyError:
            duration = 0
            original_fps = 0

        # Calculate frame skipping step
        step = int(original_fps / new_fps)

        # Select frames based on the new FPS
        new_frames = frames[::step]

        # Calculate the new duration per frame to maintain the total GIF length
        new_duration = int(1000 / new_fps)

        # Save the new GIF with the selected frames and new FPS
        new_gif_path = os.path.splitext(gif_path)[0] + "_new_fps.gif"
        new_frames[0].save(new_gif_path, save_all=True, append_images=new_frames[1:], duration=new_duration, loop=0)
        gif = Image.open(new_gif_path)
        frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]

        # Resize all frames to the specified size
        resized_frames = []
        for frame in frames:
            resized_frame = frame.resize((size_input, size_input), resample=Image.LANCZOS)
            resized_frames.append(resized_frame)

        # Determine the best grid dimensions
        total_frames = len(resized_frames)
        columns = int(math.sqrt(total_frames))
        rows = math.ceil(total_frames / columns)

        # Create a directory based on the GIF file name in its containing folder
        gif_folder_path = os.path.dirname(gif_path)
        gif_folder_name = os.path.splitext(os.path.basename(gif_path))[0] + "_gif"
        gif_folder_full_path = os.path.join(gif_folder_path, gif_folder_name)
        os.makedirs(gif_folder_full_path, exist_ok=True)

        # Initialize the combined image
        combined_width = size_input * columns
        combined_height = size_input * rows
        combined_image = Image.new('RGB', (combined_width, combined_height))

        # Paste frames into the combined image
        frame_num = 0
        for frame in resized_frames:
            col_index = frame_num % columns
            row_index = frame_num // columns
            x_offset = col_index * size_input
            y_offset = row_index * size_input
            combined_image.paste(frame, (x_offset, y_offset))
            frame_num += 1

        # Save the combined image
        combined_image_path = os.path.join(gif_folder_full_path, 'combined_image.png')
        combined_image.save(combined_image_path)
        print(f"Combined image saved: {combined_image_path}")

        # Create and write to the .vmat file
        vmat_file_path = os.path.join(gif_folder_full_path, f"{os.path.splitext(os.path.basename(gif_path))[0]}.vmat")
        with open(vmat_file_path, 'w') as vmat_file:
            vmat_file.write("// THIS FILE IS AUTO-GENERATED\n\n")
            vmat_file.write('Layer0\n{\n')
            vmat_file.write('\tshader "csgo_complex.vfx"\n\n')
            vmat_file.write('\t//---- Animation ----\n')
            vmat_file.write(f'\tF_TEXTURE_ANIMATION 1\n')
            vmat_file.write('\t//---- Ambient Occlusion ----\n')
            vmat_file.write('\tTextureAmbientOcclusion "materials/default/default_ao.tga"\n\n')
            vmat_file.write('\t//---- Color ----\n')
            vmat_file.write('\tg_flModelTintAmount "1.000"\n')
            vmat_file.write('\tg_flTexCoordRotation "0.000"\n')
            vmat_file.write('\tg_nScaleTexCoordUByModelScaleAxis "0" // None\n')
            vmat_file.write('\tg_nScaleTexCoordVByModelScaleAxis "0" // None\n')
            vmat_file.write('\tg_vColorTint "[1.000000 1.000000 1.000000 0.000000]"\n')
            vmat_file.write(f'\tTextureColor "combined_image.png"\n\n')
            vmat_file.write('\t//---- Fog ----\n')
            vmat_file.write('\tg_bFogEnabled "1"\n\n')
            vmat_file.write('\t//---- Lighting ----\n')
            vmat_file.write('\tg_flMetalness "0.000"\n')
            vmat_file.write('\tTextureRoughness "materials/default/default_rough.tga"\n\n')
            vmat_file.write('\t//---- Normal Map ----\n')
            vmat_file.write('\tTextureNormal "materials/default/default_normal.tga"\n\n')
            vmat_file.write('\t//---- Texture Address Mode ----\n')
            vmat_file.write('\tg_nTextureAddressModeU "0" // Wrap\n')
            vmat_file.write('\tg_nTextureAddressModeV "0" // Wrap\n\n')
            vmat_file.write('\t//---- Texture Animation ----\n')
            vmat_file.write('\tg_flAnimationFrame "0.000"\n')
            vmat_file.write('\tg_flAnimationTimeOffset "0.000"\n\n')
            vmat_file.write(f'\tg_flAnimationTimePerFrame "{1/new_fps:.3f}"\n')
            vmat_file.write(f'\tg_nNumAnimationCells "{total_frames}"\n')
            vmat_file.write(f'\tg_vAnimationGrid "[{columns} {rows}]"\n\n')
            vmat_file.write('}\n')

        print(f".vmat file saved: {vmat_file_path}")
        messagebox.showinfo(translations[current_language]["success"], translations[current_language]["success_message"])
    except Exception as e:
        messagebox.showerror(translations[current_language]["error"], f"{translations[current_language]['error']}: {e}")

def select_gif():
    file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
    if file_path:
        gif_path_var.set(file_path)
        try:
            duration = Image.open(file_path).info['duration']
            original_fps = 1000 / duration
            original_fps_var.set(f"{translations[current_language]['original_fps']}: {original_fps:.2f}")
        except KeyError:
            messagebox.showerror(translations[current_language]["error"], translations[current_language]["duration_error"])
            gif_path_var.set("")
            original_fps_var.set(translations[current_language]["original_fps"])

def start_processing():
    gif_path = gif_path_var.get()
    new_fps = int(fps_entry.get())
    size_input = int(size_var.get())

    if not gif_path:
        messagebox.showerror(translations[current_language]["error"], translations[current_language]["file_selection_error"])
        return

    try:
        duration = Image.open(gif_path).info['duration']
        original_fps = 1000 / duration
    except KeyError:
        messagebox.showerror(translations[current_language]["error"], translations[current_language]["duration_error"])
        return

    if new_fps < 1 or new_fps > original_fps:
        messagebox.showerror(translations[current_language]["error"], translations[current_language]["fps_error"])
        return

    if not is_power_of_two(size_input):
        messagebox.showerror(translations[current_language]["error"], translations[current_language]["size_error"])
        return

    process_gif(gif_path, new_fps, size_input)

# Create the GUI
root = tk.Tk()
root.title("GIF2VMAT by dotthegod")

gif_path_var = tk.StringVar()
original_fps_var = tk.StringVar(value=translations[current_language]["original_fps"])

# GUI Layout
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

select_gif_label = tk.Label(frame, text=translations[current_language]["select_gif"])
select_gif_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
gif_path_entry = tk.Entry(frame, textvariable=gif_path_var, width=50)
gif_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
tk.Button(frame, text="Select", command=select_gif).grid(row=0, column=2, padx=10, pady=10)

original_fps_label = tk.Label(frame, textvariable=original_fps_var)
original_fps_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='w')

new_fps_label = tk.Label(frame, text=translations[current_language]["new_fps"])
new_fps_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
fps_entry = tk.Entry(frame)
fps_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

size_label = tk.Label(frame, text=translations[current_language]["size"])
size_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
size_var = tk.StringVar()
size_var.set("512")
size_options = ["64", "128", "256", "512", "1024", "2048", "4096"]
size_menu = tk.OptionMenu(frame, size_var, *size_options)
size_menu.grid(row=3, column=1, padx=10, pady=10, sticky='w')

start_button = tk.Button(frame, text=translations[current_language]["start"], command=start_processing)
start_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Language selection menu
def change_language(*args):
    set_language(language_var.get())

language_var = tk.StringVar(value="tr")
language_menu = tk.OptionMenu(frame, language_var, *translations.keys())
language_menu.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
language_var.trace("w", change_language)

update_texts()
root.mainloop()
