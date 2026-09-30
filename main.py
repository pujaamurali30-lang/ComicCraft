import os
import urllib.parse
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_pollinations_url(prompt: str, style: str, panel_num: int, character: str) -> str:
    style_configs = {
        "fantasy": {
            "prompt": "enchanted magical forest, glowing violet and cyan flowers, ethereal fantasy digital painting, intricate detail",
            "seed_offset": 1000
        },
        "comic": {
            "prompt": "classic comic book panel, strong black ink outlines, halftones, retro marvel and dc graphic novel aesthetic",
            "seed_offset": 2000
        },
        "anime": {
            "prompt": "high quality modern anime artwork, makoto shinkai aesthetic, vivid colors, detailed background, cinematic studio ghibli lighting",
            "seed_offset": 3000
        },
        "cartoon": {
            "prompt": "3d pixar disney style render, cute character design, soft glossy lighting, vibrant cartoon animation scene",
            "seed_offset": 4000
        },
        "cyberpunk": {
            "prompt": "neon cyberpunk visual style, futuristic city backdrop, glowing magenta and teal neon lights, dark moody atmosphere",
            "seed_offset": 5000
        },
        "noir": {
            "prompt": "1940s film noir style, monochrome, high contrast black and white, dramatic shadows, moody detective story setting",
            "seed_offset": 6000
        },
        "pixel": {
            "prompt": "16-bit pixel art style, retro video game graphics, detailed pixelated landscape and character art",
            "seed_offset": 7000
        },
        "scifi": {
            "prompt": "epic science fiction art, alien planet landscape, glowing cosmic nebulae, futuristic technology and spaceships",
            "seed_offset": 8000
        },
        "chibi": {
            "prompt": "super cute chibi character, oversized head, adorable expressive eyes, pastel colors, soft whimsical illustration",
            "seed_offset": 9000
        },
        "watercolor": {
            "prompt": "expressive watercolor painting, soft pastel color bleeds, fine ink line art sketch, artistic canvas texture",
            "seed_offset": 10000
        }
    }

    config = style_configs.get(style.lower(), style_configs["fantasy"])
    full_prompt = f"{prompt}, featuring hero character {character}, panel {panel_num}, {config['prompt']}"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    seed = config["seed_offset"] + (panel_num * 107) + len(prompt)
    
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=350&nologo=true&seed={seed}"

