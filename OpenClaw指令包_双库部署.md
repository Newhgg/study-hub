# OpenClaw 指令包：双库（政策库+影音库）整理与云端部署

> 用法：全文复制转发给 OpenClaw，严格按步骤执行。
> 执行环境：Windows
> 目标目录：`C:\Users\黄锦浩\OneDrive\Desktop\双库`
> 最终交付：两个可微信扫码打开的稳定公网链接 + 二维码图片 + 整理好的本地文件
> 预计耗时：2-3 小时（含部署和测试）

---

## 一、任务目标

将政策库和影音库整理为**给同学用的公开稳定版本**，部署到云端，生成微信可扫码打开的二维码，确保长期稳定可用。

| 库 | 内容 | 公开形式 |
|----|------|----------|
| 政策库 | 阳光学院政策 + 考研/考公/竞赛/证书官方链接 + 本地政策文件 | 纯静态HTML，搜索+分类+时间线 |
| 影音库 | 课程学习资源导航（AI智能体/公考/个人成长），含课程简介、学习建议、核心知识点 | 纯静态HTML，课程卡片导航 |

> 重要：影音库**只公开课程索引和学习指南**，不公开视频文件本身（版权原因）。视频文件保留在本地 `我的资源` 目录。

---

## 二、前提条件（执行前确认）

执行前必须确认以下条件，不满足则停下来报告：

- [ ] 源目录存在且可读取：
  - `C:\Users\黄锦浩\OneDrive\Desktop\政策库-分享版\`
  - `C:\Users\黄锦浩\OneDrive\Desktop\我的资源\我的资源\`
- [ ] 目标目录存在：`C:\Users\黄锦浩\OneDrive\Desktop\双库\`（含子目录）
- [ ] Python 3.10+ 已安装（`python --version`）
- [ ] pip 可安装包
- [ ] 网络可访问公网（`curl -I https://www.baidu.com` 返回200）
- [ ] 检查是否有腾讯云CloudBase CLI：运行 `tcb --version` 或 `cloudbase --version`
- [ ] 检查是否有 git：`git --version`

> 如果 CloudBase CLI 和 git 都没有，停下来报告，由上层决定安装哪个部署工具。

---

## 三、目录结构（最终形态）

```
双库/
├── README.md                          # 总说明（双库是什么、怎么用、链接和二维码）
├── OpenClaw指令包_双库部署.md          # 本文件
├── 政策库/
│   ├── index.html                     # 政策库主页（优化稳定版）
│   ├── auto-policies.js               # 自动抓取政策数据
│   ├── 政策解读汇编.pdf                # 政策解读PDF
│   └── 政策文件/                       # 本地政策文件（11个）
├── 影音库/
│   ├── index.html                     # 影音库主页（课程导航）
│   └── courses/                        # 各课程详细页（HTML或MD）
├── 部署/
│   ├── 部署说明.md                     # 部署过程记录、域名、回滚方法
│   └── cloudbaserc.json               # CloudBase配置（如果用CloudBase）
└── 二维码/
    ├── 政策库二维码.png
    ├── 影音库二维码.png
    └── 双库总入口二维码.png（如果做了统一入口）
```

---

## 四、执行步骤

### 阶段 1：内容整理与复制（30分钟）

#### 步骤 1.1：复制政策库内容

```powershell
$src = "C:\Users\黄锦浩\OneDrive\Desktop\政策库-分享版"
$dst = "C:\Users\黄锦浩\OneDrive\Desktop\双库\政策库"

# 复制核心文件
Copy-Item "$src\政策资料库.html" "$dst\index.html" -Force
Copy-Item "$src\auto-policies.js" "$dst\auto-policies.js" -Force
Copy-Item "$src\政策解读汇编.pdf" "$dst\政策解读汇编.pdf" -Force

# 复制政策文件
Copy-Item "$src\政策文件\*" "$dst\政策文件\" -Recurse -Force

Write-Output "政策库内容复制完成"
Get-ChildItem $dst -Recurse -File | Select-Object FullName, Length
```

#### 步骤 1.2：扫描影音库课程，生成结构化数据

