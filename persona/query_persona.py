#!/usr/bin/env python3
"""
TW Persona DB Query CLI.
Search 997 personas by dimension filters with fuzzy matching.

Usage:
    python3 query_persona.py --residence 新竹市 --age 45-54 --sex 男 --occ 科技 --family 4
    python3 query_persona.py --region 北部 --age 35-44 --income ">8萬"
    python3 query_persona.py --residence 新竹市 --occ 科技 --top 5
    python3 query_persona.py --list-dimensions          # 列出所有維度值
"""
import json, sys, argparse
from collections import Counter

DB = "/home/ubuntu/lab-riscv/hermesa3/persona/tw_persona_1069.json"

DIMENSION_FIELDS = {
    "age": "age", "sex": "sex", "region": "region", "residence": "residence",
    "edu": "education", "occ": "occupation", "income": "income",
    "politics": "politics", "media": "media_diet",
    "family": "family_size", "family_income": "family_income",
    "marriage": "marriage", "hobby": "hobby",
    "price_tier": "price_tier", "hh_income_tier": "hh_income_tier",
}

DIMENSION_ALIASES = {
    "age": "年齡", "sex": "性別", "region": "區域", "residence": "居住地",
    "edu": "教育", "occ": "職業", "income": "收入",
    "politics": "政治傾向", "family": "家庭口數",
}

with open(DB) as f:
    ALL = json.load(f)

def list_dimensions():
    """Show all possible values for each dimension."""
    from collections import Counter
    for field, label in DIMENSION_ALIASES.items():
        key = DIMENSION_FIELDS[field]
        vals = sorted(set(
            str(v) if not isinstance(v, list) else "、".join(v)
            for p in ALL
            for v in [p["dimensions"].get(key, "")]
        ))
        print(f"{label} ({field}): {', '.join(v for v in vals if v)}")

def query(**kwargs):
    results = []
    for p in ALL:
        d = p["dimensions"]
        match = True
        score = 0  # higher = better match
        for key, val in kwargs.items():
            mapped = DIMENSION_FIELDS.get(key)
            if not mapped:
                continue
            actual = d.get(mapped)
            if isinstance(actual, list):
                actual_str = "、".join(actual)
            else:
                actual_str = str(actual) if actual else ""
            
            if val.startswith("~"):
                # Fuzzy match
                if val[1:].lower() not in actual_str.lower():
                    match = False
                    break
                score += 1
            elif actual_str == val:
                score += 2
            else:
                match = False
                break
        
        if match:
            results.append((score, p))
    
    results.sort(key=lambda x: -x[0])
    return results

def show_persona(p, i=0):
    d = p["dimensions"]
    hobby_text = "、".join(d["hobby"])
    prefix = p["prompt_prefix"]
    econ_ctx = ""
    segs = [s.strip() for s in prefix.split("。") if s.strip()]
    for s in reversed(segs):
        if any(kw in s for kw in ["收入","物價","省着","舒服","壓力"]):
            econ_ctx = s
            break
    
    print(f"\n{'='*55}")
    print(f"  #{i+1} {p['name']} ({p['id']})")
    print(f"{'='*55}")
    print(f"  居住地: {d['residence']}（{d['region']}）")
    print(f"  年齡: {d['age']} | 性別: {d['sex']} | 教育: {d['education']}")
    print(f"  職業: {d['occupation']} | 收入: {d['income']}")
    print(f"  家庭: {d['family_size']}人 | 家庭所得: {d['family_income']} | 婚姻: {d['marriage']}")
    print(f"  興趣: {hobby_text}")
    print(f"  政治: {d['politics']}")
    print(f"  物價分級: {d.get('price_tier','?')} | 所得分級: {d.get('hh_income_tier','?')}")
    print(f"  背景: {d['background_story'][:150]}")
    if econ_ctx:
        print(f"  脈絡: {econ_ctx}")
    print(f"  Prefix: {prefix[:200]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query TW Persona DB")
    for field, label in DIMENSION_ALIASES.items():
        parser.add_argument(f"--{field}", help=f"Filter by {label}")
    parser.add_argument("--top", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--list-dimensions", action="store_true", help="List all dimension values and exit")
    parser.add_argument("--exact", action="store_true", help="Exact match only (default: relaxed)")
    
    args = parser.parse_args()
    
    if args.list_dimensions:
        list_dimensions()
        sys.exit(0)
    
    filters = {}
    for field in DIMENSION_ALIASES:
        val = getattr(args, field, None)
        if val:
            filters[field] = val
    
    if not filters:
        print("Usage: python3 query_persona.py --residence 新竹市 --occ 科技 [--top 5]")
        print("       python3 query_persona.py --list-dimensions")
        sys.exit(1)
    
    results = query(**filters)
    
    if not results:
        print(f"❌ 無符合條件的人設。試試放寬條件（減少 filter）或使用 --list-dimensions 查看可用值。")
        print(f"   也可以試 fuzzy match: --occ ~工程")
        sys.exit(1)
    
    print(f"\n📊 符合條件: {len(results)} 筆（顯示前 {args.top} 筆）")
    for i, (score, p) in enumerate(results[:args.top]):
        show_persona(p, i)
    
    # Summary
    if len(results) <= args.top:
        print(f"\n{'='*55}")
        print(f"  共 {len(results)} 筆結果")
        print(f"{'='*55}")
