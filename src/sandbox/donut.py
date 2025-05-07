from vila.pdftools.pdf_extractor import PDFExtractor
from transformers.pipelines import pipeline
from PIL import Image
import torch

# ① モデルのロード（DocVQA 用に微調整済みモデル）
pipe = pipeline(
    task="document-question-answering",
    model="naver-clova-ix/donut-base-finetuned-docvqa",
    device=0 if torch.cuda.is_available() else -1
)

# ② 画像を読み込む (PDF→PNG などに変換済み)
pdf_extractor = PDFExtractor("pdfplumber")
page_tokens, page_images = pdf_extractor.load_tokens_and_image("./PDF/Mustango.pdf")
image = page_images[0].convert("RGB")

# ③ 「Introduction を抽出して」という質問で投げる
result = pipe(image=image,
              question="What is the title of this document?")

print(result)