```powershell
# 扫描所有课程目录，生成课程清单JSON
$videoRoot = "C:\Users\黄锦浩\OneDrive\Desktop\我的资源\我的资源"
$courses = @()

# AI系列专栏
Get-ChildItem "$videoRoot\17【AI系列专栏】" -Directory | ForEach-Object {
    $videos = Get-ChildItem $_.FullName -Filter "*.mp4" -ErrorAction SilentlyContinue | Where-Object { !$_.Name.EndsWith(".downloading") }
    $totalSize = ($videos | Measure-Object Length -Sum).Sum
    $courses += [PSCustomObject]@{
        id = "ai_" + ($_.Name.Substring(0, [Math]::Min(4, $_.Name.Length)))
        name = $_.Name
        category = "AI智能体"
        episodeCount = $videos.Count
        totalSizeGB = if($totalSize){ [math]::Round($totalSize/1GB, 2) } else { 0 }
        description = ""
        tags = @("AI","智能体","Coze","工作流")
        status = "available"
    }
}

# 公考课程
if(Test-Path "$videoRoot\【王大锤】26蓝图公考青云宏志班"){
    $videos = Get-ChildItem "$videoRoot\【王大锤】26蓝图公考青云宏志班" -Filter "*.mp4" -ErrorAction SilentlyContinue
    $courses += [PSCustomObject]@{
        id = "gongkao_wangdachui"
        name = "王大锤26蓝图公考青云宏志班"
        category = "公考"
        episodeCount = $videos.Count
        totalSizeGB = if($videos){ [math]::Round(($videos|Measure-Object Length -Sum).Sum/1GB,2) } else {0}
        description = "公考系统课程，覆盖行测、申论、面试"
        tags = @("公考","行测","申论","选调生")
        status = "available"
    }
}

# 国考真题
if(Test-Path "$videoRoot\34省+国考【.真题.】"){
    $pdfs = Get-ChildItem "$videoRoot\34省+国考【.真题.】" -Filter "*.pdf" -Recurse -ErrorAction SilentlyContinue
    $courses += [PSCustomObject]@{
        id = "gongkao_zhenti"
        name = "34省+国考真题合集"
        category = "公考"
        episodeCount = $pdfs.Count
        totalSizeGB = 0
        description = "全国各省公考真题PDF，含答案解析"
        tags = @("公考","真题","行测","申论")
        status = "available"
    }
}

# 个人成长
if(Test-Path "$videoRoot\K188大齐-超级个体认知成长学习圈"){
    $videos = Get-ChildItem "$videoRoot\K188大齐-超级个体认知成长学习圈" -Filter "*.mp4" -ErrorAction SilentlyContinue
    $courses += [PSCustomObject]@{
        id = "growth_daqi"
        name = "大齐超级个体认知成长学习圈"
        category = "个人成长"
        episodeCount = $videos.Count
        totalSizeGB = if($videos){ [math]::Round(($videos|Measure-Object Length -Sum).Sum/1GB,2) } else {0}
        description = "涵盖形象穿搭、法律防御、营养食疗、自媒体创业、亲密关系、财务管理、减脂、情感读心等全方位个人成长课程"
        tags = @("个人成长","形象","法律","营养","自媒体","财务","减脂")
        status = "available"
    }
}

# 保存课程数据
$courses | ConvertTo-Json -Depth 5 | Out-File "C:\Users\黄锦浩\OneDrive\Desktop\双库\影音库\courses_data.json" -Encoding utf8
Write-Output "扫描到 $($courses.Count) 套课程"
$courses | Select-Object name, category, episodeCount, totalSizeGB | Format-Table -AutoSize
```

---

### 阶段 2：政策库优化（30分钟）

**目标文件**：`C:\Users\黄锦浩\OneDrive\Desktop\双库\政策库\index.html`

#### 修改 1：修正文件路径（因为从子目录移到了根目录）

原HTML中本地文件路径是 `../政策文件/...`，现在改成 `政策文件/...`。

用PowerShell批量替换：
```powershell
$file = "C:\Users\黄锦浩\OneDrive\Desktop\双库\政策库\index.html"
$content = Get-Content $file -Raw -Encoding utf8
$content = $content -replace '\.\./政策文件/', '政策文件/'
$content = $content -replace '政策解读汇编\.pdf', '政策解读汇编.pdf'
Set-Content $file -Value $content -Encoding utf8
Write-Output "路径修正完成"
```

#### 修改 2：添加导入导出功能（如果原文件没有）

检查 `index.html` 是否已有「导出数据」「导入数据」按钮。如果没有，在 toolbar 区域添加：

```html
<button class="btn btn-ghost" onclick="exportData()">⬇ 导出</button>
<button class="btn btn-ghost" onclick="document.getElementById('importFile').click()">⬆ 导入</button>
<input type="file" id="importFile" accept=".json" style="display:none" onchange="importData(event)">
```

并在 `<script>` 区域添加导入导出函数（参考之前P1-T2的代码）。

#### 修改 3：优化页面标题和描述，适合分享

将 `<title>` 改为：
```html
<title>政策资料库 · 阳光学院计算机专业</title>
```

在 header 的描述中加上"分享给同学"的友好说明。

#### 修改 4：确保所有外部链接用 HTTPS

检查所有 `http://` 链接，能改 `https://` 的都改。以下几个已知用HTTP的政府网站保留HTTP（它们不支持HTTPS）：
- `http://www.scs.gov.cn/`（国家公务员局）
- `http://www.cpta.com.cn/`（中国人事考试网）
- `http://www.ciscn.cn/`（信息安全竞赛）

