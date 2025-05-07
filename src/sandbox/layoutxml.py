import torch
from transformers.models.layoutxlm import LayoutXLMProcessor
from transformers.models.auto.modeling_auto import AutoModelForTokenClassification
from vila.pdftools.pdf_extractor import PDFExtractor

# 1) デバイス設定（MPS がなければ CPU）
device = torch.device("mps" if torch.mps.is_available() else "cpu")

# 2) PDF→トークン＋ページ画像を抽出
pdf_extractor = PDFExtractor("pdfplumber")
page_tokens, page_images = pdf_extractor.load_tokens_and_image("./PDF/hasEDA/IPSJ-EC2024002.pdf")
tokens = page_tokens[0].tokens   # 1ページ目を使う例
image  = page_images[0]   # PIL.Image.Image

# トークンリストから words/bboxes を用意
words = [t.text for t in tokens]
boxes = [t.block for t in tokens]

# 3) Processor とモデルのロード
processor = LayoutXLMProcessor.from_pretrained("microsoft/layoutxlm-base")
model = AutoModelForTokenClassification.from_pretrained(
    "microsoft/layoutxlm-base",
    num_labels=12   # DocBank など12クラスを想定
).to(device)

encoding = processor(
    image,
    words=words,
    boxes=boxes,
    return_tensors="pt",
    padding="max_length",
    truncation=True
)

# 5) 推論
outputs = model(**encoding)
pred_ids = outputs.logits.argmax(-1).squeeze().tolist()

# 6) ID→ラベルにマッピングして表示
id2label = model.config.id2label
for w, idx in zip(words, pred_ids):
    print(f"{w:20} → {id2label[idx]}")
