
import requests
import pandas as pd
import re

# ============================================================
# 1. 定義維度對應表
# ============================================================

# 1.1 地區分類（六都/北/中/南/花東/離島）
REGION_MAP = {
    # 六都
    '臺北市': '都會區 (六都)', '新北市': '都會區 (六都)', '桃園市': '都會區 (六都)',
    '臺中市': '都會區 (六都)', '臺南市': '都會區 (六都)', '高雄市': '都會區 (六都)',
    # 北部（不含六都）
    '基隆市': '北', '新竹市': '北', '新竹縣': '北', '苗栗縣': '北', '宜蘭縣': '北',
    # 中部（不含六都）
    '彰化縣': '中', '南投縣': '中', '雲林縣': '中',
    # 南部（不含六都）
    '嘉義市': '南', '嘉義縣': '南', '屏東縣': '南',
    # 花東
    '花蓮縣': '花東', '臺東縣': '花東',
    # 離島
    '澎湖縣': '離島', '金門縣': '離島', '連江縣': '離島'
}

# 1.2 年齡層分組（用於 ODRP014）
def get_age_group(age):
    if age <= 6:
        return '學齡前 (0-6)'
    elif 7 <= age <= 14:
        return '青少年 (7-14)'
    elif 15 <= age <= 24:
        return '青年 (15-24)'
    elif 25 <= age <= 44:
        return '成年 (25-44)'
    elif 45 <= age <= 54:
        return '中壯齡 (45-54)'
    elif 55 <= age <= 64:
        return '中高齡 (55-64)'
    elif 65 <= age <= 74:
        return '初老齡 (65-74)'
    else:  # 75+
        return '老齡 (75+)'

# 1.3 教育程度分組（將細項教育程度歸為三大類）
def get_edu_group(edu_col_name):
    """
    將 ODRP020 的欄位名稱對應到三大教育程度。
    回傳: '國中以下' | '高中職' | '大專以上'
    """
    # 大專以上：博士、碩士、大學、二專、五專後兩年
    if any(key in edu_col_name for key in ['doctor', 'master', 'university', 'juniorcollege']):
        return '大專以上'
    # 高中職：高中、高職
    elif any(key in edu_col_name for key in ['senior', 'seniorvocational']):
        return '高中職'
    # 國中以下：國中、初職、小學、自修、不識字
    elif any(key in edu_col_name for key in ['junior', 'juniorvocational', 'primary', 'selftaught', 'illiterate']):
        return '國中以下'
    else:
        return None


# ============================================================
# 2. 資料獲取函式
# ============================================================

def fetch_api_data(url):
    """呼叫 API 並回傳 responseData 列表"""
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get('responseData', [])

# ============================================================
# 3. 處理 ODRP014：提取年齡 × 性別 × 村里人口
# ============================================================

def process_odrp014(pop_data):
    """
    將 ODRP014 的 JSON 轉為 DataFrame，包含：
    site_id, village, 年齡, 性別, 人口數
    """
    records = []
    age_col_pattern = re.compile(r'^people_age_(\d+)_([mf])$')
    
    for item in pop_data:
        site_id = item.get('site_id', '')
        village = item.get('village', '')
        
        for col_name, value in item.items():
            match = age_col_pattern.match(col_name)
            if match:
                age = int(match.group(1))
                sex = '男' if match.group(2) == 'm' else '女'
                pop = int(value) if value else 0
                if pop > 0:
                    records.append({
                        'site_id': site_id,
                        'village': village,
                        '年齡': age,
                        '性別': sex,
                        '人口數': pop
                    })
    
    df = pd.DataFrame(records)
    df['年齡層'] = df['年齡'].apply(get_age_group)
    return df


# ============================================================
# 4. 處理 ODRP020：提取教育程度 × 村里人口
# ============================================================

def process_odrp020(edu_data):
    """
    將 ODRP020 的 JSON 轉為 DataFrame，包含：
    site_id, village, 教育程度, 人口數
    """
    records = []
    edu_col_pattern = re.compile(r'^edu_(.+)_([mf])$')
    
    for item in edu_data:
        site_id = item.get('site_id', '')
        village = item.get('village', '')
        
        for col_name, value in item.items():
            match = edu_col_pattern.match(col_name)
            if match:
                edu_level = match.group(1)  # 例如: master_graduated
                sex = '男' if match.group(2) == 'm' else '女'
                pop = int(value) if value else 0
                if pop > 0:
                    edu_group = get_edu_group(edu_level)
                    if edu_group is not None:
                        records.append({
                            'site_id': site_id,
                            'village': village,
                            '性別': sex,
                            '教育程度': edu_group,
                            '人口數': pop
                        })
    
    df = pd.DataFrame(records)
    return df


