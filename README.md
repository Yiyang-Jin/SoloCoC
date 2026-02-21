# CoC 跑团助手

克苏鲁的呼唤（CoC）第七版跑团辅助工具，由 AI 模型扮演 KP（守秘人）。支持多种 LLM，均使用 OpenAI 兼容 API。

**English: [README_EN.md](README_EN.md)**

**详细使用说明：[使用指南](USAGE_GUIDE.md)**

---

## 手把手安装指南

本指南面向有基本电脑操作能力、但不熟悉 GitHub、命令行或网络配置的用户。请按顺序完成每一步。

---

### 第 0 步：准备工作

- 一台 Windows、Mac 或 Linux 电脑
- 能正常上网
- 任意浏览器（Chrome、Edge、Firefox 等）

---

### 第 1 步：安装 Python

Python 是本程序运行所需的编程语言。

1. 打开浏览器，访问：**https://www.python.org/downloads/**
2. 点击黄色的 **"Download Python 3.x.x"** 按钮
3. 运行下载好的安装包

   **Windows 用户：**  
   - 安装界面底部务必勾选 **「Add Python to PATH」**（非常重要）  
   - 点击 **「Install Now」**  
   - 安装完成后点击 **「Close」** 关闭

4. 检查是否安装成功：
   - **Windows：** 按 `Win + R`，输入 `cmd` 回车。在黑色窗口中输入：
     ```
     python --version
     ```
   - **Mac/Linux：** 打开「终端」，输入：
     ```
     python3 --version
     ```
   - 应显示类似 `Python 3.10.0` 的版本号。若提示「未找到」或报错，请重新安装，并确保 Windows 安装时勾选了「Add to PATH」。

---

### 第 2 步：获取项目文件

需要把项目文件夹放到你的电脑上。常见方式：

- **如果下载了 ZIP 压缩包：**
  1. 找到下载的 ZIP 文件（如 `SimpleCoC.zip`）
  2. 右键 → **解压到…**（Windows）或双击打开（Mac）
  3. 选择一个位置（如桌面、文档）
  4. 解压后应看到一个名为 `SimpleCoC` 的文件夹，里面有 `main.py`、`config.py`、`requirements.txt` 等文件

- **如果是别人拷贝给你的文件夹：**  
  将整个 `SimpleCoC` 文件夹复制到你能找到的位置（如桌面）

---

### 第 3 步：在项目文件夹中打开命令行

后续命令需要在 `SimpleCoC` 文件夹内执行。

**Windows：**

1. 打开文件资源管理器，进入 `SimpleCoC` 文件夹
2. 点击顶部地址栏（显示路径的位置）
3. 输入 `cmd` 后回车。会弹出黑色命令行窗口，且已经在当前文件夹下

**Mac：**

1. 打开 Finder，进入 `SimpleCoC` 文件夹
2. 右键该文件夹（或按住 Control 再点）
3. 选择 **「在终端中打开」** 或 **「服务」→「在终端中打开」**

**通用方法：**

1. 打开「终端」（Mac/Linux）或「命令提示符」（Windows）
2. 输入 `cd` 加空格，再把 `SimpleCoC` 文件夹拖进窗口，回车
   - 示例：`cd C:\Users\你的用户名\Desktop\SimpleCoC`
   - 或：`cd /Users/你的用户名/Desktop/SimpleCoC`

---

### 第 4 步：创建虚拟环境（推荐）

虚拟环境能把本项目的依赖和其他程序隔离开，避免冲突。

1. 在命令行中（当前目录应为 `SimpleCoC`），执行：
   - **Windows：**
     ```
     python -m venv venv
     ```
   - **Mac/Linux：**
     ```
     python3 -m venv venv
     ```
2. 激活虚拟环境：
   - **Windows：**
     ```
     venv\Scripts\activate
     ```
   - **Mac/Linux：**
     ```
     source venv/bin/activate
     ```
3. 命令行前会出现 `(venv)`，说明虚拟环境已激活。

---

### 第 5 步：安装依赖

程序需要一些 Python 库，用下面命令安装：

- **Windows（虚拟环境已激活）：**
  ```
  pip install -r requirements.txt
  ```
- **Mac/Linux（虚拟环境已激活）：**
  ```
  pip3 install -r requirements.txt
  ```

等待安装完成。会输出很多文字，属于正常现象。完成后会回到命令行提示符。

如果提示「pip 未找到」等错误，可尝试：
- **Windows：** `python -m pip install -r requirements.txt`
- **Mac/Linux：** `python3 -m pip install -r requirements.txt`

---

### 第 6 步：获取 API Key（或选择本地 LLM）

**推荐：** 使用阿里百炼的 **qwen3.5-plus** 模型可获得最佳跑团体验（默认配置）。若选择其他 LLM，效果可能有所差异。

本程序支持多种 AI 服务。大部分需 API Key，Ollama、LM Studio 等本地部署无需 Key。

1. 打开设置页，选择「LLM 提供商」
2. 若选 **阿里百炼**（默认）：在浏览器访问
   - **国际版：** https://modelstudio.console.alibabacloud.com/（新加坡）
   - **国内版：** https://bailian.console.aliyun.com/
