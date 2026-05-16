"""
Lit le canvas base64 depuis localStorage (via fichier temp) et sauvegarde screenshot2.png
Usage: passer l'URL de la page en 1er argument si besoin.
Ici on lit directement via Playwright Python.
"""
from playwright.sync_api import sync_playwright
import base64, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'img', 'screenshot2.png')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    
    # Charge indexadmin
    url = 'file:///C:/Users/mguitter/Documents/NW%20kids%20wytop%20-%20Copie/indexadmin.html'
    page.goto(url)
    page.wait_for_timeout(3000)
    
    # Cache l'overlay rotation, lance le niveau 4
    page.add_style_tag(content='#rotate-overlay { display: none !important; }')
    page.evaluate("if (typeof showLevelSelect === 'function') showLevelSelect();")
    page.wait_for_timeout(500)
    page.evaluate("if (typeof startLevel === 'function') startLevel(4);")
    page.wait_for_timeout(4000)
    
    # Resize canvas + redraw
    page.evaluate("""
        const canvas = document.getElementById('gameCanvas');
        if (canvas) {
            canvas.style.display = 'block';
            canvas.style.width = '1280px';
            canvas.style.height = '688px';
        }
        window.dispatchEvent(new Event('resize'));
        if (typeof resizeCanvas === 'function') resizeCanvas();
    """)
    page.wait_for_timeout(2000)
    
    # Screenshot de la page entière
    page.screenshot(path=OUT, clip={'x': 0, 'y': 0, 'width': 1280, 'height': 720})
    print(f'Saved {OUT}')
    browser.close()
