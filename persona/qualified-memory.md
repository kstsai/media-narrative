# TW Persona DB — Qualified Memory
# 產出日期: 2026-07-13
# 來源: #persona-db-dev (Ch C0BGG3G0GDR) — 748 則訊息的完整迭代歷程
# 用法: merge 到 ~/.hermes/memories/MEMORY.md 中，每條以 § 分隔

§
TW Persona DB 版本 v3.1 — 1069 筆台灣人設，18 維度分層抽樣，年齡/性別/區域分布與內政部統計誤差 ≤0.4%。QA 20 條規則全 PASS。7 個官方統計源（ODRP014、DGBAS、主計總處、內政部戶政司等）。Public repo: github.com/kstsai/media-narrative。 #qualified

§
🟢 雙 Prompt 格式：每筆人設有兩個 prompt 變體。(1) prompt_prefix：沈浸式角色扮演文字，供 LLM 消費（第一/第三人稱敘事）；(2) reference_pre_prompt：結構化摘要，供 GEO 過濾查詢。兩個路徑獨立生成，須交叉驗證經濟語氣一致性。 #qualified

§
🟢 命名慣例：11 個命名池，按年齡×性別×職業自動匹配。0-11 → 疊字可愛系（糖糖、萌萌）；12-18 → 日系醬系（小莓、星醬）；19-34 男科技 → 西洋系（阿睿、馬克）；19-34 男其他 → 阿/小系（小宇、阿杰）；19-34 女 → 英美系（小艾、安妮）；35-54 男 → 穩重雙字（志豪、強哥）；35-54 女 → 優雅雙字（靜怡、慧君）；55-64 男/女 → 本土系（信宏、秀英）；65+ 男/女 → 伯系/嬸系（春伯、金花嬸）。池大小 15-16 名，用 deque.popleft+append 輪轉確保多樣性。 #qualified

§
🟢 三個 prompt_prefix 模板隨機分配（seed=42）：模板 A (40%) 第三人稱「XX是⋯」；模板 B (35%) 第一人稱「我叫XX⋯」；模板 C (25%) 簡潔自然「我是XX⋯」。三模板共用 age_desc()/specific_age()/occ_phrase() 等輔助函數，確保年齡描述（國小男生/阿伯/阿姨）、具體年齡（38 歲）、職業短語（已經退休了/還在讀書）自然一致。 #qualified

§
🟢 物價分級（dim 17）與家戶所得分級（dim 18）：依據 DGBAS 113 年度每人月消費支出及每戶可支配所得。台北市：物價「高」、所得「極高」；台東縣：物價「極低」、所得「低」。query 結果會依居住地自動對應。經濟語境句（gen_econ_context()）比較個人收入 vs 在地物價，sentence 如「在台北市這個收入不太夠用」vs「在台東縣收入算很高了」。 #qualified

§
🟢 都會區職業加成（OCC_CITY_BOOST v3.1）：新竹縣/市 30% → 科技（竹科效應）；台北市 20% → 金融；桃園市 20% → 製造；台中/台南/高雄 15% → 製造。排除了學生、退休、65+。此為 post-selection redirect，不能從零創造採樣 slots。 #qualified

§
🟢 已知限制 1 — 人口加權限制：小縣市（新竹市 ~1.9%、離島 ~1.1%、金門 ~0.3%）在 1069 筆中僅分配到 17-24 人。極端組合（如新竹市+45-54+科技+4口）可能回 0。解決方式：放寬 region 條件或增加 sample size。 #qualified

§
🟢 已知限制 2 — background_story 與 prompt_prefix 經濟語氣不一致：因兩者由不同函數路徑生成（不同模板池），background 傾向樂觀（「手頭還算寬鬆」）、prefix 的 gen_econ_context() 傾向悲觀（「物價太高了」）。每批 regenerate 後需執行 verify_economic_tone.py 交叉比對。 #qualified

