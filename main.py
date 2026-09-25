import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse

app = FastAPI(title="Saudi Map Contour Particle Animation")

def get_map_contour_particles(width=1080, height=1920, num_particles=3000):
    """
    توليد إحداثيات جسيمات ترسم حدود خريطة المملكة (مفرغة من الداخل)
    """
    img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(img)

    # رسم شكل مبسط يمثل حدود خريطة المملكة كـ Polygon
    # (نقاط الإحداثيات التقريبية لحدود الخريطة)
    map_points = [
        (width * 0.35, height * 0.35), # الشمال الغربي (تبوك/حقل)
        (width * 0.55, height * 0.34), # الشمال الشرقي (طريف/عرعر)
        (width * 0.70, height * 0.38), # حفر الباطن
        (width * 0.78, height * 0.48), # المنطقة الشرقية / القطيف
        (width * 0.75, height * 0.58), # سلوى / حدود قطر والإمارات
        (width * 0.65, height * 0.68), # الربع الخالي الشرقي
        (width * 0.50, height * 0.68), # حدود اليمن الشرقية
        (width * 0.38, height * 0.62), # نجران / جازان
        (width * 0.32, height * 0.52), # عسير / مكة / جدة
        (width * 0.28, height * 0.42), # ينبع / الوجه
    ]
    
    # رسم حدود الخريطة فقط (سمك الخط 8 بكسل ليكون مفرغ من الداخل)
    draw.polygon(map_points, outline=255, width=8)

    img_np = np.array(img)
    y_indices, x_indices = np.where(img_np > 128)

    if len(x_indices) == 0:
        return np.random.rand(num_particles, 2) * [width, height]

    # توزيع الجسيمات على الحدود فقط
    choice = np.random.choice(len(x_indices), num_particles, replace=True)
    target_points = np.column_stack((x_indices[choice], y_indices[choice]))
    return target_points

def generate_map_video(output_path: str):
    width, height = 1080, 1920
    fps = 30
    duration_sec = 4
    total_frames = fps * duration_sec
    num_particles = 3500

    # الإحداثيات المستهدفة: حدود الخريطة المجوفة
    target_pos = get_map_contour_particles(width, height, num_particles)

    # الإحداثيات الأولية: نقاط عشوائية متفرقة
    start_pos = np.random.rand(num_particles, 2) * [width, height]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # اللون الأخضر الهوياتي (#42E695 -> BGR)
    particle_color = (149, 230, 66)

    for frame in range(total_frames):
        t = frame / float(total_frames)
        t_smooth = 1 - (1 - t) ** 3  # حركة انسيابية Ease-out

        current_pos = (1 - t_smooth) * start_pos + t_smooth * target_pos
        img_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # رسم الجسيمات الخضراء
        for p in current_pos.astype(int):
            px, py = p[0], p[1]
            if 0 <= px < width and 0 <= py < height:
                cv2.circle(img_frame, (px, py), 2, particle_color, -1)

        out.write(img_frame)

    out.release()

@app.get("/")
def home():
    return {"message": "Saudi Map Particle Generator"}

@app.get("/generate-map")
def create_map_video(background_tasks: BackgroundTasks):
    output_filename = "saudi_map_contour.mp4"
    generate_map_video(output_filename)

    background_tasks.add_task(lambda: os.remove(output_filename) if os.path.exists(output_filename) else None)
    return FileResponse(output_filename, media_type="video/mp4", filename=output_filename)
