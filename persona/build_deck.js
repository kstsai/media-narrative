const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaDatabase, FaCheckCircle, FaDollarSign, FaRobot, FaFileInvoiceDollar, FaArrowRight, FaCogs, FaHandshake, FaChartBar, FaClipboardList } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

async function buildDeck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Kuo-Shou Tsai";
  pres.title = "TW Persona DB — 合作提案";

  // ── Color palette ──
  const C = {
    navy: "1E293B",
    dark: "0F172A",
    slate: "334155",
    sky: "0EA5E9",
    amber: "F59E0B",
    emerald: "10B981",
    rose: "F43F5E",
    lightBg: "F8FAFC",
    cardBg: "FFFFFF",
    text: "1E293B",
    textMuted: "64748B",
    white: "FFFFFF",
  };

  const mkShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.10 });

  // Preload icons
  const icons = {};
  const iconList = [
    ["db", FaDatabase, "#0EA5E9"],
    ["check", FaCheckCircle, "#10B981"],
    ["dollar", FaDollarSign, "#F59E0B"],
    ["robot", FaRobot, "#6366F1"],
    ["invoice", FaFileInvoiceDollar, "#0EA5E9"],
    ["arrow", FaArrowRight, "#F59E0B"],
    ["cogs", FaCogs, "#64748B"],
    ["handshake", FaHandshake, "#10B981"],
    ["chart", FaChartBar, "#0EA5E9"],
    ["clip", FaClipboardList, "#64748B"],
  ];
  for (const [k, Icon, color] of iconList) {
    icons[k] = await iconToBase64Png(Icon, color, 256);
  }
  const iconsWhite = {
    db: await iconToBase64Png(FaDatabase, "#FFFFFF", 256),
    robot: await iconToBase64Png(FaRobot, "#FFFFFF", 256),
    dollar: await iconToBase64Png(FaDollarSign, "#FFFFFF", 256),
    handshake: await iconToBase64Png(FaHandshake, "#F59E0B", 256),
    clip: await iconToBase64Png(FaClipboardList, "#FFFFFF", 256),
    chart: await iconToBase64Png(FaChartBar, "#F59E0B", 256),
    check: await iconToBase64Png(FaCheckCircle, "#FFFFFF", 256),
  };

  // ════════════════════════════════════════
  // SLIDE 1: Title
  // ════════════════════════════════════════
  const s1 = pres.addSlide();
  s1.background = { color: C.navy };
  // Decorative bar top
  s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.amber } });
  // Decorative bar left
  s1.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.8, w: 0.08, h: 1.2, fill: { color: C.amber } });
  // Title
  s1.addText("TW Persona DB", {
    x: 0.9, y: 1.6, w: 8, h: 0.8,
    fontSize: 40, fontFace: "Calibri", bold: true, color: C.white, margin: 0,
  });
  s1.addText("合作提案", {
    x: 0.9, y: 2.3, w: 8, h: 0.6,
    fontSize: 28, fontFace: "Calibri", color: C.amber, margin: 0,
  });
  // Subtitle
  s1.addText("Phase 1 Lite 交付 · 類心理師計費模式 · 長期迭代合作", {
    x: 0.9, y: 3.2, w: 8, h: 0.5,
    fontSize: 14, fontFace: "Calibri", color: "94A3B8", margin: 0,
  });
  // Footer
  s1.addText("Kuo-Shou Tsai · 2026-07-12", {
    x: 0.9, y: 4.8, w: 8, h: 0.4,
    fontSize: 11, fontFace: "Calibri", color: "64748B", margin: 0,
  });
  // Bottom line
  s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.4, w: 10, h: 0.04, fill: { color: C.amber } });

  // ════════════════════════════════════════
  // SLIDE 2: Agenda
  // ════════════════════════════════════════
  const s2 = pres.addSlide();
  s2.background = { color: C.lightBg };
  s2.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s2.addText("今天要聊的三件事", {
    x: 0.8, y: 0.4, w: 8, h: 0.7,
    fontSize: 30, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  // Card 1
  s2.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.4, w: 8.4, h: 1.0, fill: { color: C.cardBg }, shadow: mkShadow() });
  s2.addImage({ data: icons.chart, x: 1.0, y: 1.55, w: 0.5, h: 0.5 });
  s2.addText("Phase 1 Lite：做了什麼", {
    x: 1.7, y: 1.5, w: 7, h: 0.4,
    fontSize: 18, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  s2.addText("1069 筆人設資料庫、查詢工具、品質驗證報告", {
    x: 1.7, y: 1.9, w: 7, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.textMuted, margin: 0,
  });
  // Card 2
  s2.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 2.6, w: 8.4, h: 1.0, fill: { color: C.cardBg }, shadow: mkShadow() });
  s2.addImage({ data: icons.dollar, x: 1.0, y: 2.75, w: 0.5, h: 0.5 });
  s2.addText("定價與計費方式", {
    x: 1.7, y: 2.7, w: 7, h: 0.4,
    fontSize: 18, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  s2.addText("Phase 1 固定價 NT$20,000 ＋ 後續類心理師時薪制 NT$3,000/hr", {
    x: 1.7, y: 3.1, w: 7, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.textMuted, margin: 0,
  });
  // Card 3
  s2.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.8, w: 8.4, h: 1.0, fill: { color: C.cardBg }, shadow: mkShadow() });
  s2.addImage({ data: icons.handshake, x: 1.0, y: 3.95, w: 0.5, h: 0.5 });
  s2.addText("下一步與啟動方式", {
    x: 1.7, y: 3.9, w: 7, h: 0.4,
    fontSize: 18, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  s2.addText("如何開始合作、服務分級、月上限選項", {
    x: 1.7, y: 4.3, w: 7, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.textMuted, margin: 0,
  });

  // ════════════════════════════════════════
  // SLIDE 3: What We Built
  // ════════════════════════════════════════
  const s3 = pres.addSlide();
  s3.background = { color: C.navy };
  s3.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s3.addText("Phase 1 Lite：做了什麼", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.white, margin: 0,
  });
  // Big stat callouts
  const statColor = (i) => [C.sky, C.amber, C.emerald, C.rose][i];
  const stats = [
    ["1,069", "台灣人設筆數"],
    ["22", "全臺縣市覆蓋"],
    ["20", "QA 驗證規則"],
    ["7", "官方統計引用"],
  ];
  stats.forEach(([num, label], i) => {
    const lx = 0.6 + i * 2.35;
    s3.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.3, w: 2.0, h: 0.04, fill: { color: statColor(i) } });
    s3.addText(num, {
      x: lx, y: 1.5, w: 2.0, h: 0.7,
      fontSize: 36, fontFace: "Calibri", bold: true, color: C.white, align: "center", margin: 0,
    });
    s3.addText(label, {
      x: lx, y: 2.15, w: 2.0, h: 0.4,
      fontSize: 12, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
    });
  });

  // 3-column feature cards
  const features = [
    { icon: iconsWhite.db, title: "資料本體", desc: "1069 筆 JSON\n18 維度結構化\n雙 Prompt 格式" },
    { icon: iconsWhite.dollar, title: "實用工具", desc: "CLI 查詢過濾\n20 條自動 QA\n分層抽樣工具" },
    { icon: iconsWhite.clip, title: "完整文件", desc: "RFC 規格書\n方法論白皮書\n產出驗證報告" },
  ];
  features.forEach((f, i) => {
    const fx = 0.6 + i * 3.2;
    s3.addShape(pres.shapes.RECTANGLE, { x: fx, y: 3.0, w: 2.8, h: 2.2, fill: { color: C.slate }, shadow: mkShadow() });
    s3.addImage({ data: f.icon, x: fx + 1.0, y: 3.2, w: 0.5, h: 0.5 });
    s3.addText(f.title, {
      x: fx, y: 3.7, w: 2.8, h: 0.4,
      fontSize: 15, fontFace: "Calibri", bold: true, color: C.white, align: "center", margin: 0,
    });
    s3.addText(f.desc, {
      x: fx + 0.2, y: 4.1, w: 2.4, h: 0.9,
      fontSize: 11, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
    });
  });

  // ════════════════════════════════════════
  // SLIDE 4: Data Quality
  // ════════════════════════════════════════
  const s4 = pres.addSlide();
  s4.background = { color: C.lightBg };
  s4.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.emerald } });
  s4.addText("資料品質保證", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });

  // QA stats table
  const qaData = [
    [{ text: "驗證項目", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } },
     { text: "結果", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } },
     { text: "對比對象", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } }],
    ["年齡分布誤差", "≤ 0.3%", "內政部戶籍統計"],
    ["區域分布誤差", "≤ 0.4%", "臺灣人口比"],
    ["性別比", "49.7:50.3", "實際 49.5:50.5"],
    ["縣市覆蓋", "22/22", "全臺各縣市"],
    ["QA 驗證", "20/20 通過", "R1-R20 自動化"],
    ["資料源引用", "7 個官方源", "ODRP014/DGBAS/主計總處/內政部"],
  ];
  s4.addTable(qaData, {
    x: 0.8, y: 1.2, w: 8.4,
    colW: [3.0, 2.7, 2.7],
    border: { pt: 0.5, color: "CBD5E1" },
    fontFace: "Calibri",
    fontSize: 12,
    color: C.text,
    rowH: [0.4, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35],
    margin: [4, 8, 4, 8],
  });

  // Footnote
  s4.addText("詳細報告：GENERATION-VERIFICATION-2026-07-12.md", {
    x: 0.8, y: 4.8, w: 8, h: 0.4,
    fontSize: 10, fontFace: "Calibri", italic: true, color: C.textMuted, margin: 0,
  });

  // ════════════════════════════════════════
  // SLIDE 5: Phase 1 Price
  // ════════════════════════════════════════
  const s5 = pres.addSlide();
  s5.background = { color: C.lightBg };
  s5.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.amber } });
  s5.addText("Phase 1 Lite 定價", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  // Price card
  s5.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.2, w: 3.8, h: 2.8, fill: { color: C.cardBg }, shadow: mkShadow() });
  s5.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.2, w: 3.8, h: 0.06, fill: { color: C.amber } });
  s5.addText("NT$20,000", {
    x: 0.8, y: 1.5, w: 3.8, h: 0.8,
    fontSize: 40, fontFace: "Calibri", bold: true, color: C.amber, align: "center", margin: 0,
  });
  s5.addText("一次付清 · 永久授權", {
    x: 0.8, y: 2.2, w: 3.8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.text, align: "center", margin: 0,
  });
  s5.addImage({ data: iconsWhite.check, x: 1.0, y: 2.7, w: 0.25, h: 0.25 });
  s5.addText("可用於商業產品內部", { x: 1.3, y: 2.65, w: 3, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textMuted, margin: 0 });
  s5.addImage({ data: iconsWhite.check, x: 1.0, y: 3.0, w: 0.25, h: 0.25 });
  s5.addText("不可轉售 / 再授權", { x: 1.3, y: 2.95, w: 3, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textMuted, margin: 0 });
  s5.addImage({ data: iconsWhite.check, x: 1.0, y: 3.3, w: 0.25, h: 0.25 });
  s5.addText("不含後續更新（另計）", { x: 1.3, y: 3.25, w: 3, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textMuted, margin: 0 });

  // Comparison box
  s5.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.2, w: 4.0, h: 2.8, fill: { color: C.cardBg }, shadow: mkShadow() });
  s5.addText("定價理由", {
    x: 5.2, y: 1.3, w: 4.0, h: 0.5,
    fontSize: 16, fontFace: "Calibri", bold: true, color: C.text, align: "center", margin: 0,
  });
  s5.addText([
    { text: "傳統外包行情：", options: { bold: true, breakLine: true } },
    { text: "NT$80K - 150K\n\n", options: { breakLine: true } },
    { text: "本資料庫品質：", options: { bold: true, breakLine: true } },
    { text: "7 個官方資料源\n人口誤差 ≤ 0.4%\n20 條 QA 全通過\n\n", options: { breakLine: true } },
    { text: "定價策略：", options: { bold: true, breakLine: true } },
    { text: "試水價，低於市場 75-85%" },
  ], {
    x: 5.5, y: 1.8, w: 3.5, h: 2.0,
    fontSize: 11, fontFace: "Calibri", color: C.text, margin: 0, valign: "top", lineSpacingMultiple: 1.1,
  });

  // ════════════════════════════════════════
  // SLIDE 6: Psychologist-style billing
  // ════════════════════════════════════════
  const s6 = pres.addSlide();
  s6.background = { color: C.navy };
  s6.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s6.addText("後續服務：類心理師計費", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.white, margin: 0,
  });
  // Analogy
  s6.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.1, w: 8.4, h: 1.6, fill: { color: C.slate }, shadow: mkShadow() });
  s6.addText("核心理念", {
    x: 1.0, y: 1.15, w: 7, h: 0.4,
    fontSize: 14, fontFace: "Calibri", bold: true, color: C.sky, margin: 0,
  });
  s6.addText([
    { text: "心理師收 NT$2,000-4,000/50min，賣的是 ", options: { breakLine: false } },
    { text: "聆聽、分析、判斷的能力", options: { bold: true, breakLine: true } },
    { text: "這裡收 NT$3,000/hr，賣的是 ", options: { breakLine: false } },
    { text: "domain knowledge × AI pairing 的迭代產出能力", options: { bold: true, breakLine: true } },
    { text: "你不是在買「工程師的時間」，而是在買「一個知道問題在哪、知道怎麼用 AI 解決的人的判斷力」", options: { breakLine: true } },
  ], {
    x: 1.0, y: 1.5, w: 7.8, h: 1.1,
    fontSize: 12, fontFace: "Calibri", color: "CBD5E1", margin: 0, valign: "top",
  });
  // Rate card
  s6.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.0, w: 4.0, h: 2.2, fill: { color: C.slate }, shadow: mkShadow() });
  s6.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.0, w: 4.0, h: 0.04, fill: { color: C.amber } });
  s6.addText("NT$3,000 / hr", {
    x: 0.8, y: 3.2, w: 4.0, h: 0.7,
    fontSize: 32, fontFace: "Calibri", bold: true, color: C.amber, align: "center", margin: 0,
  });
  s6.addText("最低計費 15 分鐘", {
    x: 0.8, y: 3.8, w: 4.0, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
  });
  s6.addText("時數由 AI session log 自動回報\n客戶可查 raw log 驗證", {
    x: 0.8, y: 4.2, w: 4.0, h: 0.7,
    fontSize: 11, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
  });
  // Service descriptions
  s6.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.0, w: 4.0, h: 2.2, fill: { color: C.slate }, shadow: mkShadow() });
  s6.addText("含哪些服務？", {
    x: 5.2, y: 3.1, w: 4.0, h: 0.4,
    fontSize: 14, fontFace: "Calibri", bold: true, color: C.sky, align: "center", margin: 0,
  });
  s6.addText([
    { text: "✅ 資料修正與更新\n", options: { breakLine: true } },
    { text: "✅ Domain 維度疊加\n", options: { breakLine: true } },
    { text: "✅ 新國家/產業版本\n", options: { breakLine: true } },
    { text: "✅ 操作教學與交接" },
  ], {
    x: 5.5, y: 3.5, w: 3.5, h: 1.5,
    fontSize: 12, fontFace: "Calibri", color: "CBD5E1", margin: 0, valign: "top",
  });

  // ════════════════════════════════════════
  // SLIDE 7: Hour tracking transparency
  // ════════════════════════════════════════
  const s7 = pres.addSlide();
  s7.background = { color: C.lightBg };
  s7.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s7.addText("時數透明機制", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  // Flow diagram boxes
  const boxes = [
    { x: 0.6, y: 1.3, w: 2.6, title: "提出需求", desc: "你說「幫我加一個\n選舉投票維度」", color: C.sky },
    { x: 3.7, y: 1.3, w: 2.6, title: "AI 工作", desc: "讀 code → 改 script\n→ 重跑 → QA", color: C.amber },
    { x: 6.8, y: 1.3, w: 2.6, title: "確認完成", desc: "你 review 覺得 OK\n→ commit", color: C.emerald },
  ];
  boxes.forEach(b => {
    s7.addShape(pres.shapes.RECTANGLE, { x: b.x, y: b.y, w: b.w, h: 1.5, fill: { color: C.cardBg }, shadow: mkShadow() });
    s7.addShape(pres.shapes.RECTANGLE, { x: b.x, y: b.y, w: b.w, h: 0.04, fill: { color: b.color } });
    s7.addText(b.title, { x: b.x, y: b.y + 0.15, w: b.w, h: 0.35, fontSize: 14, fontFace: "Calibri", bold: true, color: C.text, align: "center", margin: 0 });
    s7.addText(b.desc, { x: b.x + 0.2, y: b.y + 0.55, w: b.w - 0.4, h: 0.8, fontSize: 11, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0 });
  });
  // Arrows
  s7.addImage({ data: icons.arrow, x: 3.3, y: 1.75, w: 0.35, h: 0.35 });
  s7.addImage({ data: icons.arrow, x: 6.4, y: 1.75, w: 0.35, h: 0.35 });

  // Rules table
  const rulesData = [
    [{ text: "✓ 計時", options: { bold: true, fill: { color: C.emerald }, color: C.white, align: "center" } },
     { text: "✗ 不計", options: { bold: true, fill: { color: C.rose }, color: C.white, align: "center" } }],
    ["修改 code、分析資料的實際工作", "AI API 費用（NT$~0.4/次，客戶免負擔）"],
    ["見面討論 / 線上會議", "LINE 聊兩句確認事項"],
    ["調整參數 + re-run + QA iteration", "背景發想的時間"],
    ["操作教學與交接", "學習新工具的時間"],
  ];
  s7.addTable(rulesData, {
    x: 0.8, y: 3.2, w: 8.4,
    colW: [4.2, 4.2],
    border: { pt: 0.5, color: "CBD5E1" },
    fontFace: "Calibri", fontSize: 11, color: C.text,
    rowH: [0.35, 0.35, 0.35, 0.35, 0.35],
    margin: [3, 6, 3, 6],
  });

  // ════════════════════════════════════════
  // SLIDE 8: Real example
  // ════════════════════════════════════════
  const s8 = pres.addSlide();
  s8.background = { color: C.lightBg };
  s8.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.amber } });
  s8.addText("實際範例：一日工作紀錄", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });
  s8.addText("2026-07-11 ｜ 同一 session 內 6 個工作 cycle", {
    x: 0.8, y: 0.8, w: 8, h: 0.4,
    fontSize: 11, fontFace: "Calibri", italic: true, color: C.textMuted, margin: 0,
  });

  const cycles = [
    ["現狀盤點 + 改進策略討論", "0.3h", "NT$900"],
    ["分層抽樣 review tool", "0.5h", "NT$1,500"],
    ["65+ 長者 prompt 自然化", "0.5h", "NT$1,500"],
    ["全量 Pro review 6 chunks + 3 bugs", "0.75h", "NT$2,250"],
    ["婚姻真實統計資料整合（MOI）", "1.0h", "NT$3,000"],
    ["45+ 未婚家庭描述 bug fix", "0.5h", "NT$1,500"],
  ];
  const headerRow = [
    { text: "工作項目", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } },
    { text: "時數", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } },
    { text: "金額", options: { bold: true, fill: { color: C.navy }, color: C.white, align: "center" } },
  ];
  const tableRows = [headerRow, ...cycles.map(c => c)];
  s8.addTable(tableRows, {
    x: 0.8, y: 1.3, w: 8.4,
    colW: [5.0, 1.5, 1.9],
    border: { pt: 0.5, color: "CBD5E1" },
    fontFace: "Calibri", fontSize: 12, color: C.text,
    rowH: [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35],
    margin: [4, 8, 4, 8],
  });
  // Total row
  s8.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 4.2, w: 8.4, h: 0.5, fill: { color: C.navy } });
  s8.addText([
    { text: "合計：", options: { bold: true } },
    { text: "3.55 小時  ", options: { bold: true } },
    { text: "NT$ 10,650", options: { bold: true, color: C.amber } },
  ], {
    x: 0.8, y: 4.2, w: 8.4, h: 0.5,
    fontSize: 16, fontFace: "Calibri", color: C.white, align: "center", valign: "middle", margin: 0,
  });

  // ════════════════════════════════════════
  // SLIDE 9: Service levels
  // ════════════════════════════════════════
  const s9 = pres.addSlide();
  s9.background = { color: C.lightBg };
  s9.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s9.addText("後續服務分級", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.text, margin: 0,
  });

  const levels = [
    { label: "L1", color: C.emerald, title: "資料維護", desc: "資料錯誤修正\n人口權重更新\n命名風格擴充", est: "0.5-1.0 hr", cost: "NT$1,500-3,000" },
    { label: "L2", color: C.sky, title: "Domain 疊加", desc: "選舉投票紀錄維度\n消費習慣維度\n金融風險偏好", est: "2.0-4.0 hr", cost: "NT$6,000-12,000" },
    { label: "L3", color: C.amber, title: "全新建置", desc: "日本/越南/美國版\n特定產業別 DB\n完整資料庫系統", est: "8.0-15.0 hr", cost: "NT$24,000-45,000" },
  ];
  levels.forEach((lv, i) => {
    const lx = 0.6 + i * 3.2;
    s9.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.2, w: 2.8, h: 3.8, fill: { color: C.cardBg }, shadow: mkShadow() });
    s9.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.2, w: 2.8, h: 0.06, fill: { color: lv.color } });
    s9.addText(lv.label, {
      x: lx, y: 1.4, w: 2.8, h: 0.5,
      fontSize: 24, fontFace: "Calibri", bold: true, color: lv.color, align: "center", margin: 0,
    });
    s9.addText(lv.title, {
      x: lx, y: 1.85, w: 2.8, h: 0.4,
      fontSize: 16, fontFace: "Calibri", bold: true, color: C.text, align: "center", margin: 0,
    });
    s9.addText(lv.desc, {
      x: lx + 0.2, y: 2.4, w: 2.4, h: 1.2,
      fontSize: 11, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0,
    });
    s9.addShape(pres.shapes.RECTANGLE, { x: lx + 0.4, y: 3.6, w: 2.0, h: 0.02, fill: { color: "CBD5E1" } });
    s9.addText(`預估 ${lv.est}`, {
      x: lx, y: 3.7, w: 2.8, h: 0.3,
      fontSize: 11, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0,
    });
    s9.addText(lv.cost, {
      x: lx, y: 4.0, w: 2.8, h: 0.4,
      fontSize: 14, fontFace: "Calibri", bold: true, color: C.text, align: "center", margin: 0,
    });
  });

  // ════════════════════════════════════════
  // SLIDE 10: Next steps
  // ════════════════════════════════════════
  const s10 = pres.addSlide();
  s10.background = { color: C.navy };
  s10.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.amber } });
  s10.addText("下一步：如何開始", {
    x: 0.8, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true, color: C.white, margin: 0,
  });

  // 4-step process
  const steps = [
    { n: "1", title: "你取得 Phase 1", desc: "NT$20,000\n完整資料庫系統\n1069 筆 + 工具 + 文件" },
    { n: "2", title: "實際試用", desc: "用 query 工具查你的\n目標客群\n看品質是否符合預期" },
    { n: "3", title: "提出修改需求", desc: "按 session log 時薪計費\n每月結算一次\n透明可查驗" },
    { n: "4", title: "長期合作", desc: "可轉月訂閱制\nNT$15K-25K/月\n穩定迭代更新" },
  ];
  steps.forEach((st, i) => {
    const sx = 0.4 + i * 2.45;
    s10.addShape(pres.shapes.RECTANGLE, { x: sx, y: 1.3, w: 2.1, h: 3.5, fill: { color: C.slate }, shadow: mkShadow() });
    // Circle number
    s10.addShape(pres.shapes.OVAL, { x: sx + 0.7, y: 1.4, w: 0.5, h: 0.5, fill: { color: C.amber } });
    s10.addText(st.n, {
      x: sx + 0.7, y: 1.4, w: 0.5, h: 0.5,
      fontSize: 18, fontFace: "Calibri", bold: true, color: C.navy, align: "center", valign: "middle", margin: 0,
    });
    s10.addText(st.title, {
      x: sx, y: 2.0, w: 2.1, h: 0.4,
      fontSize: 15, fontFace: "Calibri", bold: true, color: C.white, align: "center", margin: 0,
    });
    s10.addText(st.desc, {
      x: sx + 0.15, y: 2.5, w: 1.8, h: 1.8,
      fontSize: 11, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
    });
  });

  // Optional options
  s10.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 5.0, w: 8.4, h: 0.4, fill: { color: C.dark } });
  s10.addText("可調整選項：月上限 NT$20-30K ｜ 最低月份按實際時數 ｜ 多 domain 疊加 9 折", {
    x: 0.8, y: 5.0, w: 8.4, h: 0.4,
    fontSize: 11, fontFace: "Calibri", color: "94A3B8", align: "center", valign: "middle", margin: 0,
  });

  // ════════════════════════════════════════
  // SLIDE 11: Thank you
  // ════════════════════════════════════════
  const s11 = pres.addSlide();
  s11.background = { color: C.navy };
  s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.sky } });
  s11.addText("謝謝 ｜ 期待合作", {
    x: 0.8, y: 1.5, w: 8, h: 1.0,
    fontSize: 40, fontFace: "Calibri", bold: true, color: C.white, align: "center", margin: 0,
  });
  s11.addText("所有資料與文件已上傳至 GitHub", {
    x: 0.8, y: 2.5, w: 8, h: 0.5,
    fontSize: 14, fontFace: "Calibri", color: "94A3B8", align: "center", margin: 0,
  });
  s11.addText("https://github.com/kstsai/media-narrative", {
    x: 0.8, y: 3.0, w: 8, h: 0.5,
    fontSize: 14, fontFace: "Consolas", color: C.sky, align: "center", margin: 0,
  });
  s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.4, w: 10, h: 0.04, fill: { color: C.sky } });

  // ── Write file ──
  const outPath = "/home/ubuntu/media-narrative/persona/TW-Persona-DB-Proposal.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log("✅ Deck saved to:", outPath);
}

buildDeck().catch(e => { console.error(e); process.exit(1); });
