# 搜索策略提示词

本文件定义了 6 轮分维度搜索策略。

---

## ROUND_1

**名称：** 靶点机制与适应症基准

**查询：** {drug_name} target mechanism MOA indication epidemiology SOC standard treatment guideline NCCN

**重点：** 靶点特征、适应症定位、SOC基准

**搜索目标：**
- 靶点名称、生物学机制、成药验证状态
- 真实时间治疗路径，美国指南各线序推荐方案包括疗效基准、各线序治疗起始率、中位持续时间、TNT、剩余患者比例
- 核心适应症的病理类型、治疗线序定位（1L/2L/3L+）
- 当前标准治疗方案（SOC）及历史疗效基准数据

---

## ROUND_2

**名称：** 临床数据-安全性

**查询：** {drug_name} clinical trial safety DLT MTD RP2D TRAE adverse event toxicity discontinuation dose escalation phase 1

**重点：** 剂量探索、安全性数据、不良事件

**搜索目标：**
- 剂量探索结果（DLT、MTD、RP2D）
- 安全性数据：TRAE发生率、≥G3毒性比例、停药率
- 治疗相关死亡事件（TRD）
- 特别关注的不良事件（AESI，如ILD、血细胞减少等）

---

## ROUND_3

**名称：** 临床数据-疗效

**查询：** {drug_name} efficacy ORR DCR PFS OS response survival outcome biomarker PSA ctDNA DoR subgroup analysis

**重点：** 疗效信号、生存数据、生物标志物

**搜索目标：**
- 核心疗效数据（ORR、DCR、中位DoR、中位PFS、中位OS）
- 95% CI（置信区间）、样本量（N）、中位随访时间
- 亚组分析结果（特定突变亚型或不同表达水平的疗效差异）
- 生物标志物相关性分析

---

## ROUND_4

**名称：** 同机制竞品格局

**查询：** {drug_name} competitor same target same mechanism clinical data phase trial head-to-head comparison benchmark

**重点：** 同靶点/同机制竞品、技术代际、直接对比

**搜索目标：**
- 同靶点/同机制核心竞品（≥5个）及研发阶段
- 竞品的临床试验编号、关键疗效数据（ORR、PFS、OS）、安全性数据（≥G3 TRAE、停药率）
- 技术代际评估（第一代/第二代/第三代/第四代）
- 市场定位（First-in-Class、Best-in-Class、Fast-Follower）
- 跨试验疗效和安全性数据对比（绝对值+差异区间）

---

## ROUND_5

**名称：** 同适应症同线序不同机制竞品

**查询：** {drug_name} indication same line therapy approved drugs standard of care ORR PFS OS clinical trial results comparison alternative treatment

**重点：** 同适应症同线序的不同机制已获批/在研药物疗效安全性数据

**搜索目标：**
- 同适应症同线序的不同机制已获批药物（化疗、靶向、免疫、ADC、放射配体等）
- 各药物的关键注册试验数据：ORR、中位PFS、中位OS、≥G3 TRAE、停药率
- 95% CI、样本量（N）、中位随访时间
- 不同机制药物之间的疗效安全性横向对比基准
- 本品相对于 SOC 的潜在优劣势定位

---

## ROUND_6

**名称：** 商业策略与催化剂

**查询：** {drug_name} market strategy catalyst milestone funding runway pipeline combination therapy partnership licensing FDA approval BTD accelerated approval analyst expectation

**重点：** 差异化价值、联合用药、催化剂时间线

**搜索目标：**
- 差异化价值主张（Reason to Exist）
- 联合用药探索方向（联用PD-1、化疗、抗血管生成药物等）
- 市场预期与监管路径（常规审批/加速审批/突破性疗法BTD）
- 关键催化剂时间线（未来12-24个月的数据读出、会议报告、监管里程碑）
- 融资情况与现金跑道

---

## 数据质量要求

### 来源优先级顺序
1. **同行评议期刊**（NEJM, Lancet Oncology, JCO, Annals of Oncology等）
2. **主要肿瘤学会口头报告/摘要**（ASCO, ESMO, ASH, SABCS, AACR等）
3. **监管与临床试验库**（FDA/EMA文件、CDE数据库、ClinicalTrials.gov）
4. **公司官方披露**（新闻稿、财报、投资者讲演PPT）
5. **商业与分析师报告**（需明确注明发布机构）

### 数据质量红线
- **强制溯源：** 每个关键数据点必须标注：[来源URL + 发布时间 + 试验代号/NCT号]
- **数据精度：** 疗效数据必须包含绝对数值、95% CI、样本量（N）、中位随访时间
- **状态标记：** 早期或非最终数据需标注："preliminary"、"interim analysis"或"cutoff date: YYYY-MM"
- **证据不足：** 信息未找到时明确标注："信息未披露"或"待确认"，严禁编造数据
