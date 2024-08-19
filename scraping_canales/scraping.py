import json
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from scraping_peliculas_series.utils.feth_utils import (
    fetch_html#, extract_data, scrape_series
)

HEADERS = {
        "User-Agent": "python-requests/2.32.3"
}

async def scrape_series(session, url):
    """Scrapes the series from the given URL and returns the title and description."""
    html_content = await fetch_html(session, url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        seccion = soup.find('div', class_="inner")
        titulo = seccion.find('h2').get_text(strip=True) if seccion.find('h2') else "No encontrado"
        descripcion = seccion.find('p').get_text(strip=True) if seccion.find('p') else "No encontrada"
        return titulo, descripcion
    return "No encontrado", "No encontrada"

async def process_data(session, data):
    """Processes the data, scrapes information from series, and updates the data structure."""
    tasks = []

    for key in data.keys():
        for item in data[key]:
            original_link = item['link']
            print(f'link = "{original_link}"')
            tasks.append(scrape_series(session, original_link))

    print('Esperando a que todas las tareas se completen...')
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print('Todas las tareas completadas o con errores capturados.')

    index = 0
    for key in data.keys():
        for item in data[key]:
            result = results[index]
            if isinstance(result, Exception):
                print(f"Error processing {item['link']}: {result}")
                titulo, descripcion = "Error encontrado", "Descripción no disponible"
            else:
                titulo, descripcion = result
            item['canal'] = titulo
            item['descripcion'] = descripcion
            index += 1
    return data

def save_data(data, filename):
    """Saves the updated data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

async def main():
    
    
    
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'resultados.json')
    output_file_path = os.path.join(current_directory, 'resultados_actualizados.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        updated_data = await process_data(session, data)

    save_data(updated_data, output_file_path)

if __name__ == "__main__":
    asyncio.run(main())
