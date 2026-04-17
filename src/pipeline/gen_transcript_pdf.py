import os
from fpdf import FPDF

# Reconstruct the conversation from context (summarized for teaching value)
transcript = [
    ("User", "來做分析與視覺化分布，應該會是兩個分頁，此外也要能在該分頁調閱各個原始問題，點擊後也應該可以互相跳轉。先設計，不要做"),
    ("AI", "收到需求。設計包含：1.GIS地圖分頁 2.數據統計圖表 3.陳情明細列表。地圖將展示熱區，列表將支持跳轉地圖。"),
    ("User", "做吧 記得使用繁體中文"),
    ("AI", "開始開發。使用 Leaflet.js 與 ECharts，整合高雄市交通數據，實作自動編碼管線。"),
    ("User", "不要使用IP，我不想被攻擊，用 LOCLAHOST"),
    ("AI", "明白。伺服器已切換至 127.0.0.1 綁定，確保內網安全。"),
    ("User", "嚴重度就是附近多次被提及 列為民眾不開心關鍵區域"),
    ("AI", "實作「密度聚合」算法。當同路口出現超過 3 筆案件，自動標記為頂級紅色熱點（怨念值 5.0）。"),
    ("User", "點近來應該看到好多個問題，可右側只有一個。當右側浮現後我可能迷失左側的，最好有按鈕可以幫我FOCUS回去"),
    ("AI", "修正細節：1.實作抽屜內的案件選單 2.新增青色呼吸圈高亮當前點擊點，防止迷失。"),
    ("User", "數據分析頁面目前沒資料"),
    ("AI", "技術修正：由於分頁隱藏導致圖表寬度為0，已加入 resize() 監聽事件，確保切換後圖表立即呈現。"),
    ("User", "原始陳述分頁，然後要顯示完整內容，有的太多就是讓他可以收攏或展開"),
    ("AI", "新增「原始陳情」獨立分頁。實作文字摺疊器，透過 Click-to-Expand 處理長文案排版。"),
    ("User", "重疊有點不直覺，想個設計 或者有按鈕。最上面的過濾器用別的底色 不然都會忽略"),
    ("AI", "介面優化：1.改用底部彈出式展開鈕 2.將網頁 Header 改為石板深藍色並加上青色外框，顯著提升辨識度。"),
    ("User", "定位來源不重要，那那是內部的技術問題，不是交通局的。"),
    ("AI", "業務轉型：移除技術圖表，替換成行政區熱度排行與負責課室分析，讓報表更貼近交通局決策需求。"),
    ("User", "用NGROK幫我RUN起來，然後給我網址"),
    ("AI", "佈署完成。網址已透過 Ngrok 隧道對外發布。")
]

class PDF(FPDF):
    def header(self):
        self.set_font('msjh', 'B', 16)
        self.cell(0, 10, 'GeoDoc Insight 開發對話原稿 (AI 教學用)', ln=True, align='C')
        self.ln(10)

def generate_pdf():
    # Use Microsoft JhengHei font for Chinese support
    # Path: C:\Windows\Fonts\msjh.ttc
    font_path = r'C:\Windows\Fonts\msjh.ttc'
    
    pdf = PDF()
    pdf.add_font('msjh', '', font_path)
    pdf.add_font('msjh', 'B', font_path)
    # Note: fpdf2 requires extraction for TTC or simple support. 
    # Since we are in a limited environ, we'll use simple text output logic first.
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for speaker, text in transcript:
        # Speaker
        pdf.set_font('msjh', 'B', 12)
        color = (34, 211, 238) if speaker == "AI" else (239, 68, 68)
        pdf.set_text_color(*color)
        pdf.cell(0, 10, f'[{speaker}]:', ln=True)
        
        # Content
        pdf.set_font('msjh', '', 11)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 41, 59)
        pdf.multi_cell(0, 8, text, border=0, fill=True)
        pdf.ln(5)
    
    output_path = os.path.join('g:\\我的雲端硬碟\\AGENT\\GeoDoc_Insight', 'GeoDoc_Insight_對話原稿_教學用.pdf')
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    generate_pdf()
