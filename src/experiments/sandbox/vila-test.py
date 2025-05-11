from pathlib import Path
import layoutparser as lp
from layoutparser.elements import Layout
from vila.pdftools.pdf_extractor import PDFExtractor
from vila.predictors import HierarchicalPDFPredictor
from layoutparser.models import EfficientDetLayoutModel
def extract_sections_as_list(tokens, token_glue:str = ""):
	"""
	# 概要
	predicted_tokens を受け取り、
	```
	[
	  {"title": "abstract",	"content": "..."},
	  {"title": "Introduction","content": "..."},
	  …
	]
	```
	の形のリストを返す。
	"""
	sections = []
	current_title = None
	content:list[str] = []

	def commit():
		nonlocal current_title, content
		if current_title is not None:
			text = token_glue.join(content).strip()
			sections.append({"title": current_title, "content": text})
		content = []

	for token in tokens:
		typ  = token.type.lower()
		text = token.text

		if typ != "abstract" and current_title == "abstract":
			commit()
			current_title = None
			continue
		
		if typ == "abstract":
			# 抽象セクション開始
			current_title = "abstract"
			content.append(text)
		elif typ == "section":
			# 新しい章開始
			commit()			 # 前のセクションをコミット
			current_title = text.strip()
			# 見出し自身は content に含めたくなければコメントアウト
			# buffer.append(text)

		else:
			# 本文トークン
			if current_title is None: continue
			if len(content) != 0 and content[-1].endswith("-"):
				content[-1] += text
			else:
				content.append(text)

	# 最後のセクションをコミット
	commit()
	return sections

def docbank_with_vila(path:str):
	pdf_extractor = PDFExtractor("pdfplumber")
	page_tokens, page_images = pdf_extractor.load_tokens_and_image(path)
	vision_model = EfficientDetLayoutModel("lp://PubLayNet")
	pdf_predictor = HierarchicalPDFPredictor.from_pretrained(
		"allenai/hvila-block-layoutlm-finetuned-docbank"
	)
	all_tokens:list[Layout] = []
	for idx, page_token in enumerate(page_tokens): # type: ignore
		blocks = vision_model.detect(page_images[idx])
		page_token.annotate(blocks=blocks)
		pdf_data = page_token.to_pagedata().to_dict()
		predicted_tokens = pdf_predictor.predict(pdf_data, page_token.page_size)
		all_tokens.extend(predicted_tokens)
		
		annotated = lp.draw_box(page_images[idx], predicted_tokens, box_width=0, box_alpha = 0.25)
		annotated.show()
	return all_tokens
	
def structurize_pdf(path:str, token_glue:str):
	tokens = docbank_with_vila(path)
	return extract_sections_as_list(tokens, token_glue)
	

if __name__ == "__main__":
	sections = structurize_pdf("./PDF/hasEDA/IPSJ-EC2024073.pdf", "")
	print(len(sections))
	print([sec["title"] for sec in sections])