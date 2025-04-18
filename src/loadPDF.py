import pymupdf4llm
import os
import glob

def load(file: str):
    return pymupdf4llm.to_markdown(file)

def load_all(dir: str, cache_dir: str):
    os.makedirs(cache_dir, exist_ok=True)
    
    texts = []
    pdf_files = glob.glob(os.path.join(dir, "*.pdf"))
    
    for pdf_file in pdf_files:
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
    has_EDAdir = os.path.join(pdf_dir,"hasEDA")
    has_EDA_cachedir = os.path.join(cache_dir,"hasEDA")
    little_EDAdir = os.path.join(pdf_dir,"littleEDA")
    little_EDA_cachedir = os.path.join(cache_dir,"littleEDA")
    not_EDAdir = os.path.join(pdf_dir,"notEDA")
    not_EDA_cachedir = os.path.join(cache_dir,"notEDA")
    test_dir = os.path.join(pdf_dir,"test")
    test_cachedir = os.path.join(cache_dir,"test")
    load_all(has_EDAdir, has_EDA_cachedir)
    load_all(not_EDAdir, not_EDA_cachedir)
    load_all(little_EDAdir, little_EDA_cachedir)
    load_all(test_dir, test_cachedir)