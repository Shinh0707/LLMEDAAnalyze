import fugashi

# タグ付け器（unidic-lite に基づく）
tagger = fugashi.Tagger()
EXCLUDE_SURFACE = {"し", "する", "いる", "よう", "なる", "ある", "てる", "した", "して", "された", "られる"}

def extract_meaningful_chunks(text):
    tagger = fugashi.Tagger()
    tokens = list(tagger(text))
    
    results = []
    buffer = ""
    prev_pos1 = ""
    
    for word in tokens:
        surface = word.surface
        lemma = word.feature.lemma
        pos1 = word.feature.pos1

        # 除外したい単独語（記号・助詞・助動詞・補助動詞的な動詞）
        if pos1 in {"助詞", "助動詞", "記号"} or lemma in EXCLUDE_SURFACE or surface in EXCLUDE_SURFACE:
            buffer = ""
            prev_pos1 = ""
            continue

        # 接頭辞 → 次の語と結合
        if pos1 == "接頭辞":
            buffer = surface
            prev_pos1 = pos1
            continue

        # 接尾辞 → 前の語と結合（後ろにつける）
        if pos1 == "接尾辞" and results:
            results[-1] += surface
            buffer = ""
            prev_pos1 = ""
            continue

        # 副詞 + 動詞/名詞 など → 結合
        if prev_pos1 == "副詞" and pos1 in {"名詞", "動詞", "形容詞"}:
            results[-1] += surface
            buffer = ""
            prev_pos1 = ""
            continue

        # 接頭辞の後 → 合成して追加
        if prev_pos1 == "接頭辞":
            results.append(buffer + surface)
            buffer = ""
        # 単独の名詞・動詞・副詞など → そのまま追加
        elif pos1 in {"名詞", "動詞", "形容詞", "副詞"}:
            results.append(surface)

        prev_pos1 = pos1

    return set(results)


def extract_common_meaningful_tokens(eda_series):
    token_sets = []

    for entry in eda_series.dropna():
        keywords = entry.split(";")
        combined = " ".join(keywords)
        tokens = extract_meaningful_chunks(combined)
        if tokens:
            token_sets.append(tokens)

    if not token_sets:
        return []

    return sorted(set.intersection(*token_sets))