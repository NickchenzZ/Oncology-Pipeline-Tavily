# Oncology Pipeline Analyst (Tavily Edition)

基于 Tavily Search API 的早期肿瘤管线价值评估工具，采用 6 轮分维度深度搜索。

## 功能概述

本工具通过 Tavily API 自动化收集早期肿瘤药物的公开信息，搜索结果由当前运行的模型直接生成结构化分析报告。

### 核心能力

- **6轮分维度深度搜索**：靶点机制、安全性、疗效、同机制竞品、同适应症竞品、商业策略逐轮聚焦
- **高质量搜索**：Tavily 提供带引用的搜索结果，自动过滤低质量来源
- **结构化分析框架**：基于三大支柱（靶点机制、临床数据、竞品格局）的系统化评估
- **多格式输出**：JSON、Markdown、PDF 三种格式报告
- **当前模型生成报告**：无需额外 API 调用，由运行中的模型直接分析生成

## 架构设计

### 文件结构

```
Oncology-Pipeline-Tavily/
├── tavily_research.py            # 主入口：Tavily 研究模式
├── prompts/
│   ├── analysis_framework.md     # 分析框架模板
│   └── search_prompt.md          # 搜索策略提示词
├── src/
│   ├── research/
│   │   ├── executor.py           # 研究执行器
│   │   └── prompt_loader.py      # 提示词加载
│   ├── report/
│   │   ├── base.py               # 报告基类
│   │   ├── markdown_report.py    # Markdown 报告生成
│   │   ├── pdf_report.py         # PDF 报告生成
│   │   └── factory.py            # 报告工厂
│   └── utils/
│       ├── logger.py             # 日志工具
│       └── retry.py              # 重试机制
├── requirements.txt              # 依赖包
└── .env.example                  # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包：
- `tavily-python` - Tavily Search API 客户端
- `python-dotenv` - 环境变量管理
- `fpdf2` - PDF 生成（可选）

### 2. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填写密钥：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
TAVILY_API_KEY=your_tavily_api_key
```

获取 API Key：
- Tavily: https://tavily.com/

### 3. 执行研究

```bash
python tavily_research.py "Enhertu"
```

自定义输出路径：

```bash
python tavily_research.py "ORIC-944" --output custom_report.json
```

## 搜索策略

6轮搜索分别聚焦：

1. **靶点机制与适应症基准** - 靶点特征、适应症定位、SOC基准
2. **临床数据-安全性** - 剂量探索、安全性数据、不良事件
3. **临床数据-疗效** - 疗效信号、生存数据、生物标志物
4. **同机制竞品格局** - 同靶点/同机制竞品、技术代际、直接对比
5. **同适应症同线序不同机制竞品** - 已获批/在研不同机制药物疗效安全性数据
6. **商业策略与催化剂** - 差异化价值、联合用药、催化剂时间线

## 分析框架

报告基于三大支柱的结构化框架：

### 章节一：靶点机制与适应症定位
- 靶点验证与分子受众
- 治疗线序与SOC基准

### 章节二：临床数据解读与竞品对比
- 竞品格局
- 本品早期临床数据（安全性、疗效）
- 竞品横向对比

### 章节三：商业定位与市场格局
- 差异化价值主张
- 市场规模与竞争态势

### 章节四：临床开发策略与催化剂
- 开发路径与里程碑
- 关键催化剂时间线

### 章节五：风险评估与投资要点
- 关键风险因素
- 投资建议

## 输出文件

每次研究生成三个文件：

```
research_{drug_name}_{timestamp}.json      # 原始数据
research_{drug_name}_{timestamp}.md        # Markdown 报告
research_{drug_name}_{timestamp}.pdf       # PDF 报告
```

示例：
```
research_Enhertu_1709568234.json
research_Enhertu_1709568234.md
research_Enhertu_1709568234.pdf
```

## 使用流程

工具采用两阶段流程：

1. **搜索阶段**：运行 `tavily_research.py` 执行 6 轮深度搜索，保存 JSON 原始数据
2. **报告阶段**：当前模型基于搜索数据生成分析报告，然后调用 `save_report()` 回写 MD/PDF 文件

### 搜索阶段

```bash
python tavily_research.py "Enhertu"
```

### 报告回写

模型生成报告后，使用 Write 工具将完整报告写入 MD 文件，然后调用 `save_report_from_file()` 生成带来源的 MD 和 PDF：

```python
import sys
sys.path.insert(0, ".")
from src.report.factory import save_report_from_file

files = save_report_from_file("report_draft.md", "research_Enhertu_xxxx.json")
print(files)
```

## 自定义配置

### 自定义搜索策略

编辑 `prompts/search_prompt.md` 文件来调整搜索策略，使用 `ROUND_1` 到 `ROUND_5` 章节。

### 自定义分析框架

编辑 `prompts/analysis_framework.md` 来调整报告结构和重点。

## 数据质量声明

本工具生成的报告基于公开信息自动收集和分析，具有以下特点：

**优势**：
- Tavily 提供高质量的搜索结果，自动过滤低质量来源
- 快速覆盖多个公开来源
- 结构化呈现关键信息
- 标注数据来源和时间戳

**局限**：
- 依赖公开信息的完整性和准确性
- 可能遗漏最新或非公开数据
- 需要人工验证关键数据点

**使用建议**：
1. 将报告作为初步研究的起点，而非最终结论
2. 交叉验证关键疗效数据（ORR、PFS等）
3. 通过官方渠道确认临床试验进展
4. 结合专业判断评估差异化优势

## 技术细节

### API 限制

- Tavily: 每月 1000 次免费搜索，付费计划可扩展

### 存储位置

- 报告输出: 当前工作目录

### 依赖版本

- Python: 3.8+
- tavily-python: 最新版本
- fpdf2: 2.7.0+ (可选)

## 许可证

本工具仅供研究和学习使用。

## 更新日志

### v1.3 (2026-03-15)
- 两阶段流程：搜索保存 JSON，模型生成报告后回写 MD/PDF
- save_report() 支持报告内容回写

### v1.2 (2026-03-15)
- 移除 Anthropic API 依赖，报告由当前运行的模型直接生成
- 只需配置 Tavily API Key

### v1.1 (2026-03-15)
- 移除双模式，统一为 6 轮分维度深度搜索
- 所有搜索轮次使用 Tavily advanced 深度搜索

### v1.0 (2026-03-15)
- 初始版本
- 基于 Tavily Search API
- 集成 Claude API 生成报告
- 支持 Deep/Fast 两种研究模式
