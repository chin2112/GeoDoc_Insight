---
name: clawhub
description: 技能搜尋與安裝器 — 當需要找現有 SKILL 或安裝新 SKILL 時啟動，支援本地搜尋、全域庫搜尋與網路搜尋三層策略。
---

# CLAWHUB — 技能搜尋器

## 角色定位

CLAWHUB 是 Agent 的「技能獵人」。當任務需要特定能力，或指揮官說要「找 SKILL」，Agent 必須透過 CLAWHUB 的標準流程進行搜尋，而不是自行從零發明。

---

## 觸發詞（Trigger Keywords）

當指揮官說出以下任何關鍵字，Agent **必須**立刻啟動 CLAWHUB 流程：

- 「找SKILL」
- 「找技能」
- 「我需要 XXX 技能」
- 「有沒有 XXX 的技能」
- 「有沒有現成的 XXX」
- 「搜尋技能」

---

## 搜尋流程（三層策略）

### Layer 1 — 本地搜尋（優先）

```
搜尋路徑：[當前專案]/_agents/skills/
工具：find_by_name + view_file (SKILL.md)
```

1. 列出當前專案 `_agents/skills/` 下的所有技能
2. 比對技能 description 是否符合需求
3. 若找到 → 直接讀取 SKILL.md 並回報給指揮官

### Layer 2 — 全域庫搜尋

```
搜尋路徑：StartAgent/_agents/skills/
工具：find_by_name + view_file (SKILL.md)
```

1. 搜尋 StartAgent 全域技能庫
2. 若找到 → 詢問指揮官是否複製到當前專案  
3. 確認後使用 `run_command` 複製整個 skill 資料夾

### Layer 3 — 網路搜尋（最後手段）

```
工具：search_web / read_url_content
```

1. 以「[需求] AI agent skill prompt」為關鍵字搜尋
2. 找到合適的實作或提示詞後，整理成標準 SKILL.md 格式
3. 提案給指揮官審核
4. 確認後安裝到 `_agents/skills/[name]/SKILL.md`

---

## 安裝規範

新技能的 SKILL.md **必須**包含以下結構：

```markdown
---
name: [技能識別名稱，小寫加底線]
description: [一句話說明此技能做什麼]
---

# [技能名稱]

## 角色定位
[此技能的職責與邊界]

## 使用時機
[什麼情況下啟動此技能]

## 執行步驟
[具體的操作步驟]
```

---

## 回報格式

搜尋完成後，以以下格式回報：

```
🔍 CLAWHUB 搜尋結果

需求：[指揮官的需求描述]

Layer 1 本地搜尋：[找到 / 未找到]
Layer 2 全域庫搜尋：[找到 [技能名] / 未找到]
Layer 3 網路搜尋：[找到 [來源] / 未搜尋]

建議方案：[複製 [技能名] / 安裝新技能 [技能名] / 無合適技能]

是否執行？
```

---

## 安裝路徑

| 場景 | 安裝目標 |
|---|---|
| 為當前專案安裝 | `[Project]/_agents/skills/[name]/` |
| 加入全域技能庫 | `StartAgent/_agents/skills/[name]/` |
| 兩者皆需 | 先安裝全域，再複製至當前專案 |
