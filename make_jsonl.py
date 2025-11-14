import pandas as pd
import json

def excel_to_jsonl(excel_path, jsonl_path, sheet_name="ssg"):
    """엑셀 → JSONL 변환"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    with open(jsonl_path, 'w', encoding='utf-8-sig') as f:
        for _, row in df.iterrows():
            record = row.dropna().to_dict()
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"✅ 1단계 완료: 엑셀 → JSONL 변환 ({jsonl_path})")


def restructure_jsonl(input_path, output_path):
    """JSONL 구조 재정렬"""
    with open(input_path, "r", encoding="utf-8-sig") as infile, \
         open(output_path, "w", encoding="utf-8-sig") as outfile:
        
        for line in infile:
            data = json.loads(line.strip())
            
            product = {
                "product_id": data.get("상품 번호"),
                "product_name": data.get("상품명"),
                "waffle": {
                    "url": data.get("와플커머스_url")
                },
                "competitors": []
            }
            
            # 경쟁사(name_N, <name>_url) 자동 매핑
            for i in range(1, 10):  # 경쟁사 많을 때 대비
                name_key = f"name_{i}"
                if name_key in data:
                    name = data[name_key]
                    name = name.strip()
                    url_key = f"{name}_url"
                    url = data.get(url_key)
                    product["competitors"].append({
                        "name": name,
                        "url": url
                    })
                else:
                    break

            outfile.write(json.dumps(product, ensure_ascii=False) + '\n')

    print(f"✅ 2단계 완료: JSONL 구조화 ({output_path})")


if __name__ == "__main__":
    excel_path = "가격조사.xlsx"
    temp_jsonl = "가격조사.jsonl"
    final_jsonl = "가격조사_구조화.jsonl"

    # 1단계: 엑셀 → JSONL
    excel_to_jsonl(excel_path, temp_jsonl, sheet_name="ssg")

    # 2단계: JSONL 구조 변환
    restructure_jsonl(temp_jsonl, final_jsonl)

    print("🎉 전체 변환 완료!")