3. 进入 API Key 或模型工作台相关页面，创建 Key（通常以 `sk-` 开头）
4. 复制该 Key 并妥善保存。**不要泄露给他人。**
5. 若使用 **Ollama** 或 **LM Studio**：先在本机安装并启动对应服务，选择该提供商后无需填写 Key。

---

### 第 7 步：启动程序

1. 确认当前命令行：
   - 已在 `SimpleCoC` 文件夹内
   - 如使用了第 4 步，则已激活虚拟环境（行首有 `(venv)`）

2. 执行：
   - **Windows：**
     ```
     python main.py
     ```
   - **Mac/Linux：**
     ```
     python3 main.py
     ```

3. 正常情况下会看到类似输出：
   ```
   INFO:     Uvicorn running on http://0.0.0.0:29147
   ```
4. **不要关闭此窗口**，关闭会停止程序。

---

### 第 8 步：在浏览器中打开

1. 打开任意浏览器
2. 在地址栏输入：
   ```
   http://localhost:29147
   ```
3. 回车
4. 应能看到 CoC 跑团助手的界面

---

### 第 9 步：在网页中配置 API Key

1. 在界面中点击右上角齿轮图标或「设置」按钮
2. 在 **API Key** 输入框中粘贴第 6 步复制的 Key
3. 选择界面语言（如中文）
4. 点击 **保存**
5. 关闭设置窗口后即可开始使用

---

### 第 10 步：基本使用

1. **剧本：** 上传 PDF 格式的剧本（如已有的 CoC 模组）
2. **人物卡：** 新建或导入人物卡（支持 PDF、JSON、TXT 等）
3. **对话：** 选择人物卡或「玩家询问 KP」模式，输入行动或提问
4. **投骰：** KP 回复中会按 `[ROLL:技能|值]`、`[DICE:1d6]` 等标记自动投骰

> 更详细的界面说明、操作流程与投骰语法请参阅 **[使用指南](USAGE_GUIDE.md)**。

---

## 支持的 LLM 提供商

在设置中可选择以下提供商，均通过 OpenAI 兼容接口调用：

| 提供商 | 获取 Key | 默认模型 |
|--------|----------|----------|
| 阿里百炼 | [国内](https://bailian.console.aliyun.com/) [国际](https://modelstudio.console.alibabacloud.com/) | qwen3.5-plus |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | deepseek-chat |
| 月之暗面 Kimi | [platform.moonshot.ai](https://platform.moonshot.ai/) | moonshot-v1-8k |
| 智谱 GLM | [open.bigmodel.cn](https://open.bigmodel.cn/) | glm-4-plus |
| Groq | [console.groq.com](https://console.groq.com/) | llama-3.1-70b-versatile |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | gpt-4o-mini |
| OpenRouter | [openrouter.ai](https://openrouter.ai/) | 多模型聚合 |
| Together.ai | [api.together.xyz](https://api.together.xyz/) | 开源推理 |
| Ollama（本地） | 无需 Key | qwen2.5 |
| LM Studio（本地） | 无需 Key | 自选 |
| 自定义 | 自填 base_url | 自填 model |

---

## 功能概览

- **多 LLM 接入：** 支持阿里百炼、DeepSeek、Kimi、智谱、Groq、OpenAI、OpenRouter、Ollama 等
- **中英双语：** 界面支持中文/English 切换，偏好保存在 localStorage
- **Web 配置 API Key：** 在设置页配置，保存于 `data/api_config.json`
- **人物卡管理：** 新建、编辑、导入（PDF/JSON/TXT/MD/HTML/DOCX）、AI 生成
- **剧本 RAG：** 上传 PDF 剧本，基于 BM25 检索相关内容供 KP 参考
- **KP 对话：** 与 AI KP 对话，支持指定人物卡行动或玩家询问
- **投骰系统：** D100、3D6、技能检定；KP 回复中 `[ROLL:技能|值]`、`[DICE:表达式]` 自动执行
- **行动日志：** 记录对话、投骰、检定，可导出

---

## 常见问题

**「Python 不是内部或外部命令」或「command not found」**

- 重新安装 Python，Windows 安装时务必勾选「Add Python to PATH」
- 安装后重启命令行或电脑

**「pip 不是内部或外部命令」**

- 使用：`python -m pip install -r requirements.txt`（Mac/Linux 用 `python3 -m pip`）

**「端口 29147 已被占用」**

- 可能有其他程序占用该端口。关闭其他正在运行的本程序，或在 `main.py` 底部修改端口号（如改为 29148）

**「API 错误」或「请设置 API Key」**

- 在网页设置中粘贴有效的百炼 API Key。确认以 `sk-` 开头且无多余空格

**「无法访问此网站」或「连接被拒绝」**

- 确保程序在运行（第 7 步）且命令行窗口未关闭
- 地址使用 `http://localhost:29147`（用 http，不要用 https）

---

## 目录结构

```
SimpleCoC/
├── main.py           # 程序入口
├── config.py         # 配置
├── api_config.py     # API Key 存储（来自 Web 设置）
├── coc_*.py          # CoC 相关模块
├── settings_store.py # 生成参数
├── defaults/         # 默认 KP 提示词
├── static/           # 前端
└── data/             # 本地数据（人物卡、剧本、会话等，不入 git）
```

---

## 停止程序

- 在运行程序的命令行窗口中按 `Ctrl + C`
- 或直接关闭该命令行窗口
