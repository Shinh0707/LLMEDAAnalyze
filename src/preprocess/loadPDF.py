import pymupdf4llm
import os
import glob
from tqdm import tqdm

def load(file: str):
    return pymupdf4llm.to_markdown(file)

def load_all(dir: str, cache_dir: str):
    os.makedirs(cache_dir, exist_ok=True)
    
    texts = []
    pdf_files = glob.glob(os.path.join(dir, "*.pdf"))
    
    for pdf_file in tqdm(pdf_files, desc=dir):
        filename = os.path.splitext(os.path.basename(pdf_file))[0] + ".txt"
        cache_path = os.path.join(cache_dir, filename)
        if os.path.exists(cache_path):
            continue
        
        text = load(pdf_file)
        texts.append(text)
        
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
    
    return texts

if __name__ == "__main__":
    pdf_dir = "PDF"
    cache_dir = "PDF/cache"

    def EDA_load_all(folder_name:str):
        directory = os.path.join(pdf_dir,folder_name)   
        cachedir = os.path.join(cache_dir,folder_name)
        load_all(directory, cachedir) 
    
    EDA_load_all("hasEDA")
    EDA_load_all("littleEDA")
    EDA_load_all("notEDA")
    EDA_load_all("ECSympo/EC2022")
    EDA_load_all("ECSympo/EC2023")
    EDA_load_all("ECSympo/EC2024")