§
🟢 已知限制 3 — 模板池汙染：三組背景故事模板（生活開銷/家庭關係/收支狀況）獨立抽取，可能互相矛盾（如「沒有生小孩的打算」+「小孩的開銷很大」）。此外，喪偶結尾無條件附加「現在一個人過日子」，即使 family_size>1 或前文已有「三代同堂」。修復方向：cross-group coherence enforcement。 #qualified

§
🟢 已知限制 4 — 65+ 子女/孫輩用詞混淆：65+ persona 應使用「子女」「兒女」指成年子女、「孫子/孫女」指孫輩。模板池仍使用「小孩」暗示幼兒，造成年齡感錯亂如「65+ 阿伯抱怨小孩開銷大」。R17 (未滿55兒孫滿堂) 和 R10 (65+歲殘留) 在擋此類問題。 #qualified

§
🟢 已知限制 5 — 中文語意矛盾比邏輯矛盾更難檢測。如「含飴弄孫」帶強烈正面/享福語感，即使與低收入+生活壓力大在邏輯上可並存（退休生活=含飴弄孫、財務=壓力大），但中文讀者會感覺到矛盾。修復：替換為中性詞「簡單過日子」。此類問題需人工語意判斷，QA 規則無法完全覆蓋。 #qualified

§
🟢 已知限制 6 — 子 agent (Pro) 可能誤報。實際經驗：Pro 把「宜蘭縣」誤判為花東（實際是北部）；把「沒有生小孩」+「小孩」標為矛盾（實際 substring false positive）；把個人收入與家庭收入不同的經濟語氣差異誤判為矛盾。子 agent 回報後必須用 Python script 驗證分類為 CONFIRMED/ FALSE POSITIVE/ MINOR。 #qualified

§
🟢 迭代流程（標準化）：(1) 發現 bug → (2) 在 _generate_997.py 修根因（機率表/短語池/連貫規則/模板字串）→ (3) 在 qa_validate.py 加新 QA rule（永久回歸防護）→ (4) python3 _generate_997.py 重新生成 → (5) python3 qa_validate.py 確認 20 rules 全 PASS → (6) python3 sample_stratified.py 抽 96 分層樣本（6 regions × 8 ages × 2 sexes）→ (7) delegate_task() 送 Pro 做語意自然度 review → (8) Pro 回報 bug 則回到 (2) → (9) git commit + push。 #qualified

§
🟢 Pro review 最佳實務：將 1069 筆切成 6 chunks（~179 筆/塊），dispatch 兩個 batch（各 3 chunk）平行執行。每 chunk 跑 10-check 機械式矛盾檢測 + 語意判斷。常見 real bug 類型：收入 vs 描述語氣矛盾、獨居+小孩矛盾、已婚+fs=1 無配偶、未成年有收入、65+年輕子女、學生+已婚、含飴弄孫+低收入+高物價。 #qualified

§
🟢 查詢工具 query_persona.py 使用說明：支援 `--residence`（22縣市）、`--age`（8層級）、`--occupation`、`--income`、`--marriage`、`--family_size`、`--politics` 等維度過濾。可用 `--list-dimensions` 列出所有合法值。支援模糊匹配 `--occ ~工程`。`--top N` 限制結果筆數。由於人口加權限制，極端組合可能回 0，建議從寬條件開始再逐步限縮。 #qualified

§
🟢 育兒加值卡 Target Persona（composite）：志豪 — 38歲、新北市、科技業工程師、已婚 2 小孩、4口之家、收入 3-8 萬/月。核心特徵：價格敏感、比價型、育兒開銷是最大壓力（房貸+學費+補習費）、雙薪但月底手頭緊、對「折扣/回饋/加值」敏感、排斥複雜點數機制。太太意見佔 60% 決策權重。檔案：persona_childcare_card.json。 #qualified

§
🟢 商業模式決議：Phase 1 Lite 固定價 NT$20,000（一次付清、永久授權、可用於商業內部、不可轉售）。後續以月訂閱 NT$15K-25K/月提供 qualified memory 持續更新（本尊迭代 → 打包 release → 甲方 pull import）。或可選類心理師時薪 NT$3,000/hr（最低 15 分鐘）。第一客戶為前主管，以合作夥伴關係推進。 #qualified