其余链接确保是HTTPS。

#### 修改 5：添加"分享给同学"提示

在页面底部 footer 区域添加：
```html
<div style="text-align:center;margin-top:20px;padding:16px;background:#f0f4ff;border-radius:10px;font-size:13px;color:#4f46e5;">
  📢 觉得有用？分享给同班同学吧！所有政策链接均来自官方渠道，可放心查阅。
</div>
```

---

### 阶段 3：影音库页面建设（45分钟）

**目标**：创建一个纯静态的影音库导航主页 `C:\Users\黄锦浩\OneDrive\Desktop\双库\影音库\index.html`。

这个页面是给同学看的课程学习资源导航，**不包含视频文件本身**，只包含：
- 课程卡片（名称、分类、集数、简介、标签）
- 学习建议和路线
- 核心知识点提炼
- 免费替代资源链接（B站/慕课等）

创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>学习资源库 · 课程导航</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#18181b;--ink2:#3f3f46;--muted:#71717a;--faint:#a1a1aa;--brand:#6366f1;--accent:#8b5cf6;--line:#e4e4e7;--green:#059669;--amber:#b45309}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;background:var(--bg);color:var(--ink);min-height:100vh;-webkit-font-smoothing:antialiased}
header{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;padding:36px 24px 28px;text-align:center}
header h1{font-size:24px;font-weight:700;margin-bottom:6px}
header p{font-size:13px;opacity:.85;max-width:600px;margin:0 auto}
.stats{display:flex;gap:16px;justify-content:center;margin-top:16px;flex-wrap:wrap}
.stat-item{background:rgba(255,255,255,.15);backdrop-filter:blur(4px);padding:6px 16px;border-radius:999px;font-size:12px;font-weight:600}
.wrap{max-width:1100px;margin:0 auto;padding:0 20px}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:22px 0 4px}
.search{flex:1;min-width:200px;position:relative}
.search input{width:100%;padding:10px 14px 10px 38px;border:1px solid var(--line);border-radius:8px;font-size:14px;outline:none;background:#fff}
.search input:focus{border-color:var(--brand);box-shadow:0 0 0 3px rgba(99,102,241,.12)}
.search::before{content:"⌕";position:absolute;left:14px;top:8px;font-size:16px;color:var(--faint)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
.tab{padding:7px 15px;border-radius:999px;background:#fff;border:1px solid var(--line);font-size:13px;cursor:pointer;transition:all .15s;color:var(--muted);font-weight:600}
.tab:hover{border-color:var(--brand);color:var(--brand)}
.tab.active{background:var(--brand);border-color:var(--brand);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin:8px 0 40px}
.card{background:#fff;border-radius:12px;padding:18px;border:1px solid var(--line);transition:all .15s;display:flex;flex-direction:column;gap:8px}
.card:hover{transform:translateY(-2px);border-color:rgba(99,102,241,.45);box-shadow:0 10px 30px rgba(24,24,27,.08)}
.card h3{font-size:15px;font-weight:600;line-height:1.45}
.card .meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.tag{font-size:11px;padding:2px 10px;border-radius:999px;background:rgba(99,102,241,.09);border:1px solid rgba(99,102,241,.2);color:var(--brand);font-weight:600}
.tag.ai{background:#ede9fe;border-color:#c4b5fd;color:#6d28d9}
.tag.gongkao{background:#fef3c7;border-color:#fde68a;color:#b45309}
.tag.growth{background:#dcfce7;border-color:#bbf7d0;color:#16a34a}
.card .desc{font-size:13px;color:var(--muted);line-height:1.55}
.card .detail{font-size:12px;color:var(--faint);margin-top:auto;padding-top:8px;border-top:1px dashed var(--line);display:flex;justify-content:space-between}
.card .tags-row{display:flex;gap:6px;flex-wrap:wrap}
.empty{grid-column:1/-1;text-align:center;color:var(--muted);padding:60px 0;font-size:14px}
.section{margin:24px 0 8px}
.section h2{font-size:16px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.tip-box{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 18px;margin:16px 0;font-size:13px;color:#92400e;line-height:1.6}
.tip-box b{color:#b45309}
footer{text-align:center;color:var(--faint);font-size:12px;padding:20px 0 40px}
@media(max-width:640px){header{padding:24px 16px}.wrap{padding:0 14px}}
</style>
</head>
<body>
<header>
  <h1>📚 学习资源库 · 课程导航</h1>
  <p>AI智能体 · 公考 · 个人成长 — 精选课程学习指南，含学习路线和核心知识点</p>
  <div class="stats">
    <span class="stat-item" id="statTotal">0 套课程</span>
    <span class="stat-item">AI智能体</span>
    <span class="stat-item">公考</span>
    <span class="stat-item">个人成长</span>
  </div>
</header>

<div class="wrap">
  <div class="tip-box">
    <b>📌 使用说明：</b>本页面为课程学习资源导航，提供课程简介、学习建议和核心知识点提炼。视频文件为个人学习资料，不在此公开传播。建议配合<b>免费公开资源</b>（B站、慕课网等）学习。
  </div>

  <div class="toolbar">
    <div class="search"><input id="q" type="text" placeholder="搜索课程，如：Coze / 公考 / 减脂…" oninput="render()"></div>
  </div>
  <div class="tabs" id="tabs"></div>
  <div class="grid" id="grid"></div>

  <div class="section">
    <h2>🎯 推荐学习路线</h2>
    <div class="grid">
      <div class="card">
        <h3>大一上 · 基础打牢</h3>
        <div class="tags-row"><span class="tag">C语言</span><span class="tag">高数</span><span class="tag">四级</span></div>
        <div class="desc">重点搞定C语言编程基础、高等数学上册、英语四级词汇。课余可以了解AI智能体工具（Coze/扣子），用AI提高学习效率。</div>
        <div class="detail"><span>优先级：⭐⭐⭐</span><span>周期：3-4个月</span></div>
      </div>
      <div class="card">
        <h3>大一下 · 竞赛入门</h3>
        <div class="tags-row"><span class="tag">蓝桥杯</span><span class="tag">数学建模</span><span class="tag">Python</span></div>
        <div class="desc">参加蓝桥杯省赛（4月）、数学建模国赛（9月）。学习Python数据分析，开始接触AI智能体实战，尝试用Coze搭建简单应用。</div>
        <div class="detail"><span>优先级：⭐⭐⭐</span><span>周期：3-4个月</span></div>
      </div>
      <div class="card">
        <h3>大二 · 能力分化</h3>
        <div class="tags-row"><span class="tag">考公/考研</span><span class="tag">AI副业</span><span class="tag">专业深化</span></div>
        <div class="desc">确定方向：考公路线开始了解行测申论，考研路线开始数学英语基础。同时可以探索AI智能体接单（PPT制作、文案生成），培养副业能力。</div>
        <div class="detail"><span>优先级：⭐⭐</span><span>周期：全年</span></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>🔗 免费公开资源推荐</h2>
    <div class="grid">
      <div class="card">
        <h3>B站 · 免费编程课程</h3>
        <div class="tags-row"><span class="tag">免费</span><span class="tag">C语言</span><span class="tag">Python</span></div>
        <div class="desc">翁恺C语言、黑马程序员Python、哈工大计算机网络/组成原理，全部免费，质量高。</div>
        <div class="detail"><span>平台：B站</span><span>费用：免费</span></div>
      </div>
      <div class="card">
        <h3>中国大学MOOC</h3>
        <div class="tags-row"><span class="tag">免费</span><span class="tag">高数</span><span class="tag">专业课</span></div>
        <div class="desc">宋浩高数、哈工大计算机专业课、名校公开课，可免费学习，部分课程付费认证。</div>
        <div class="detail"><span>平台：icourse163.org</span><span>费用：免费</span></div>
      </div>
      <div class="card">
        <h3>Coze/扣子 · AI智能体平台</h3>
        <div class="tags-row"><span class="tag">免费</span><span class="tag">AI智能体</span><span class="tag">实战</span></div>
        <div class="desc">字节跳动推出的AI智能体搭建平台，免费使用，无需编程基础即可搭建智能体，适合入门实战。</div>
        <div class="detail"><span>平台：coze.cn</span><span>费用：免费</span></div>
      </div>
    </div>
  </div>
</div>

<footer>学习资源库 · 仅供学习交流 · 视频资料不公开传播 · 最后更新 2026-08-20</footer>

<script>
// 课程数据（由OpenClaw根据扫描结果填充）
const COURSES = [
  {
    name: "白先生AI流量体-老板的随身操盘手",
    category: "AI智能体",
    catClass: "ai",
    episodes: 13,
    size: "1.7GB",
    desc: "GPT调教心流法 + 数字员工操作 + 短视频7天起号 + 爆款视频底层逻辑。适合想用AI做自媒体流量的同学。",
    tags: ["GPT","提示词","数字员工","短视频","起号"],
    points: ["结构化提示词构建","智能体工作流讲解","AI数字人应用","短视频选题技法","爆款流量密码"]
  },
  {
    name: "秋叶AI智能体",
    category: "AI智能体",
    catClass: "ai",
    episodes: 1,
    size: "课件",
    desc: "秋叶老师的AI智能体课程，侧重办公效率提升和智能体实战应用。",
    tags: ["AI智能体","办公效率"],
    points: ["AI智能体基础","办公场景应用"]
  },
  {
    name: "猴帝-AI智能体线上课",
    category: "AI智能体",
    catClass: "ai",
    episodes: 19,
    size: "13GB",
    desc: "从AI基础到Coze入门，再到工作流搭建和智能体变现。体系完整，适合从零开始学AI智能体的同学。",
    tags: ["Coze","工作流","智能体变现","AI基础"],
    points: ["人工智能基础","Coze从0到1搭建智能体","工作流基础用法","AI智能体落地认知","智能体变现路径"]
  },
  {
    name: "陈厂长AI智能体实战创业营",
    category: "AI智能体",
    catClass: "ai",
    episodes: 10,
    size: "部分下载",
    desc: "3天实战创业营，侧重AI智能体的商业落地和创业方向。部分文件未完成下载。",
    tags: ["AI智能体","创业","实战"],
    points: ["智能体商业落地","创业方向选择","实战案例分析"]
  },
  {
    name: "王大锤26蓝图公考青云宏志班",
    category: "公考",
    catClass: "gongkao",
    episodes: 0,
    size: "待整理",
    desc: "公考系统课程，覆盖行测、申论、面试全模块，适合立志考公/选调生的同学。",
    tags: ["公考","行测","申论","面试","选调生"],
    points: ["行测五大模块","申论写作技巧","面试结构化","选调生政策解读"]
  },
  {
    name: "34省+国考真题合集",
    category: "公考",
    catClass: "gongkao",
    episodes: 0,
    size: "PDF",
    desc: "全国各省公考真题及答案解析PDF，刷题必备。配合课程学习效果更佳。",
    tags: ["公考","真题","刷题"],
    points: ["国考真题","各省省考真题","答案解析"]
  },
  {
    name: "大齐超级个体认知成长学习圈",
    category: "个人成长",
    catClass: "growth",
    episodes: 36,
    size: "30GB+",
    desc: "全方位个人成长课程：形象穿搭、法律防御、营养食疗、立身处事、魅力蜕变、自媒体创业、亲密关系、财务管理、轻盈减脂、情感读心。适合想全面提升自己的同学。",
    tags: ["形象","法律","营养","自媒体","亲密关系","财务","减脂","情感"],
    points: ["形象穿搭提升","法律常识防御","营养食疗健康","自媒体创业入门","亲密关系经营","财务管理基础","科学减脂方法","情感读心技巧"]
  }
];

const CATS = ["全部","AI智能体","公考","个人成长"];

function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}

function render(){
  const q=(document.getElementById("q").value||"").trim().toLowerCase();
  const active=document.querySelector(".tab.active");
  const cat=active?active.dataset.cat:"全部";
  const items=COURSES.filter(c=>
    (cat==="全部"||c.category===cat)&&
    (!q||(c.name+" "+c.desc+" "+c.tags.join(" ")).toLowerCase().includes(q))
  );
  document.getElementById("statTotal").textContent=COURSES.length+" 套课程";
  const grid=document.getElementById("grid");
  if(!items.length){grid.innerHTML='<div class="empty">没有找到匹配的课程</div>';return}
  grid.innerHTML=items.map(c=>`
    <div class="card">
      <h3>${esc(c.name)}</h3>
      <div class="meta"><span class="tag ${c.catClass}">${c.category}</span>${c.episodes>0?`<span class="tag">${c.episodes}集</span>`:""}</div>
      <div class="desc">${esc(c.desc)}</div>
      <div class="tags-row">${c.tags.slice(0,4).map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div>
      <div class="detail"><span>📺 ${c.size}</span><span>核心知识点 ${c.points.length}个</span></div>
    </div>
  `).join("");
}

function renderTabs(){
  document.getElementById("tabs").innerHTML=CATS.map(c=>`<button class="tab${c==="全部"?" active":""}" data-cat="${c}" onclick="setTab(this)">${c}</button>`).join("");
}
function setTab(el){document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));el.classList.add("active");render()}

renderTabs();render();
</script>
</body>
</html>
```

将上述HTML写入 `C:\Users\黄锦浩\OneDrive\Desktop\双库\影音库\index.html`。

---

### 阶段 4：创建统一入口页（可选，推荐）

创建 `C:\Users\黄锦浩\OneDrive\Desktop\双库\index.html`，作为双库总入口：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>阳光学院计算机 · 学习资源双库</title>
<style>
body{font-family:"PingFang SC","Microsoft YaHei",sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;margin:0;display:flex;align-items:center;justify-content:center;padding:20px}
.container{max-width:800px;width:100%}
h1{color:#fff;text-align:center;font-size:28px;margin-bottom:8px}
.subtitle{color:rgba(255,255,255,.8);text-align:center;font-size:14px;margin-bottom:32px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:600px){.cards{grid-template-columns:1fr}}
.card{background:#fff;border-radius:16px;padding:28px 24px;text-decoration:none;color:inherit;transition:all .2s;box-shadow:0 10px 40px rgba(0,0,0,.15)}
.card:hover{transform:translateY(-4px);box-shadow:0 20px 50px rgba(0,0,0,.2)}
.card .icon{font-size:40px;margin-bottom:12px}
.card h2{font-size:20px;margin:0 0 8px;color:#18181b}
.card p{font-size:13px;color:#71717a;line-height:1.6;margin:0}
.card .arrow{margin-top:16px;color:#6366f1;font-size:14px;font-weight:600}
.footer{text-align:center;color:rgba(255,255,255,.6);font-size:12px;margin-top:32px}
</style>
</head>
<body>
<div class="container">
  <h1>📚 阳光学院计算机 · 学习资源双库</h1>
  <p class="subtitle">政策资料库 + 学习资源库 — 同学们的随身学习助手</p>
  <div class="cards">
    <a class="card" href="政策库/index.html">
      <div class="icon">📋</div>
      <h2>政策资料库</h2>
      <p>阳光学院政策 · 考研/考公/竞赛/证书官方链接 · 行动时间线 · 搜索即查</p>
      <div class="arrow">进入 →</div>
    </a>
    <a class="card" href="影音库/index.html">
      <div class="icon">🎬</div>
      <h2>学习资源库</h2>
      <p>AI智能体 · 公考 · 个人成长课程导航 · 学习路线 · 免费资源推荐</p>
      <div class="arrow">进入 →</div>
    </a>
  </div>
  <p class="footer">仅供学习交流 · 政策链接均来自官方渠道 · 最后更新 2026-08-20</p>
</div>
</body>
</html>
```

---

### 阶段 5：云端部署（45分钟）

#### 方案 A：腾讯云 CloudBase 静态托管（优先，国内访问快，微信兼容好）

用户已有 CloudBase 环境（从之前的 URL 可知）。执行：

```powershell
# 1. 检查 CloudBase CLI
tcb --version
# 如果没有，安装：
npm install -g @cloudbase/cli
# 或
npm install -g cloudbase

# 2. 登录（需要用户授权，OpenClaw执行到这一步时如果需要扫码登录，停下来让用户操作）
tcb login

# 3. 列出环境，找到已有的环境ID
tcb env:list

# 4. 在双库目录创建 cloudbaserc.json
# 把 envId 替换为实际的环境ID
```

创建 `C:\Users\黄锦浩\OneDrive\Desktop\双库\部署\cloudbaserc.json`：
```json
{
  "envId": "替换为实际环境ID",
  "functionRoot": "functions",
  "staticRoot": "./",
  "hooks": {
    "preDeploy": {},
    "postDeploy": {}
  }
}
```

```powershell
# 5. 部署静态网站（从双库根目录部署）
cd "C:\Users\黄锦浩\OneDrive\Desktop\双库"
tcb hosting:deploy ./ -e 替换为环境ID

# 6. 查看部署后的域名
tcb hosting:detail -e 替换为环境ID
```

部署成功后，会得到一个 `https://xxx.tcloudbaseapp.com/` 格式的域名。

#### 方案 B：GitHub Pages（备选，如果CloudBase不可用）

```powershell
# 1. 检查git
git --version

# 2. 在双库目录初始化git
cd "C:\Users\黄锦浩\OneDrive\Desktop\双库"
git init
git add .
git commit -m "init: 双库首次部署"

# 3. 需要用户在GitHub创建仓库，然后推送
# 这一步需要用户的GitHub账号，OpenClaw执行到这里时停下来让用户操作
git remote add origin https://github.com/用户名/仓库名.git
git branch -M main
git push -u origin main

# 4. 在GitHub仓库设置中开启Pages：Settings → Pages → Source: main branch / root
# 5. 等待部署完成，得到 https://用户名.github.io/仓库名/ 链接
```

> 注意：GitHub Pages 在国内访问可能较慢，微信内偶尔打不开。优先用 CloudBase。

#### 部署记录

无论用哪个方案，部署完成后将以下信息写入 `C:\Users\黄锦浩\OneDrive\Desktop\双库\部署\部署说明.md`：

```markdown
# 部署说明

## 部署信息
- 部署时间：2026-08-20
- 部署方式：腾讯云CloudBase / GitHub Pages
- 环境ID：xxx
- 部署目录：双库/

## 访问链接
- 双库总入口：https://xxx/
- 政策库：https://xxx/政策库/index.html
- 影音库：https://xxx/影音库/index.html

## 二维码
- 政策库二维码：二维码/政策库二维码.png
- 影音库二维码：二维码/影音库二维码.png
- 双库总入口二维码：二维码/双库总入口二维码.png

## 更新方法
### CloudBase
```bash
cd 双库目录
tcb hosting:deploy ./ -e 环境ID
```

### GitHub Pages
```bash
cd 双库目录
git add .
git commit -m "update: xxx"
git push
```

## 回滚方法
- CloudBase：`tcb hosting:rollback` 或重新部署上一版本
- GitHub Pages：`git revert <commit>` 后 push

## 注意事项
- 政策库的本地文件（政策文件/目录）已随静态网站部署，可直接在线打开
- auto-policies.js 为静态数据，更新时需要替换文件后重新部署
- 影音库不包含视频文件，仅为课程导航页面
```

---

### 阶段 6：生成二维码（15分钟）

```powershell
# 1. 安装 qrcode 库
pip install qrcode[pil]

# 2. 创建生成二维码的脚本
```

创建 `C:\Users\黄锦浩\OneDrive\Desktop\双库\部署\gen_qrcode.py`：

```python
#!/usr/bin/env python3
"""生成双库二维码"""
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import os

# 部署后的链接（部署完成后替换为实际链接）
LINKS = {
    "政策库二维码": "https://替换为实际域名/政策库/index.html",
    "影音库二维码": "https://替换为实际域名/影音库/index.html",
    "双库总入口二维码": "https://替换为实际域名/",
}

OUTPUT_DIR = r"C:\Users\黄锦浩\OneDrive\Desktop\双库\二维码"

def gen_qr(name, url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6366f1", back_color="white")
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.save(path)
    print(f"✓ 生成: {path} ({url})")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, url in LINKS.items():
        gen_qr(name, url)
    print("\n完成！二维码已保存到", OUTPUT_DIR)
```

```powershell
# 3. 部署完成后，替换脚本中的链接，然后运行
python "C:\Users\黄锦浩\OneDrive\Desktop\双库\部署\gen_qrcode.py"
```

---

### 阶段 7：稳定性测试（20分钟）

部署完成后，必须进行以下测试，全部通过才算稳定：

```powershell
# 1. 页面可访问性测试
$urls = @(
    "https://替换为域名/",
    "https://替换为域名/政策库/index.html",
    "https://替换为域名/影音库/index.html"
)
foreach($url in $urls){
    try{
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        Write-Output "✓ $url -> $($resp.StatusCode)"
    } catch {
        Write-Output "✗ $url -> 失败: $($_.Exception.Message)"
    }
}

# 2. 政策库功能测试（用浏览器或curl检查关键元素）
# - 页面标题正确
# - 搜索框存在
# - 分类标签存在
# - 时间线存在
# - 政策文件链接可打开

# 3. 影音库功能测试
# - 课程卡片显示正确
# - 分类筛选正常
# - 搜索功能正常

# 4. 微信兼容性测试（需要手动用微信扫码确认）
# - 微信扫码能打开页面
# - 页面加载不超过3秒
# - 页面布局在手机上正常
# - 链接不被微信拦截
```

**手动测试清单**（需要用户配合）：
- [ ] 微信扫码打开政策库，页面正常显示
- [ ] 微信扫码打开影音库，页面正常显示
- [ ] 政策库搜索功能正常（搜"助学贷款"有结果）
- [ ] 政策库分类筛选正常
- [ ] 政策库本地文件链接可打开（如校历PDF）
- [ ] 影音库课程卡片显示完整
- [ ] 影音库分类筛选正常
- [ ] 手机端布局正常（响应式）
- [ ] 页面加载速度可接受（<3秒）

---

### 阶段 8：写 README 总说明（10分钟）

创建 `C:\Users\黄锦浩\OneDrive\Desktop\双库\README.md`：

```markdown
# 阳光学院计算机 · 学习资源双库

> 政策资料库 + 学习资源库（影音库导航），给同学们用的稳定公开版本。
> 最后更新：2026-08-20

## 快速访问

### 扫码访问
| 库 | 二维码 |
|----|--------|
| 双库总入口 | ![](二维码/双库总入口二维码.png) |
| 政策资料库 | ![](二维码/政策库二维码.png) |
| 学习资源库 | ![](二维码/影音库二维码.png) |

### 链接访问
- 双库总入口：https://替换为域名/
- 政策资料库：https://替换为域名/政策库/index.html
- 学习资源库：https://替换为域名/影音库/index.html

## 政策库包含什么

- 阳光学院官方政策（入学、资助、助学贷款、校历、辅修等）
- 考研政策（研招网官方链接）
- 考公政策（国家公务员局、人事考试网、福建省考）
- 竞赛信息（蓝桥杯、ACM、数学建模、互联网+等10+竞赛官方链接）
- 证书考试（软考、计算机等级、四六级）
- 2026-2027学年行动时间线（逐月竞赛/考试节点）
- 支持搜索、分类筛选

## 学习资源库包含什么

- AI智能体课程导航（4套课程，含Coze入门、工作流、智能体变现）
- 公考课程导航（系统课程+真题合集）
- 个人成长课程导航（36集，涵盖形象/法律/营养/自媒体/财务/减脂等）
- 推荐学习路线（大一上/大一下/大二）
- 免费公开资源推荐（B站、慕课、Coze等）

> 注意：学习资源库仅提供课程导航和学习指南，视频文件为个人学习资料，不公开传播。

## 目录结构

```
双库/
├── index.html              # 双库总入口
├── 政策库/
│   ├── index.html          # 政策库主页
│   ├── auto-policies.js    # 自动抓取政策数据
│   ├── 政策解读汇编.pdf
│   └── 政策文件/           # 本地政策文件
├── 影音库/
│   ├── index.html          # 影音库主页（课程导航）
│   └── courses/            # 课程详细页
├── 部署/
│   ├── 部署说明.md
│   ├── cloudbaserc.json
│   └── gen_qrcode.py
└── 二维码/
    ├── 政策库二维码.png
    ├── 影音库二维码.png
    └── 双库总入口二维码.png
```

## 如何更新

### 更新政策库
1. 修改 `政策库/index.html` 或 `政策库/auto-policies.js`
2. 重新部署：`tcb hosting:deploy ./ -e 环境ID`

### 更新影音库
1. 修改 `影音库/index.html`
2. 重新部署

### 更新二维码
1. 修改 `部署/gen_qrcode.py` 中的链接
2. 运行 `python 部署/gen_qrcode.py`

## 技术说明

- 纯静态HTML/CSS/JS，无后端依赖，加载快
- 部署在腾讯云CloudBase（国内访问快，微信兼容）
- 响应式设计，手机/电脑均可正常使用
- 政策数据来自官方渠道，可放心查阅

## 维护者

黄锦浩 · 阳光学院计算机科学与技术专业 2026级
```

---

## 五、验收标准

全部满足才算完成：

- [ ] 双库目录结构完整（政策库/影音库/部署/二维码 四个子目录）
- [ ] 政策库 index.html 路径已修正（政策文件/ 而非 ../政策文件/）
- [ ] 政策库有导入导出功能
- [ ] 政策库所有外部链接可正常访问（HTTP的政府网站除外）
- [ ] 影音库 index.html 已创建，包含7套课程卡片
- [ ] 影音库有分类筛选和搜索功能
- [ ] 影音库有学习路线推荐和免费资源推荐
- [ ] 双库总入口 index.html 已创建
- [ ] 云端部署成功，得到公网可访问的HTTPS链接
- [ ] 三个二维码已生成（政策库/影音库/总入口）
- [ ] 部署说明.md 已写，包含链接、更新方法、回滚方法
- [ ] README.md 已写，包含二维码、链接、使用说明
- [ ] 页面可访问性测试通过（curl返回200）
- [ ] 微信扫码测试通过（用户手动确认）
- [ ] 手机端响应式布局正常

---

## 六、出错处理规则

| 情况 | 处理方式 |
|------|----------|
| 前提条件不满足 | 立即停止，报告哪项不满足 |
| CloudBase CLI 未安装且无法安装 | 改用 GitHub Pages 方案，报告 |
| CloudBase 登录需要扫码 | 停下来让用户扫码登录，登录后继续 |
| 部署失败（域名/权限问题） | 保存完整错误日志，报告，不自行修改环境配置 |
| 二维码生成失败（qrcode库安装失败） | 用在线二维码生成API（如 `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=URL`）下载图片 |
| 页面测试404 | 检查部署路径和文件路径，修正后重新部署 |
| 微信打不开链接 | 检查是否HTTPS、域名是否被微信拦截；CloudBase域名通常没问题；如果是GitHub Pages被拦，改用CloudBase |

> **绝对禁止**：
> - 上传视频文件到云端（版权+空间问题）
> - 修改用户的CloudBase环境配置（除了部署静态文件）
> - 删除源目录（政策库-分享版、我的资源）的任何文件
> - 安装系统级软件（如Node.js，如果没有则报告由用户决定）

---

## 七、完成后交付

任务完成后，向上层报告：

1. **部署链接**：
   - 双库总入口：https://xxx/
   - 政策库：https://xxx/政策库/index.html
   - 影音库：https://xxx/影音库/index.html

2. **二维码位置**：
   - `C:\Users\黄锦浩\OneDrive\Desktop\双库\二维码\` 下3个PNG文件

3. **文件清单**：双库目录下所有文件列表

4. **部署方式**：CloudBase / GitHub Pages，环境ID，更新命令

5. **测试结果**：可访问性测试通过情况，微信测试待用户确认

6. **未完成项**：哪些没做、原因

---

*指令包结束。OpenClaw 严格按阶段1→8顺序执行，不自由发挥。*