# ============================================================
# 5. 主程式：整合兩份資料
# ============================================================

def main():
    import sys
    # 5.1 獲取資料
    print("正在獲取 ODRP014 人口年齡性別資料...")
    pop_data = fetch_api_data(
        'https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP014/11405'
    )
    
    print("正在獲取 ODRP020 教育程度資料...")
    edu_data = fetch_api_data(
        'https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP020/114'
    )
    
    # 5.2 分別處理
    print(f"處理人口年齡性別資料...{len(pop_data)} 筆")
    pop_df = process_odrp014(pop_data)

    pop_df['縣市'] = pop_df['site_id'].apply(lambda x: x.split('市')[0] + '市' if '市' in x else x)
    #pop_df['縣市'] = pop_df['site_id'].apply(lambda x: x.split('區')[0] if '區' in x else x)
    pop_df['地區'] = pop_df['縣市'].map(REGION_MAP)

    pop2_df = pop_df.groupby(
        ['地區', '縣市', '年齡層', '性別'],
        as_index=False
    )['人口數'].sum()
    print(pop2_df)
    print("處理教育程度資料...")
    edu_df = process_odrp020(edu_data)
    
    sys.exit(0)
    # 5.3 合併：以 site_id + village + 性別 為鍵
    # 注意：ODRP020 只有 15歲以上，所以合併後只保留 15歲以上 的人口
    pop_15up_df = pop_df[pop_df['年齡'] >= 15].copy()
    
    merged_df = pd.merge(
        pop_15up_df,
        edu_df,
        on=['site_id', 'village', '性別'],
        how='inner'  # 只保留兩邊都有的村里（確保教育資料存在）
    )
    
    # 5.4 加入縣市與地區分類
    # 從 site_id 提取縣市名稱（site_id 格式如 '65000010001'，前兩碼為縣市代碼）
    # 但 site_id 欄位已包含中文縣市名，直接使用
    merged_df['縣市'] = merged_df['site_id'].apply(lambda x: x.split('市')[0] + '市' if '市' in x else x)
    # 更穩健：直接從 site_id 提取（假設 site_id 格式為 '縣市區名'）
    # 實際上 site_id 是 '新北市板橋區'，我們可以取出第一個行政區名稱
    merged_df['縣市'] = merged_df['site_id'].apply(lambda x: x.split('區')[0] if '區' in x else x)
    merged_df['地區'] = merged_df['縣市'].map(REGION_MAP)
    
    # 5.5 最終彙總：依 地區、縣市、年齡層、性別、教育程度 分組
    final_df = merged_df.groupby(
        ['地區', '縣市', '年齡層', '性別', '教育程度'],
        as_index=False
    )['人口數'].sum()
    
    # 5.6 儲存結果
    final_df.to_csv('population_by_region_age_sex_edu.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 完成！共 {len(final_df)} 筆彙總資料，已儲存至 CSV")
    
    # 5.7 查詢範例：台北市 45-54歲 男 大專以上 人口數與佔比
    query_df = final_df[
        (final_df['縣市'] == '臺北市') &
        (final_df['年齡層'] == '中壯齡 (45-54)') &
        (final_df['性別'] == '男') &
        (final_df['教育程度'] == '大專以上')
    ]
    if not query_df.empty:
        target_pop = query_df['人口數'].sum()
        total_pop = final_df[final_df['縣市'] == '臺北市']['人口數'].sum()
        ratio = (target_pop / total_pop * 100) if total_pop > 0 else 0
        print(f"\n📊 查詢結果：臺北市 45-54歲 男 大專以上")
        print(f"   目標人口數：{target_pop:,}")
        print(f"   台北市總人口 (15歲以上)：{total_pop:,}")
        print(f"   佔比：{ratio:.2f}%")


if __name__ == "__main__":
    main()
