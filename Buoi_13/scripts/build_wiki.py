import os
import re
import sys
import shutil
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def sanitize_filename(name):
    """Xóa các ký tự không hợp lệ trong tên file trên Windows"""
    return re.sub(r'[\\/:*?"<>|]', '', str(name)).strip()

def build_wiki():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    wiki_dir = os.path.join(base_dir, "wiki")
    
    entities_path = os.path.join(output_dir, "entities.csv")
    relations_path = os.path.join(output_dir, "relations.csv")
    
    if not os.path.exists(entities_path) or not os.path.exists(relations_path):
        print("Lỗi: Không tìm thấy entities.csv hoặc relations.csv trong outputs/")
        return

    # Clean & recreate wiki directories
    if os.path.exists(wiki_dir):
        shutil.rmtree(wiki_dir)
        
    risks_dir = os.path.join(wiki_dir, "risks")
    controls_dir = os.path.join(wiki_dir, "controls")
    events_dir = os.path.join(wiki_dir, "events")
    
    os.makedirs(risks_dir, exist_ok=True)
    os.makedirs(controls_dir, exist_ok=True)
    os.makedirs(events_dir, exist_ok=True)
    
    entities_df = pd.read_csv(entities_path, keep_default_na=False)
    relations_df = pd.read_csv(relations_path, keep_default_na=False)
    
    # Map entity details by ID
    entity_map = {row["id"]: row.to_dict() for _, row in entities_df.iterrows()}
    
    # Helper to get full page name (ID - Tên)
    def get_page_name(eid):
        info = entity_map.get(eid, {})
        name = info.get("name") or info.get("description") or eid
        cleaned_name = sanitize_filename(name)
        return f"{eid} - {cleaned_name}"

    # Build indexing of relationships
    incoming_rels = {}
    outgoing_rels = {}
    
    for _, rel in relations_df.iterrows():
        src = rel["source_id"]
        tgt = rel["target_id"]
        
        outgoing_rels.setdefault(src, []).append(rel.to_dict())
        incoming_rels.setdefault(tgt, []).append(rel.to_dict())
        
    wikilink_count = 0
    pages_created = 0

    # 1. Build RuiRo pages
    risks = entities_df[entities_df["type"] == "RuiRo"]
    for _, r in risks.iterrows():
        rid = r["id"]
        rname = r["name"]
        page_title = get_page_name(rid)
        filename = f"{page_title}.md"
        filepath = os.path.join(risks_dir, filename)
        
        controls_mitigating = incoming_rels.get(rid, [])
        events_observed = outgoing_rels.get(rid, [])
        
        content = f"""---
id: {rid}
title: "{page_title}"
aliases:
  - "{page_title}"
  - "{rname}"
  - "{rid}"
type: RuiRo
verification_status: {r['verification_status']}
data_origin: {r['data_origin']}
---

# {page_title}

## 1. Thông Tin Chung
- **Mã Rủi Ro:** `{rid}`
- **Tên Rủi Ro:** {rname}
- **Danh Mục (Category):** {r['category']}
- **Mô Tả:** {r['description']}
- **Đơn Vị Phụ Trách (Owner Unit ID):** `{r['owner_unit_id']}`

## 2. Diễn Giải Rủi Ro (Cause -> Event -> Impact)
- **Nguyên Nhân (Cause):** {r['cause']}
- **Sự Kiện (Event):** {r['event']}
- **Tác Động (Impact):** {r['impact']}

## 3. Mức Độ Rủi Ro
- **Mức Rủi Ro Cố Hữu (Inherent Level):** `{r['inherent_level']}`
- **Mức Rủi Ro Còn Lại (Residual Level):** `{r['residual_level']}`

## 4. Kiểm Soát Giảm Thiểu (MITIGATES)
"""
        if controls_mitigating:
            for rel in controls_mitigating:
                ctrl_id = rel["source_id"]
                ctrl_page_name = get_page_name(ctrl_id)
                wikilink_count += 1
                content += f"- [[{ctrl_page_name}]]\n"
                content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Xác minh:* `{rel['verification_status']}`\n"
                content += f"  - *Bằng chứng:* \"{rel['evidence_quote']}\"\n"
        else:
            content += "*Chưa có kiểm soát giảm thiểu nào được ghi nhận cho rủi ro này.*\n"
            
        content += "\n## 5. Sự Kiện Rủi Ro Quan Sát Được (OBSERVED_AS)\n"
        if events_observed:
            for rel in events_observed:
                evt_id = rel["target_id"]
                evt_page_name = get_page_name(evt_id)
                wikilink_count += 1
                content += f"- [[{evt_page_name}]]\n"
                content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Xác minh:* `{rel['verification_status']}`\n"
                content += f"  - *Bằng chứng:* \"{rel['evidence_quote']}\"\n"
        else:
            content += "*Chưa có sự kiện rủi ro nào được phát hiện liên quan.*\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        pages_created += 1

    # 2. Build KiemSoat pages
    controls = entities_df[entities_df["type"] == "KiemSoat"]
    for _, c in controls.iterrows():
        cid = c["id"]
        cname = c["name"]
        page_title = get_page_name(cid)
        filename = f"{page_title}.md"
        filepath = os.path.join(controls_dir, filename)
        
        risks_mitigated = outgoing_rels.get(cid, [])
        
        content = f"""---
id: {cid}
title: "{page_title}"
aliases:
  - "{page_title}"
  - "{cname}"
  - "{cid}"
type: KiemSoat
verification_status: {c['verification_status']}
data_origin: {c['data_origin']}
---

# {page_title}

## 1. Thông Tin Kiểm Soát
- **Mã Kiểm Soát:** `{cid}`
- **Tên Kiểm Soát:** {cname}
- **Loại Kiểm Soát (Control Type):** {c['control_type']}
- **Tần Suất (Frequency):** {c['frequency']}
- **Hiệu Quả (Effectiveness):** `{c['effectiveness']}`
- **Vai Trò Phụ Trách (Owner Role ID):** `{c['owner_role_id']}`

## 2. Rủi Ro Được Giảm Thiểu (MITIGATES)
"""
        if risks_mitigated:
            for rel in risks_mitigated:
                risk_id = rel["target_id"]
                risk_page_name = get_page_name(risk_id)
                wikilink_count += 1
                content += f"- [[{risk_page_name}]]\n"
                content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Xác minh:* `{rel['verification_status']}`\n"
                content += f"  - *Bằng chứng:* \"{rel['evidence_quote']}\"\n"
        else:
            content += "*Kiểm soát này hiện chưa được gán cho rủi ro nào.*\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        pages_created += 1

    # 3. Build SuKienRuiRo pages
    events = entities_df[entities_df["type"] == "SuKienRuiRo"]
    for _, e in events.iterrows():
        eid = e["id"]
        ename = e["name"]
        page_title = get_page_name(eid)
        filename = f"{page_title}.md"
        filepath = os.path.join(events_dir, filename)
        
        risks_observed = incoming_rels.get(eid, [])
        
        loss_val = f"{int(float(e['loss_amount_vnd'])):,} VND" if e['loss_amount_vnd'] and str(e['loss_amount_vnd']) != '0' else "0 VND"
        
        content = f"""---
id: {eid}
title: "{page_title}"
aliases:
  - "{page_title}"
  - "{ename}"
  - "{eid}"
type: SuKienRuiRo
verification_status: {e['verification_status']}
data_origin: {e['data_origin']}
---

# {page_title}

## 1. Thông Tin Sự Kiện
- **Mã Sự Kiện:** `{eid}`
- **Tên Sự Kiện:** {ename}
- **Mô Tả Chi Tiết:** {e['description']}
- **Mức Độ Nghiêm Trọng (Severity):** `{e['severity']}`
- **Tổn Thất Tài Chính:** `{loss_val}`
- **Ngày Xảy Ra:** `{e['occurred_at']}`
- **Ngày Phát Hiện:** `{e['discovered_at']}`

## 2. Rủi Ro Tương Ứng (OBSERVED_AS)
"""
        if risks_observed:
            for rel in risks_observed:
                risk_id = rel["source_id"]
                risk_page_name = get_page_name(risk_id)
                wikilink_count += 1
                content += f"- [[{risk_page_name}]]\n"
                content += f"  - *Quan hệ:* `{rel['relationship_type']}` | *Xác minh:* `{rel['verification_status']}`\n"
                content += f"  - *Bằng chứng:* \"{rel['evidence_quote']}\"\n"
        else:
            content += "*Sự kiện này chưa được liên kết với hồ sơ rủi ro nào.*\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        pages_created += 1

    # 4. Build Home.md
    home_filepath = os.path.join(wiki_dir, "Home.md")
    home_content = f"""---
id: HOME-001
title: "Wiki Risk Graph Home"
aliases:
  - "Wiki Risk Graph Home"
  - "Home"
type: WikiHome
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# 🛡️ Wiki Risk Graph — Trực Quan Hóa Tri Thức Rủi Ro

Chào mừng bạn đến với **Wiki Risk Graph**, hệ thống tri thức rủi ro dạng đồ thị được xây dựng tự động từ dữ liệu chuẩn hóa.

---

## 📊 Thống Kê Tổng Quan Đồ Thị

- **Tổng số trang Wiki (Nodes):** `{pages_created + 1}` (Bao gồm Home.md)
  - 🔴 **Hồ sơ Rủi ro (`RuiRo`):** `{len(risks)}`
  - 🟢 **Kiểm soát (`KiemSoat`):** `{len(controls)}`
  - 🟡 **Sự kiện Rủi ro (`SuKienRuiRo`):** `{len(events)}`
- **Tổng số Liên kết Knowledge Graph (Edges):** `{len(relations_df)}`
  - 🛡️ `MITIGATES` (KiemSoat -> RuiRo): `{len(relations_df[relations_df['relationship_type']=='MITIGATES'])}`
  - ⚠️ `OBSERVED_AS` (RuiRo -> SuKienRuiRo): `{len(relations_df[relations_df['relationship_type']=='OBSERVED_AS'])}`

---

## 🔗 Danh Mục Tri Thức

### 1. 🔴 Danh Sách Hồ Sơ Rủi Ro (`RuiRo`)
"""
    for _, r in risks.iterrows():
        wikilink_count += 1
        page_name = get_page_name(r['id'])
        home_content += f"- [[{page_name}]] — (Mức rủi ro: `{r['residual_level']}`)\n"

    home_content += "\n### 2. 🟢 Danh Sách Kiểm Soát (`KiemSoat`)\n"
    for _, c in controls.iterrows():
        wikilink_count += 1
        page_name = get_page_name(c['id'])
        home_content += f"- [[{page_name}]] — (Loại: `{c['control_type']}`)\n"

    home_content += "\n### 3. 🟡 Danh Sách Sự Kiện Rủi Ro (`SuKienRuiRo`)\n"
    for _, e in events.iterrows():
        wikilink_count += 1
        page_name = get_page_name(e['id'])
        home_content += f"- [[{page_name}]] — (Mức độ: `{e['severity']}`)\n"

    home_content += """
---

## 📍 Đường Đi Chi Tiết Mẫu (Sample Knowledge Path)
`[KS-001 - Đối soát tự động giao dịch và sổ cái]` 
   └── 🛡️ *MITIGATES* ──> `[RR-001 - Giao dịch chuyển tiền bị hạch toán sai]` 
                               └── ⚠️ *OBSERVED_AS* ──> `[SK-001 - Sai lệch trạng thái giao dịch...]`
"""
    with open(home_filepath, "w", encoding="utf-8") as f:
        f.write(home_content)
    pages_created += 1

    print("=" * 60)
    print("KẾT QUẢ SINH WIKI MARKDOWN FOR OBSIDIAN")
    print("=" * 60)
    print(f"- Thư mục Wiki đã tạo tại: {wiki_dir}")
    print(f"- Tổng số trang Wiki Markdown đã tạo: {pages_created} trang")
    print(f"  + wiki/Home.md (1 trang)")
    print(f"  + wiki/risks/ ({len(risks)} trang)")
    print(f"  + wiki/controls/ ({len(controls)} trang)")
    print(f"  + wiki/events/ ({len(events)} trang)")
    print(f"- Tổng số Obsidian [[wikilink]] đã chèn: {wikilink_count} wikilinks")
    print("=" * 60)

if __name__ == "__main__":
    build_wiki()