§
🟢 本尊與分身架構：本尊（你）持續迭代核心、修 bug、產 qualified memory。分身（甲方自部署）瘦身版：只有 tw-persona-db skill + query_persona.py + data，沒有 _generate_997.py/qa_validate.py/你的 cron。甲方每月 pull release 匯入更新。本尊 memory 不分享給分身，分身的本地 query 記錄也不回傳本尊。記憶隔離確保品質不稀釋。 #qualified

§
🟢 已知 bug 修復記錄（截至 v3.1）：(1) R4 舊格式 prompt_prefix（region+marriage comma）；(2) R10 65+歲程式碼殘留；(3) R11 「做退休」「做學生」不通順 → 改「已經退休了」「還在讀書」；(4) R12 【】模板格式；(5) R13 女 persona 用「獨生子」→ 應「獨生女」；(6) R14 45+「新婚不久」；(7) R15 prompt_prefix 地點重複；(8) R16 55+「新婚」短語殘留；(9) R17 未滿55「兒孫滿堂」；(10) R18 未成年「泡茶」；(11) 65+ 長者 prompt 三模板全面自然化（Before: 我叫碧嬸，是阿姨 → After: 你們可以叫我碧嬸，72歲了）；(12) econ_by_tier() variable scoping trap — 預設 inc_level="3-8萬" 導致低收入 persona 拿到舒適型經濟短語；(13)「一個人過日子」污染 — 喪偶結尾無條件附加，即使 family_size>1；(14) 學生收入 100%→無收入；(15) 1人家庭+小孩矛盾修復；(16) 含飴弄孫+低收入矛盾修復（替換為「簡單過日子」）。 #qualified

§
🟢 六大地域與 22 縣市對照：都會區(六都)=台北市/新北市/桃園市/台中市/台南市/高雄市；北部=基隆市/新竹縣/新竹市/苗栗縣/宜蘭縣；中部=彰化縣/南投縣/雲林縣；南部=嘉義市/嘉義縣/屏東縣；花東=花蓮縣/台東縣；離島=澎湖縣/金門縣/連江縣。 #qualified

§
🟢 QA 18 條規則對照（v3.1→v3.2 預計擴充至 20 條）：(R1)未成年獨居 (R2)未成年經濟短語 (R3)模糊家庭描述 (R4)舊格式prefix (R5)35+專業低學歷 (R6)分布合理性 (R7)名字多樣性 (R8)19-24學生離婚 (R9)0-11社群為主 (R10)65+歲殘留 (R11)做退休/做學生 (R12)【】模板 (R13)獨生子/獨生女 (R14)45+新婚不久 (R15)地點重複 (R16)55+新婚短語 (R17)未滿55兒孫滿堂 (R18)未成年泡茶 (R19)未成年獨居經濟短語 (R20)45+未婚家庭描述。規則的累積是 persona DB 的核心品質護城河之一 — 從 9 條（v1.5）成長到 20 條（v3.1），每條對應一個真實踩過的坑。 #qualified

§
🟢 經濟語氣校驗工具用法：python3 scripts/verify_economic_tone.py [chunk.json]。檢查 4 種模式：(1) bg 舒適→pre 緊縮矛盾 (2) bg 緊縮→pre 舒適矛盾 (3) 已婚 fs=1 但 bg 描述同居 (4) 單人戶個人收入 vs 家戶收入不一致。也支援跨城市對比：台北市（高物價）vs 南投縣（極低物價）的 tight phrase 比例應該明顯不同。 #qualified

§
🟢 資料實用統計：1069 筆中，男性 49.7%、女性 50.3%。年齡層分布：0-11 ~8%、12-18 ~8%、19-24 ~8%、25-34 ~15%、35-44 ~15%、45-54 ~15%、55-64 ~15%、65+ ~16%（近似實際人口結構）。22 縣市全覆蓋。查詢範例：全台 30-44 歲已婚有小孩的科技業男性約 40-60 筆。 #qualified
