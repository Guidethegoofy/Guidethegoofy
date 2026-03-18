
import os
import glob
import base64
import struct

def get_png_dimensions(data):
    # PNG signature: 8 bytes
    # IHDR chunk: 4 bytes length, 4 bytes type ('IHDR'), 4 bytes width, 4 bytes height
    # Total offset directly to width: 8 + 4 + 4 = 16
    w, h = struct.unpack('>LL', data[16:24])
    return w, h

def create_animated_svg(input_dir, output_file):
    # Find all png files sorted by name
    frames = sorted(glob.glob(os.path.join(input_dir, "frame_*.png")))
    if not frames:
        print(f"No frames found in {input_dir}")
        return

    # Read dimensions from first frame
    with open(frames[0], 'rb') as f:
        data = f.read()
        width, height = get_png_dimensions(data)
    
    encoded_frames = []
    for frame in frames:
        with open(frame, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            encoded_frames.append(encoded)

    num_frames = len(encoded_frames)
    
    # User requested approx 4.0 FPS
    fps = 4.0
    duration_per_frame = 1.0 / fps # 0.25 seconds
    
    total_duration = num_frames * duration_per_frame
    
    # CSS animation percentages
    # Each frame is visible for 1/N of the time
    step_percent = 100.0 / num_frames
    
    svg_content = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .frame {{
      animation: fade {total_duration}s infinite step-end;
      opacity: 0;
    }}
'''
    
    for i in range(num_frames):
        # Calculate delay so frame starts at correct time
        delay = i * duration_per_frame
        svg_content += f'''    .frame:nth-child({i+1}) {{
      animation-delay: {delay}s;
    }}
'''

    # Using step-end for cleaner frame transitions if supported, or linear with hard stops
    # The previous logic used linear stops:
    # 0%, {step_percent}% {{ opacity: 1; }}
    # {step_percent + 0.01}%, 100% {{ opacity: 0; }}
    
    svg_content += f'''
    @keyframes fade {{
      0%, {step_percent}% {{ opacity: 1; }}
      {step_percent + 0.001}%, 100% {{ opacity: 0; }}
    }}
  </style>
'''
    
    for encoded in encoded_frames:
        svg_content += f'  <image href="data:image/png;base64,{encoded}" width="{width}" height="{height}" class="frame" />\n'
    
    svg_content += '</svg>'
    
    with open(output_file, 'w') as f:
        f.write(svg_content)
    print(f"Generated {output_file} with {num_frames} frames at {fps} FPS (total duration {total_duration:.2f}s).")

if __name__ == "__main__":
    input_dir = "../Yuchan_Idle"
    output_file = "yuchan_idle.svg"
    create_animated_svg(input_dir, output_file)
