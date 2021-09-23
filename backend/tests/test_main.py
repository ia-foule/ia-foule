from fastapi.testclient import TestClient
from pathlib import Path

from main import app

client = TestClient(app)

def test_predict_on_url():
    url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Foule_au_march%C3%A9_hebdomadaire_de_Fasintsara.JPG/1200px-Foule_au_march%C3%A9_hebdomadaire_de_Fasintsara.JPG'
    response = client.get("/prediction/?url="+url)
    assert response.status_code == 200
    assert response.json() == {'nb_person': 127}

def test_predict_on_image():
    img_path = Path(__file__).resolve().parent / 'data/IMG_1.jpg'
    response = client.post(
        "/image", files={"file": ("filename", img_path.open("rb"), "image/jpeg")}
    )
    assert response.status_code == 200
    assert response.json() == {'nb_person': 37}