def create_pdf(panels, style_name):
    pdf = FPDF()
    for p in panels:
        pdf.add_page()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, f"ComicCraft - {style_name.title()} Edition", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 10, f"Panel {p['panel_num']}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, f"Story: {p['narration']}")
        pdf.set_font("Arial", "I", 12)
        pdf.multi_cell(0, 8, f"Dialogue: {p['dialogue']}")
    filepath = "comic_story.pdf"
    pdf.output(filepath)
    return filepath

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ComicCraft - AI Comic Creator</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1e1e2f 0%, #0f0c20 100%); padding: 20px; color: #fff; }
        .card { max-width: 800px; margin: 20px auto; background: #252836; padding: 30px; border-radius: 16px; border: 2px solid #3b3f54; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { text-align: center; font-size: 32px; color: #ff79c6; text-transform: uppercase; margin-bottom: 5px; }
        .sub { text-align: center; color: #8be9fd; margin-bottom: 25px; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #bd93f9; }
        input, select, textarea { width: 100%; padding: 12px; margin-top: 6px; border-radius: 8px; border: 1px solid #44475a; background: #191a21; color: #f8f8f2; box-sizing: border-box; font-size: 15px; }
        button { background: linear-gradient(90deg, #ff5555 0%, #ff79c6 100%); color: white; border: none; padding: 14px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 20px; text-transform: uppercase; }
        button:hover { opacity: 0.9; }
        .comic-panel { background: #191a21; border: 2px solid #6272a4; padding: 15px; margin-top: 20px; border-radius: 12px; }
        .comic-panel img { width: 100%; min-height: 250px; background-color: #282a36; border-radius: 8px; border: 2px solid #44475a; margin-top: 10px; display: block; object-fit: cover; }
        .download-btn { background: linear-gradient(90deg, #50fa7b 0%, #8be9fd 100%); color: #000; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎨 ComicCraft</h1>
        <div class="sub">Generate Real AI Comic Panels</div>
        <form id="comicForm">
            <label>Story Prompt:</label>
            <textarea id="prompt" rows="3" required>A young girl in a magical dress walking through an enchanted forest with glowing purple and blue flowers</textarea>
            
            <label>Character Name:</label>
            <input type="text" id="character_name" value="Aria" required>
            
            <label>Select Visual Style:</label>
            <select id="art_style">
                <option value="fantasy">1. Fantasy / Enchanted Magic</option>
                <option value="comic">2. Classic Graphic Novel</option>
                <option value="anime">3. Detailed Anime</option>
                <option value="cartoon">4. 3D Pixar Cartoon</option>
                <option value="cyberpunk">5. Neon Cyberpunk</option>
                <option value="noir">6. Film Noir</option>
                <option value="pixel">7. Pixel Art</option>
                <option value="scifi">8. Sci-Fi Space</option>
                <option value="chibi">9. Cute Chibi</option>
                <option value="watercolor">10. Watercolor Painting</option>
            </select>
            
            <button type="submit">✨ Generate AI Comic</button>
        </form>
        
        <div id="output"></div>
        
        <form action="/download-pdf" method="post" id="pdfForm" style="display:none;">
            <input type="hidden" name="art_style" id="pdf_style" value="fantasy">
            <button type="submit" class="download-btn">📥 Download Comic as PDF</button>
        </form>
    </div>

    <script>
        document.getElementById('comicForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            btn.innerText = '⚡ Generating AI Artwork...';
            btn.disabled = true;

            const formData = new FormData();
            formData.append('prompt', document.getElementById('prompt').value);
            formData.append('character_name', document.getElementById('character_name').value);
            const style = document.getElementById('art_style').value;
            formData.append('art_style', style);
            document.getElementById('pdf_style').value = style;

            try {
                const res = await fetch('/generate-comic', { method: 'POST', body: formData });
                const data = await res.json();
                
                // Cache buster: appended timestamp ensures browser reloads the image every time
                const timestamp = Date.now();

                let html = `<h2 style="text-align:center; color:#ff79c6; margin-top:25px;">📖 ${data.title}</h2>`;
                data.panels.forEach(p => {
                    const freshImageUrl = `${p.image_url}&t=${timestamp}`;
                    html += `
                        <div class="comic-panel">
                            <h3>Panel ${p.panel_num} (${p.style_name})</h3>
                            <p><strong>Narration:</strong> ${p.narration}</p>
                            <p><strong>Dialogue:</strong> <em>"${p.dialogue}"</em></p>
                            <img src="${freshImageUrl}" alt="AI Generated Image" onerror="this.onerror=null; this.src='https://picsum.photos/600/350';">
                        </div>
                    `;
                });
                document.getElementById('output').innerHTML = html;
                document.getElementById('pdfForm').style.display = 'block';
            } catch (err) {
                console.error(err);
                alert('An error occurred while generating comic panels.');
            } finally {
                btn.innerText = '✨ Generate AI Comic';
                btn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return UI_HTML

@app.post("/generate-comic")
async def generate_comic(
    prompt: str = Form(...),
    character_name: str = Form("Aria"),
    art_style: str = Form("fantasy")
):
    url1 = get_pollinations_url(prompt, art_style, 1, character_name)
    url2 = get_pollinations_url(prompt, art_style, 2, character_name)

    return {
        "status": "success",
        "title": f"The Adventure of {character_name}",
        "style": art_style,
        "panels": [
            {
                "panel_num": 1,
                "style_name": art_style.title(),
                "narration": f"{character_name} steps into the scene: {prompt}.",
                "dialogue": f"{character_name}: 'This place is full of mystery!'",
                "image_url": url1
            },
            {
                "panel_num": 2,
                "style_name": art_style.title(),
                "narration": f"Continuing deeper into the world, {character_name} makes a new discovery.",
                "dialogue": f"{character_name}: 'I must keep exploring!'",
                "image_url": url2
            }
        ]
    }

@app.post("/download-pdf")
async def download_pdf(art_style: str = Form("fantasy")):
    panels = [
        {"panel_num": 1, "narration": "The journey begins.", "dialogue": "Hero: 'Ready!'"},
        {"panel_num": 2, "narration": "The story unfolds.", "dialogue": "Hero: 'Found it!'"}
    ]
    pdf_path = create_pdf(panels, art_style)
    return FileResponse(pdf_path, filename=f"ComicCraft_{art_style}.pdf", media_type="application/pdf")