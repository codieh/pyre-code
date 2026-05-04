#!/usr/bin/env python3
"""Generate annotated reference and interview notebooks for batch 1 (14 tasks)."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT / "solutions"
TASKS_DIR = ROOT / "torch_judge" / "tasks"


def load_task(task_id):
    ns = {}
    exec((TASKS_DIR / f"{task_id}.py").read_text(), ns)
    return ns["TASK"]


def find_nb_number(task_id):
    for p in sorted(SOLUTIONS_DIR.glob("*_solution.ipynb")):
        tid = re.sub(r"^\d+_", "", p.stem).replace("_solution", "")
        if tid == task_id:
            return p.name.split("_")[0]
    return "99"


def find_existing_nb(task_id, interview=False):
    suffix = "_interview" if interview else "_solution"
    for p in sorted(SOLUTIONS_DIR.glob(f"*{suffix}.ipynb")):
        tid = re.sub(r"^\d+_", "", p.stem).replace(suffix, "")
        if tid == task_id:
            return p
    return None


def extract_cells(nb_path):
    """Extract demo and judge cells from existing notebook."""
    nb = json.loads(nb_path.read_text())
    demo_cells = []
    judge_cells = []
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        # Skip colab install and import cells
        if "google.colab" in src:
            continue
        if src.strip().startswith("import ") or src.strip().startswith("from "):
            continue
        if "# ✅" in src:
            continue
        if "check(" in src or "judge" in src.lower():
            judge_cells.append(src)
        elif "Verify" in src or "print(" in src or "demo" in src.lower():
            demo_cells.append(src)
        elif len(src.strip()) > 0:
            demo_cells.append(src)
    return "\n\n".join(demo_cells), "\n\n".join(judge_cells)


def build_header(task, variant):
    tag = "面试版" if variant == "interview" else "参考版"
    title = task.get("title", "")
    difficulty = task.get("difficulty", "")
    desc_zh = task.get("description_zh", "")
    hint_zh = task.get("hint_zh", "")
    func_name = task.get("function_name", "")

    lines = [f"# 🔴 Solution: {title}（{tag}）", "", "## 📋 题目描述", ""]
    if difficulty:
        lines += [f"**难度：** {difficulty}", ""]
    if desc_zh:
        lines += [desc_zh, ""]
    if hint_zh:
        lines += [f"**提示：** {hint_zh}", ""]
    return "\n".join(lines)


def make_notebook(header_md, solution_code, demo_code, judge_code, summary_md):
    def code_cell(src):
        lines = src.split("\n")
        for i in range(len(lines) - 1):
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
        return {
            "cell_type": "code",
            "execution_count": None,
            "id": None,
            "metadata": {},
            "outputs": [],
            "source": lines,
        }

    def md_cell(src):
        lines = src.split("\n")
        for i in range(len(lines) - 1):
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
        return {
            "cell_type": "markdown",
            "id": None,
            "metadata": {},
            "source": lines,
        }

    cells = [
        md_cell(header_md),
        code_cell("import torch\nimport math"),
        code_cell(solution_code),
    ]
    if demo_code.strip():
        cells.append(code_cell(demo_code))
    if judge_code.strip():
        cells.append(code_cell(judge_code))
    if summary_md.strip():
        cells.append(md_cell(summary_md))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_nb(task_id, variant, solution_code, summary_md, demo_code="", judge_code=""):
    task = load_task(task_id)
    header = build_header(task, variant)
    nb = make_notebook(header, solution_code, demo_code, judge_code, summary_md)
    num = find_nb_number(task_id)
    suffix = "_interview" if variant == "interview" else "_solution"
    out_path = SOLUTIONS_DIR / f"{num}_{task_id}{suffix}.ipynb"
    out_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
    print(f"  Written: {out_path.name}")


# ============================================================
# TASK-SPECIFIC ANNOTATED CODE
# ============================================================

ANNOTATIONS = {}

# ---- 1. relu ----
ANNOTATIONS["relu"] = {}
ANNOTATIONS["relu"]["reference"] = """# ✅ SOLUTION

def relu(x: torch.Tensor) -> torch.Tensor:
    # ---- Step 1: 构造布尔掩码 ----
    # (x > 0) 逐元素比较，返回布尔张量，shape 与 x 相同
    # 例如 x = [-2, -1, 0, 1, 2] → mask = [False, False, False, True, True]
    mask = (x > 0)

    # ---- Step 2: 掩码转为浮点并逐元素相乘 ----
    # .float() 将布尔转为 0.0 / 1.0（PyTorch 不支持 bool * float 直接运算）
    # x * mask_float：正数位置 ×1 = 原值，非正位置 ×0 = 0
    # 这就是 ReLU 的定义：max(0, x)
    # 梯度流：乘法操作天然支持反向传播（梯度在正区间为1，非正区间为0）
    return x * mask.float()"""

ANNOTATIONS["relu"]["interview"] = """# ✅ INTERVIEW

def relu(x: torch.Tensor) -> torch.Tensor:
    # ---- Step 1: 构造布尔掩码 ----
    # (x > 0) 返回与 x 同 shape 的布尔张量
    # True 表示该位置为正数，False 表示非正
    mask = (x > 0)

    # ---- Step 2: 转浮点并逐元素相乘 ----
    # 必须 .float()：PyTorch 不允许 bool 张量直接参与算术运算
    # 乘法实现：正数 ×1 = 原值，非正数 ×0 = 0
    # 面试要点：这个实现自动支持梯度（autograd 会记录乘法操作）
    # 数值稳定性：ReLU 没有数值稳定问题（不像 softmax/exp）
    return x * mask.float()

# 面试常见追问：
# Q: 为什么不用 torch.clamp(x, min=0)？
# A: 可以，但面试要求手写底层实现。clamp 内部也是类似逻辑。
# Q: ReLU 的缺点？
# A: "dead neuron"问题——如果输入持续为负，梯度永远为0，参数不再更新。
#    解决方案：Leaky ReLU、PReLU、ELU 等变体。"""

ANNOTATIONS["relu"]["summary"] = """## 📝 核心思路总结

1. **ReLU 的本质**：逐元素 max(0, x)，用布尔掩码 + 乘法即可实现
2. **布尔转浮点**：PyTorch 不支持 bool × float，必须先 `.float()`
3. **梯度流**：乘法操作天然支持 autograd，正区间梯度为1，非正区间为0
4. **面试扩展**：dead neuron 问题及 Leaky ReLU 等变体"""


# ---- 2. softmax ----
ANNOTATIONS["softmax"] = {}
ANNOTATIONS["softmax"]["reference"] = """# ✅ SOLUTION

def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    # ---- Step 1: 数值稳定性——减去最大值 ----
    # softmax(x_i) = exp(x_i) / Σ exp(x_j)
    # 问题：如果 x 中有很大的正数（如 1000），exp(1000) 会溢出 inf
    # 技巧：减去最大值 max(x)，因为 softmax 对平移不变：
    #   softmax(x_i - c) = exp(x_i - c) / Σ exp(x_j - c)
    #                     = exp(x_i)·exp(-c) / Σ exp(x_j)·exp(-c)
    #                     = softmax(x_i)
    # 这样最大值变为 0，exp(0)=1，其他值为负数，exp 一定在 (0,1] 范围
    x_max = x.max(dim=dim, keepdim=True).values

    # ---- Step 2: 减去最大值后的指数 ----
    # x_shifted 的最大值为 0，所有 exp 结果 ∈ (0, 1]，不会溢出
    x_shifted = x - x_max

    # ---- Step 3: 计算指数 ----
    exp_x = torch.exp(x_shifted)

    # ---- Step 4: 求和（归一化分母） ----
    # keepdim=True 保持维度，使后续除法能正确广播
    # 例如 x shape=[3,4]，dim=-1 → sum shape=[3,1]（而非 [3]）
    sum_exp = exp_x.sum(dim=dim, keepdim=True)

    # ---- Step 5: 逐元素除法得到概率分布 ----
    # 结果每一行（沿 dim）之和为 1，值域 (0, 1]
    return exp_x / sum_exp"""

ANNOTATIONS["softmax"]["interview"] = """# ✅ INTERVIEW

def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    # ---- Step 1: 数值稳定性——减去最大值 ----
    # 核心技巧：softmax 对常数平移不变，减去 max 防止 exp 溢出
    # x.max(dim, keepdim) 返回 named tuple，.values 取最大值张量
    # keepdim=True：保持 dim 维度为 1，便于后续广播
    x_max = x.max(dim=dim, keepdim=True).values

    # ---- Step 2: 平移 ----
    # 平移后最大值为 0，exp(0)=1，其余 exp ∈ (0,1)
    x_shifted = x - x_max

    # ---- Step 3: 指数 ----
    # exp 是单调递增函数，保持相对大小关系
    exp_x = torch.exp(x_shifted)

    # ---- Step 4: 归一化 ----
    # sum(dim, keepdim) 沿指定维度求和，保持维度以便广播
    # 除法后每行和为 1，得到合法概率分布
    sum_exp = exp_x.sum(dim=dim, keepdim=True)
    return exp_x / sum_exp

# 面试高频考点：
# 1. 为什么要减 max？防止 exp 溢出（数值稳定性）
# 2. 为什么 keepdim=True？保持形状以便广播除法
# 3. softmax 的梯度？Jacobian 矩阵较复杂，但 CrossEntropyLoss 合并计算更高效
# 4. 温度参数？softmax(x/T)，T→0 趋近 argmax，T→∞ 趋近均匀分布"""

ANNOTATIONS["softmax"]["summary"] = """## 📝 核心思路总结

1. **数值稳定性**：减去 max 防止 exp 溢出，这是 softmax 实现的核心技巧
2. **keepdim 的作用**：保持求和维度，使除法能正确广播
3. **平移不变性**：softmax(x - c) = softmax(x)，数学上等价
4. **面试要点**：温度参数、梯度推导、与 CrossEntropyLoss 的关系"""


# ---- 3. linear ----
ANNOTATIONS["linear"] = {}
ANNOTATIONS["linear"]["reference"] = """# ✅ SOLUTION

def linear(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor = None) -> torch.Tensor:
    # ---- Step 1: 矩阵乘法 x @ W^T ----
    # PyTorch 的 Linear 层定义：y = x @ W^T + b
    # 为什么是 W^T？因为 PyTorch 存储 weight shape 为 [out_features, in_features]
    # 而数学上 y = Wx + b 中 W 是 [out, in]，所以 x @ W.T 才能对齐
    # 例如 x=[batch, in], W=[out, in], W.T=[in, out]
    # x @ W.T → [batch, in] @ [in, out] = [batch, out] ✓
    output = x @ weight.T

    # ---- Step 2: 加偏置（可选） ----
    # bias shape 通常为 [out_features]，广播机制自动扩展到 [batch, out]
    # 广播规则：从右往左对齐，维度为1或相等即可
    if bias is not None:
        output = output + bias

    return output"""

ANNOTATIONS["linear"]["interview"] = """# ✅ INTERVIEW

def linear(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor = None) -> torch.Tensor:
    # ---- Step 1: 线性变换 y = x @ W^T + b ----
    # weight shape: [out_features, in_features]
    # x shape: [*, in_features]（* 表示任意前导维度，如 batch）
    # weight.T shape: [in_features, out_features]
    # 矩阵乘法：[*, in] @ [in, out] = [*, out]
    output = x @ weight.T

    # ---- Step 2: 加偏置 ----
    # bias shape: [out_features]
    # 广播：[*, out] + [out] → 自动沿 batch 维广播
    # 例如 [32, 768] + [768] → [32, 768]
    if bias is not None:
        output = output + bias

    return output

# 面试追问：
# Q: 为什么 PyTorch 用 weight.T 而不是直接 weight？
# A: 存储 [out, in] 方便按行访问输出神经元对应的权重，且与 Kaiming/Xavier 初始化公式对齐
# Q: 矩阵乘法的计算复杂度？
# A: O(batch × in × out)，即每个输出元素需要 in 次乘加"""

ANNOTATIONS["linear"]["summary"] = """## 📝 核心思路总结

1. **线性变换本质**：y = x @ W^T + b，矩阵乘法 + 广播加偏置
2. **权重转置原因**：PyTorch 存储为 [out, in]，需转置后与 x 做矩阵乘
3. **广播机制**：bias [out] 自动广播到 [batch, out]
4. **计算复杂度**：O(batch × in × out)"""


# ---- 4. layernorm ----
ANNOTATIONS["layernorm"] = {}
ANNOTATIONS["layernorm"]["reference"] = """# ✅ SOLUTION

def layernorm(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    # Layer Norm 对每个样本的最后几个维度做归一化
    # 公式：y = γ * (x - μ) / √(σ² + ε) + β
    # 其中 μ, σ² 是沿归一化维度的均值和方差

    # ---- Step 1: 计算均值 ----
    # keepdim=True 保持维度，便于后续广播
    # 例如 x shape=[32, 768]，沿 dim=-1 → mean shape=[32, 1]
    mean = x.mean(dim=-1, keepdim=True)

    # ---- Step 2: 计算方差 ----
    # Var(x) = E[(x - μ)²] = E[x²] - μ²
    # 这里用 (x - mean)² 的均值，即有偏方差（PyTorch 默认 behavior）
    var = ((x - mean) ** 2).mean(dim=-1, keepdim=True)

    # ---- Step 3: 归一化 ----
    # 减均值除标准差，得到均值为0方差为1的分布
    # eps=1e-5 防止除零（当方差接近0时）
    x_norm = (x - mean) / torch.sqrt(var + eps)

    # ---- Step 4: 仿射变换（可学习参数） ----
    # γ (weight) 和 β (bias) 是可学习的缩放和偏移参数
    # 让网络可以"撤销"归一化（如果需要的话）
    # weight, bias shape 通常为 [768]，广播到 [32, 768]
    return weight * x_norm + bias"""

ANNOTATIONS["layernorm"]["interview"] = """# ✅ INTERVIEW

def layernorm(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    # ---- Step 1: 沿最后一维求均值 ----
    # keepdim=True：[32, 768] → [32, 1]（而非 [32]），方便广播
    mean = x.mean(dim=-1, keepdim=True)

    # ---- Step 2: 沿最后一维求方差 ----
    # 用 (x - mean)² 的均值，这是总体方差（除以 N，非 N-1）
    # 面试关键：为什么不用无偏估计（除以 N-1）？
    # A: 深度学习中 N 通常很大，N vs N-1 差异可忽略，且 PyTorch 默认用有偏
    var = ((x - mean) ** 2).mean(dim=-1, keepdim=True)

    # ---- Step 3: 归一化 ----
    # 标准化公式：(x - μ) / √(σ² + ε)
    # eps 的作用：防止方差为0时除零（例如全常数输入）
    x_norm = (x - mean) / torch.sqrt(var + eps)

    # ---- Step 4: 仿射变换 ----
    # γ * x_norm + β：可学习的缩放和偏移
    # 为什么要这一步？纯归一化会限制网络表达能力
    # γ, β 让网络可以学习"需要多少归一化"
    return weight * x_norm + bias

# 面试追问：
# Q: LayerNorm vs BatchNorm 区别？
# A: LN 沿特征维度归一化（每个样本独立），BN 沿 batch 维度归一化
# Q: 为什么 Transformer 用 LN 不用 BN？
# A: 序列长度可变，batch 统计不稳定；LN 不依赖 batch，更稳定"""

ANNOTATIONS["layernorm"]["summary"] = """## 📝 核心思路总结

1. **归一化公式**：(x - μ) / √(σ² + ε)，沿最后维度计算统计量
2. **keepdim 的必要性**：保持维度用于广播，避免形状错误
3. **仿射变换**：γ, β 可学习参数，让网络恢复表达能力
4. **eps 的作用**：数值稳定，防止除零"""


# ---- 5. attention ----
ANNOTATIONS["attention"] = {}
ANNOTATIONS["attention"]["reference"] = """# ✅ SOLUTION

def attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
    # Scaled Dot-Product Attention
    # 公式：Attention(Q, K, V) = softmax(Q @ K^T / √d_k) @ V
    # 这是 Transformer 的核心计算单元

    # ---- Step 1: 获取键的维度 d_k ----
    # key shape: [batch, seq_len, d_k]
    # d_k 用于缩放，防止点积值过大导致 softmax 梯度消失
    d_k = key.size(-1)

    # ---- Step 2: 计算注意力分数 Q @ K^T ----
    # query: [batch, seq_q, d_k], key: [batch, seq_k, d_k]
    # key.transpose(-2, -1): [batch, d_k, seq_k]
    # scores: [batch, seq_q, seq_k] — 每个 query 对每个 key 的相似度
    scores = query @ key.transpose(-2, -1)

    # ---- Step 3: 缩放 ----
    # 除以 √d_k：当 d_k 较大时，点积值方差为 d_k
    # 不缩放的话 softmax 会趋向 one-hot，梯度极小
    # 缩放后方差为 1，softmax 输出更平滑
    scores = scores / math.sqrt(d_k)

    # ---- Step 4: 应用 mask（可选） ----
    # mask 通常用于：
    #   - padding mask：忽略填充位置
    #   - causal mask：防止看到未来信息
    # 将 mask 为 0 的位置设为 -inf，softmax 后变为 0
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # ---- Step 5: softmax 归一化 ----
    # 沿最后一维（key 维度）做 softmax
    # 得到注意力权重，每行和为 1
    attn_weights = torch.softmax(scores, dim=-1)

    # ---- Step 6: 加权求和 ----
    # attn_weights: [batch, seq_q, seq_k] @ value: [batch, seq_k, d_v]
    # output: [batch, seq_q, d_v] — 每个 query 位置的上下文向量
    return attn_weights @ value"""

ANNOTATIONS["attention"]["interview"] = """# ✅ INTERVIEW

def attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
    # ---- Step 1: 计算缩放点积注意力分数 ----
    # Q @ K^T：衡量每个 query 与每个 key 的相似度
    # key.transpose(-2, -1)：交换最后两维 [B,S,D] → [B,D,S]
    # scores shape: [batch, seq_q, seq_k]
    d_k = key.size(-1)
    scores = query @ key.transpose(-2, -1)

    # ---- Step 2: 缩放 ----
    # 为什么要除以 √d_k？
    # 假设 Q,K 元素独立同分布，均值0方差1
    # 则点积的均值为0，方差为 d_k
    # d_k 越大，值越大，softmax 越趋近 one-hot → 梯度消失
    # 除以 √d_k 使方差回到 1
    scores = scores / math.sqrt(d_k)

    # ---- Step 3: Mask ----
    # masked_fill：将条件为 True 的位置替换为指定值
    # -inf 经过 softmax 后变为 0（exp(-inf) = 0）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # ---- Step 4: 手写 softmax（面试版） ----
    # 数值稳定：减去最大值
    scores_max = scores.max(dim=-1, keepdim=True).values
    scores_shifted = scores - scores_max
    exp_scores = torch.exp(scores_shifted)
    sum_exp = exp_scores.sum(dim=-1, keepdim=True)
    attn_weights = exp_scores / sum_exp

    # ---- Step 5: 加权求和 ----
    # 注意力权重 × value = 上下文向量
    # [B, Sq, Sk] @ [B, Sk, D] = [B, Sq, D]
    return attn_weights @ value

# 面试高频考点：
# Q: 为什么叫"scaled" dot-product？
# A: 因为除以 √d_k 做了缩放
# Q: 复杂度？
# A: O(seq_q × seq_k × d_k)，即序列长度的平方级
# Q: mask 的两种类型？
# A: padding mask（忽略填充）+ causal mask（防止看到未来）"""

ANNOTATIONS["attention"]["summary"] = """## 📝 核心思路总结

1. **核心公式**：softmax(QK^T / √d_k) @ V，缩放点积注意力
2. **缩放原因**：防止点积过大导致 softmax 梯度消失
3. **Mask 机制**：-inf 经 softmax 变 0，实现选择性忽略
4. **复杂度**：O(n²d)，序列长度的平方级"""


# ---- 6. mha ----
ANNOTATIONS["mha"] = {}
ANNOTATIONS["mha"]["reference"] = """# ✅ SOLUTION

def multi_head_attention(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    # Multi-Head Attention：将注意力分成多个头并行计算
    # 直觉：每个头学习不同的注意力模式（语法、语义、位置等）

    batch_size, seq_len, d_model = x.shape
    # ---- Step 1: 计算每个头的维度 ----
    # d_model 必须能被 num_heads 整除
    d_k = d_model // num_heads

    # ---- Step 2: 线性投影得到 Q, K, V ----
    # x: [B, S, d_model] @ W_q: [d_model, d_model] → Q: [B, S, d_model]
    # 每个头的权重被"隐式"包含在同一个大矩阵中
    Q = x @ W_q
    K = x @ W_k
    V = x @ W_v

    # ---- Step 3: 拆分成多头 ----
    # [B, S, d_model] → [B, S, num_heads, d_k] → [B, num_heads, S, d_k]
    # transpose(1,2) 把 num_heads 维提前，方便批量做注意力
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K = K.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V = V.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    # ---- Step 4: 缩放点积注意力 ----
    # scores: [B, num_heads, S, S] — 每个头独立计算注意力
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    # ---- Step 5: Mask（可选） ----
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # ---- Step 6: Softmax + 加权求和 ----
    attn = torch.softmax(scores, dim=-1)
    # attn: [B, H, S, S] @ V: [B, H, S, d_k] → [B, H, S, d_k]
    out = attn @ V

    # ---- Step 7: 合并多头 ----
    # transpose 回来：[B, H, S, d_k] → [B, S, H, d_k]
    # contiguous()：transpose 后内存不连续，需要重新排列
    # view：合并 H 和 d_k 回 d_model
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)

    # ---- Step 8: 输出投影 ----
    # 最终线性变换，混合各头的信息
    return out @ W_o"""

ANNOTATIONS["mha"]["interview"] = """# ✅ INTERVIEW

def multi_head_attention(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ---- Step 1: QKV 投影 ----
    # 线性变换：[B, S, d] @ [d, d] = [B, S, d]
    Q = x @ W_q
    K = x @ W_k
    V = x @ W_v

    # ---- Step 2: 拆分多头 ----
    # view: [B, S, d] → [B, S, H, d_k]
    # transpose(1,2): [B, S, H, d_k] → [B, H, S, d_k]
    # 关键：transpose 后内存不连续，必须 contiguous() 才能 view
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K = K.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V = V.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    # ---- Step 3: 注意力计算 ----
    # 每个头独立计算：[B, H, S, d_k] @ [B, H, d_k, S] = [B, H, S, S]
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # 手写 softmax
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    # ---- Step 4: 加权求和 ----
    out = attn @ V  # [B, H, S, d_k]

    # ---- Step 5: 合并多头 ----
    # transpose: [B, H, S, d_k] → [B, S, H, d_k]
    # contiguous().view: 合并最后两维 → [B, S, d_model]
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)

    # ---- Step 6: 输出投影 ----
    return out @ W_o

# 面试追问：
# Q: 为什么要多头而不是单头？
# A: 多头让模型同时关注不同子空间的信息（类似 CNN 多通道）
# Q: 为什么需要 contiguous()？
# A: transpose 只改变步长不改变内存布局，view 需要连续内存"""

ANNOTATIONS["mha"]["summary"] = """## 📝 核心思路总结

1. **多头拆分**：将 d_model 拆成 num_heads × d_k，各头独立计算注意力
2. **view + transpose**：reshape 的关键操作，注意 contiguous() 的必要性
3. **输出投影**：W_o 混合各头信息，恢复到 d_model 维度
4. **为什么多头**：不同头学习不同的注意力模式"""


# ---- 7. batchnorm ----
ANNOTATIONS["batchnorm"] = {}
ANNOTATIONS["batchnorm"]["reference"] = """# ✅ SOLUTION

def batchnorm(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, running_mean: torch.Tensor, running_var: torch.Tensor, training: bool = True, momentum: float = 0.1, eps: float = 1e-5) -> torch.Tensor:
    # Batch Norm 沿 batch 维度归一化（对每个特征通道独立计算）
    # x shape: [batch, features] 或 [batch, features, ...]
    # 归一化维度：除 batch 维外的所有维度

    # ---- 确定归一化维度 ----
    # 对于 2D: [B, F] → dims=[0]
    # 对于 4D: [B, C, H, W] → dims=[0, 2, 3]
    # 即"除特征维外的所有维度"
    dims = [0] + list(range(2, x.ndim))

    if training:
        # ---- 训练模式：用当前 batch 的统计量 ----
        # Step 1: 计算 batch 均值
        mean = x.mean(dim=dims)

        # Step 2: 计算 batch 方差
        var = x.var(dim=dims, unbiased=False)

        # Step 3: 更新 running statistics（指数移动平均）
        # running_mean = (1-momentum) * running_mean + momentum * batch_mean
        # momentum 越大，越信任当前 batch
        running_mean[:] = (1 - momentum) * running_mean + momentum * mean
        running_var[:] = (1 - momentum) * running_var + momentum * var
    else:
        # ---- 推理模式：用训练时积累的 running statistics ----
        mean = running_mean
        var = running_var

    # ---- Step 4: 归一化 ----
    # reshape mean/var 为可广播的形状
    # 2D: [F] → [1, F]; 4D: [C] → [1, C, 1, 1]
    shape = [1, -1] + [1] * (x.ndim - 2)
    mean_r = mean.view(shape)
    var_r = var.view(shape)

    x_norm = (x - mean_r) / torch.sqrt(var_r + eps)

    # ---- Step 5: 仿射变换 ----
    return weight.view(shape) * x_norm + bias.view(shape)"""

ANNOTATIONS["batchnorm"]["interview"] = """# ✅ INTERVIEW

def batchnorm(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, running_mean: torch.Tensor, running_var: torch.Tensor, training: bool = True, momentum: float = 0.1, eps: float = 1e-5) -> torch.Tensor:
    # 归一化维度：batch 维 + 空间维（如果是高维）
    dims = [0] + list(range(2, x.ndim))

    if training:
        # ---- 训练：用 batch 统计量 ----
        mean = x.mean(dim=dims)
        var = x.var(dim=dims, unbiased=False)

        # ---- 更新 running statistics ----
        # 指数移动平均（EMA）：smoothed = (1-α) * old + α * new
        # running 用于推理时的归一化
        running_mean[:] = (1 - momentum) * running_mean + momentum * mean
        running_var[:] = (1 - momentum) * running_var + momentum * var
    else:
        # ---- 推理：用 running 统计量 ----
        # 推理时 batch 可能很小（甚至为1），不能用 batch 统计
        mean = running_mean
        var = running_var

    # ---- reshape 为可广播形状 ----
    # [F] → [1, F, 1, 1]（4D 情况）或 [1, F]（2D 情况）
    shape = [1, -1] + [1] * (x.ndim - 2)
    mean_r = mean.view(shape)
    var_r = var.view(shape)

    # ---- 归一化 + 仿射 ----
    x_norm = (x - mean_r) / torch.sqrt(var_r + eps)
    return weight.view(shape) * x_norm + bias.view(shape)

# 面试追问：
# Q: BN 训练和推理的区别？
# A: 训练用 batch 统计，推理用 running 统计
# Q: momentum 参数？
# A: 控制 EMA 速度，越大越信任当前 batch
# Q: BN 的问题？
# A: 依赖 batch size，小 batch 统计不稳定；序列长度不适用（用 LN）"""

ANNOTATIONS["batchnorm"]["summary"] = """## 📝 核心思路总结

1. **训练 vs 推理**：训练用 batch 统计，推理用 running EMA
2. **归一化维度**：沿 batch + 空间维，每个特征通道独立
3. **running statistics**：指数移动平均，momentum 控制更新速度
4. **view 广播**：reshape 统计量为可广播形状是关键"""


# ---- 8. rmsnorm ----
ANNOTATIONS["rmsnorm"] = {}
ANNOTATIONS["rmsnorm"]["reference"] = """# ✅ SOLUTION

def rmsnorm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    # RMS Norm（Root Mean Square Normalization）
    # 比 LayerNorm 更简单：不减均值，只除以 RMS
    # 公式：y = x / RMS(x) * γ，其中 RMS(x) = √(mean(x²))
    # 优点：计算更快（省去均值计算），在 LLM 中广泛使用（LLaMA, GPT-NeoX 等）

    # ---- Step 1: 计算均方值 ----
    # x.pow(2) 或 x ** 2：逐元素平方
    # .mean(dim=-1, keepdim=True)：沿最后一维求均值
    # 例如 x shape=[32, 768] → rms_sq shape=[32, 1]
    rms_sq = x.pow(2).mean(dim=-1, keepdim=True)

    # ---- Step 2: 计算 RMS 并归一化 ----
    # rms = √(mean(x²))，加 eps 防止除零
    # x / rms：将每个向量缩放到 RMS=1
    x_norm = x / torch.sqrt(rms_sq + eps)

    # ---- Step 3: 仿射变换 ----
    # 只有缩放 γ，没有偏移 β（比 LayerNorm 少一个参数）
    # 这是 RMSNorm 的设计选择，减少参数量
    return weight * x_norm"""

ANNOTATIONS["rmsnorm"]["interview"] = """# ✅ INTERVIEW

def rmsnorm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    # ---- Step 1: 计算均方值 ----
    # RMS² = mean(x²)，沿最后一维
    # 与 LayerNorm 的区别：不减均值，直接算平方的均值
    # 数学上：RMS(x) = √(1/d × Σx_i²)
    rms_sq = x.pow(2).mean(dim=-1, keepdim=True)

    # ---- Step 2: 归一化 ----
    # x / RMS(x)：缩放到 RMS ≈ 1
    # eps=1e-6（比 LayerNorm 的 1e-5 更小，因为 RMS 通常更大）
    x_norm = x / torch.sqrt(rms_sq + eps)

    # ---- Step 3: 缩放 ----
    # 只有 γ 没有 β，这是 RMSNorm 的特点
    return weight * x_norm

# 面试追问：
# Q: RMSNorm vs LayerNorm？
# A: RMSNorm 不减均值，计算更快；只有 γ 没有 β
# Q: 为什么现代 LLM 用 RMSNorm？
# A: 计算效率更高，实验效果与 LayerNorm 相当"""

ANNOTATIONS["rmsnorm"]["summary"] = """## 📝 核心思路总结

1. **RMS 公式**：√(mean(x²))，不减均值，比 LayerNorm 更简洁
2. **只有 γ 没有 β**：减少参数，计算更快
3. **数值稳定**：eps 防止除零
4. **现代 LLM 标配**：LLaMA、GPT-NeoX 等都用 RMSNorm"""


# ---- 9. causal_attention ----
ANNOTATIONS["causal_attention"] = {}
ANNOTATIONS["causal_attention"]["reference"] = """# ✅ SOLUTION

def causal_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> torch.Tensor:
    # Causal (Masked) Self-Attention
    # 核心区别：每个位置只能看到自己和之前的位置，不能看到未来
    # 这是自回归模型（GPT等）的关键，保证生成时的因果性

    d_k = key.size(-1)

    # ---- Step 1: 计算注意力分数 ----
    scores = query @ key.transpose(-2, -1) / math.sqrt(d_k)

    # ---- Step 2: 创建因果 mask ----
    # torch.triu(diagonal=1) 生成上三角矩阵（对角线以上为1，以下为0）
    # 例如 seq_len=4：
    # [[0, 1, 1, 1],
    #  [0, 0, 1, 1],
    #  [0, 0, 0, 1],
    #  [0, 0, 0, 0]]
    # 位置 i 只能看到 ≤ i 的位置
    seq_len = query.size(-2)
    causal_mask = torch.triu(torch.ones(seq_len, seq_len, device=query.device), diagonal=1).bool()

    # ---- Step 3: 应用 mask ----
    # 将上三角（未来位置）设为 -inf
    # softmax 后这些位置变为 0，实现因果性
    scores = scores.masked_fill(causal_mask, float('-inf'))

    # ---- Step 4: Softmax + 加权求和 ----
    attn_weights = torch.softmax(scores, dim=-1)
    return attn_weights @ value"""

ANNOTATIONS["causal_attention"]["interview"] = """# ✅ INTERVIEW

def causal_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> torch.Tensor:
    d_k = key.size(-1)

    # ---- Step 1: 注意力分数 ----
    scores = query @ key.transpose(-2, -1) / math.sqrt(d_k)

    # ---- Step 2: 因果 mask ----
    # torch.triu 上三角，diagonal=1 表示不包含对角线
    # 结果：位置 i 只能关注 j ≤ i
    seq_len = query.size(-2)
    causal_mask = torch.triu(torch.ones(seq_len, seq_len, device=query.device), diagonal=1).bool()

    # ---- Step 3: mask + softmax ----
    # masked_fill(condition, value)：条件为 True 的位置填 value
    scores = scores.masked_fill(causal_mask, float('-inf'))

    # 手写 softmax
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn_weights = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    return attn_weights @ value

# 面试追问：
# Q: 为什么需要 causal mask？
# A: 自回归生成时，预测第 t 个 token 只能用 0..t-1 的信息
# Q: triu 的 diagonal 参数？
# A: diagonal=0 包含对角线，diagonal=1 不包含"""

ANNOTATIONS["causal_attention"]["summary"] = """## 📝 核心思路总结

1. **因果性**：每个位置只能看到自己和之前的位置
2. **上三角 mask**：torch.triu(diagonal=1) 生成未来位置的 mask
3. **-inf → softmax → 0**：mask 的标准实现方式
4. **自回归基础**：GPT 等生成模型的核心机制"""


# ---- 10. gqa ----
ANNOTATIONS["gqa"] = {}
ANNOTATIONS["gqa"]["reference"] = """# ✅ SOLUTION

def grouped_query_attention(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, num_kv_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    # Grouped Query Attention (GQA)
    # MHA: 每个 head 有自己的 Q, K, V
    # GQA: 多个 query head 共享一组 K, V（减少 KV cache 大小）
    # 例如 num_heads=8, num_kv_heads=2 → 每 4 个 query head 共享 1 组 KV

    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ---- Step 1: 投影 Q, K, V ----
    Q = x @ W_q  # [B, S, d_model]
    K = x @ W_k  # [B, S, num_kv_heads * d_k]
    V = x @ W_v  # [B, S, num_kv_heads * d_k]

    # ---- Step 2: 拆分并 reshape ----
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)  # [B, H, S, d_k]
    K = K.view(batch_size, seq_len, num_kv_heads, d_k).transpose(1, 2)  # [B, G, S, d_k]
    V = V.view(batch_size, seq_len, num_kv_heads, d_k).transpose(1, 2)  # [B, G, S, d_k]

    # ---- Step 3: 扩展 KV 以匹配 Q 的 head 数 ----
    # repeat_interleave：将每个 KV head 复制 num_heads//num_kv_heads 次
    # 例如 2 KV heads → 8 KV heads（每个复制 4 次）
    n_rep = num_heads // num_kv_heads
    K = K.repeat_interleave(n_rep, dim=1)
    V = V.repeat_interleave(n_rep, dim=1)

    # ---- Step 4: 标准注意力计算 ----
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attn = torch.softmax(scores, dim=-1)
    out = attn @ V

    # ---- Step 5: 合并多头 + 输出投影 ----
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    return out @ W_o"""

ANNOTATIONS["gqa"]["interview"] = """# ✅ INTERVIEW

def grouped_query_attention(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, num_kv_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ---- Step 1: 投影 ----
    Q = x @ W_q  # [B, S, d_model]
    K = x @ W_k  # [B, S, num_kv_heads * d_k]
    V = x @ W_v  # [B, S, num_kv_heads * d_k]

    # ---- Step 2: 拆分 ----
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K = K.view(batch_size, seq_len, num_kv_heads, d_k).transpose(1, 2)
    V = V.view(batch_size, seq_len, num_kv_heads, d_k).transpose(1, 2)

    # ---- Step 3: KV 扩展 ----
    # repeat_interleave：将 KV heads 复制以匹配 query heads
    # 关键：不是 expand，需要实际复制数据
    n_rep = num_heads // num_kv_heads
    K = K.repeat_interleave(n_rep, dim=1)
    V = V.repeat_interleave(n_rep, dim=1)

    # ---- Step 4: 注意力 ----
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # 手写 softmax
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    out = attn @ V

    # ---- Step 5: 合并 + 投影 ----
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    return out @ W_o

# 面试追问：
# Q: GQA vs MHA vs MQA？
# A: MHA 每 head 独立 KV；GQA 多 head 共享 KV；MQA 所有 head 共享 1 组 KV
# Q: 为什么用 GQA？
# A: 减少 KV cache 大小，推理更快，效果接近 MHA"""

ANNOTATIONS["gqa"]["summary"] = """## 📝 核心思路总结

1. **GQA 核心**：多个 query head 共享 KV head，减少 KV cache
2. **repeat_interleave**：扩展 KV 以匹配 query head 数
3. **GQA = MHA + MQA 的折中**：平衡效果和效率
4. **推理优化**：KV cache 减少 num_heads/num_kv_heads 倍"""


# ---- 11. sliding_window ----
ANNOTATIONS["sliding_window"] = {}
ANNOTATIONS["sliding_window"]["reference"] = """# ✅ SOLUTION

def sliding_window_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, window_size: int, mask: torch.Tensor = None) -> torch.Tensor:
    # Sliding Window Attention
    # 每个位置只关注局部窗口内的位置，而非全部序列
    # 复杂度从 O(n²) 降到 O(n × w)，w = window_size
    # 用于 Longformer、Mistral 等长序列模型

    d_k = key.size(-1)
    seq_len = query.size(-2)

    # ---- Step 1: 计算注意力分数 ----
    scores = query @ key.transpose(-2, -1) / math.sqrt(d_k)

    # ---- Step 2: 创建滑动窗口 mask ----
    # 位置 i 只能关注 [i-window_size, i+window_size] 范围内的位置
    # i - j 的绝对值 > window_size 的位置被 mask 掉
    # torch.arange(seq_len) - torch.arange(seq_len).unsqueeze(1) 得到相对距离矩阵
    positions = torch.arange(seq_len, device=query.device)
    rel_dist = (positions.unsqueeze(0) - positions.unsqueeze(1)).abs()
    window_mask = rel_dist > window_size  # True 表示超出窗口

    # ---- Step 3: 应用 mask ----
    scores = scores.masked_fill(window_mask, float('-inf'))

    # ---- Step 4: 额外 mask（如因果 mask） ----
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # ---- Step 5: Softmax + 加权求和 ----
    attn_weights = torch.softmax(scores, dim=-1)
    return attn_weights @ value"""

ANNOTATIONS["sliding_window"]["interview"] = """# ✅ INTERVIEW

def sliding_window_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, window_size: int, mask: torch.Tensor = None) -> torch.Tensor:
    d_k = key.size(-1)
    seq_len = query.size(-2)

    # ---- Step 1: 注意力分数 ----
    scores = query @ key.transpose(-2, -1) / math.sqrt(d_k)

    # ---- Step 2: 滑动窗口 mask ----
    # 位置 i 和 j 的距离 |i-j| > window_size 则 mask
    positions = torch.arange(seq_len, device=query.device)
    # unsqueeze(0) 和 unsqueeze(1) 配合广播得到 [S, S] 距离矩阵
    rel_dist = (positions.unsqueeze(0) - positions.unsqueeze(1)).abs()
    window_mask = rel_dist > window_size

    # ---- Step 3: 应用 mask ----
    scores = scores.masked_fill(window_mask, float('-inf'))

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # ---- Step 4: softmax + 求和 ----
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn_weights = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    return attn_weights @ value

# 面试追问：
# Q: 滑动窗口注意力的复杂度？
# A: O(n × w)，w 为窗口大小，相比全局 O(n²) 大幅降低
# Q: 如何捕获全局信息？
# A: 可以交替使用全局和局部注意力层（如 Longformer）"""

ANNOTATIONS["sliding_window"]["summary"] = """## 📝 核心思路总结

1. **局部注意力**：每个位置只关注窗口大小范围内的位置
2. **距离 mask**：|i-j| > window_size 的位置设为 -inf
3. **复杂度优化**：O(n²) → O(n×w)
4. **长序列处理**：Longformer、Mistral 等模型的基础"""


# ---- 12. linear_attention ----
ANNOTATIONS["linear_attention"] = {}
ANNOTATIONS["linear_attention"]["reference"] = """# ✅ SOLUTION

def linear_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
    # Linear Attention
    # 标准注意力：softmax(QK^T)V，需要计算 S×S 矩阵 → O(S²D)
    # 线性注意力：用核函数近似 softmax，改变计算顺序 → O(SD²)
    # 关键技巧：φ(Q)(φ(K)^T V) 先算 KV 再乘 Q

    d_k = key.size(-1)

    # ---- Step 1: 核函数映射 ----
    # 用 elu + 1 近似 softmax 的核函数
    # elu(x) + 1 保证非负（类似 exp 的效果但计算更快）
    # φ(x) = elu(x) + 1
    Q = torch.nn.functional.elu(query) + 1
    K = torch.nn.functional.elu(key) + 1

    # ---- Step 2: 计算 KV 矩阵（核心优化） ----
    # 标准：Q @ K^T @ V → O(S²D)
    # 线性：K^T @ V → O(SD²)，然后 Q @ (K^T V) → O(SD²)
    # K^T: [B, H, D, S] @ V: [B, H, S, D] → KV: [B, H, D, D]
    # 这是 O(SD²) 而非 O(S²D)，当 S > D 时更快
    KV = K.transpose(-2, -1) @ value

    # ---- Step 3: Q 乘以 KV ----
    # Q: [B, H, S, D] @ KV: [B, H, D, D] → output: [B, H, S, D]
    output = Q @ KV

    # ---- Step 4: 归一化 ----
    # 除以 Z = φ(K) 的行和，起到类似 softmax 分母的作用
    # Z: [B, H, S, 1]
    Z = Q @ K.transpose(-2, -1).sum(dim=-1, keepdim=True)
    output = output / (Z + 1e-6)

    return output"""

ANNOTATIONS["linear_attention"]["interview"] = """# ✅ INTERVIEW

def linear_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
    d_k = key.size(-1)

    # ---- Step 1: 核函数映射 ----
    # elu(x) + 1：近似 exp，但计算更简单
    # 关键：保持非负性，这是线性注意力能分解的前提
    Q = torch.nn.functional.elu(query) + 1
    K = torch.nn.functional.elu(key) + 1

    # ---- Step 2: 先算 K^T @ V ----
    # 标准注意力顺序：(Q @ K^T) @ V → O(S²D)
    # 线性注意力顺序：Q @ (K^T @ V) → O(SD²)
    # 利用矩阵乘法结合律，改变计算顺序！
    # K^T: [B, H, D, S] @ V: [B, H, S, D] → [B, H, D, D]
    KV = K.transpose(-2, -1) @ value

    # ---- Step 3: Q @ KV ----
    # [B, H, S, D] @ [B, H, D, D] → [B, H, S, D]
    output = Q @ KV

    # ---- Step 4: 归一化 ----
    # Z = Σ φ(k_j)，类似 softmax 的分母
    # 每个 query 的输出需要除以其对应的 Z
    Z = Q @ K.transpose(-2, -1).sum(dim=-1, keepdim=True)
    output = output / (Z + 1e-6)

    return output

# 面试追问：
# Q: 为什么叫"线性"注意力？
# A: 复杂度与序列长度成线性关系 O(SD²)，而非 O(S²)
# Q: 为什么用 elu+1？
# A: 需要非负核函数来近似 softmax，elu+1 保证非负
# Q: 缺点？
# A: 核函数近似损失精度，实际效果可能不如标准注意力"""

ANNOTATIONS["linear_attention"]["summary"] = """## 📝 核心思路总结

1. **核心思想**：改变矩阵乘法顺序，O(S²D) → O(SD²)
2. **核函数**：elu+1 近似 exp，保持非负性
3. **结合律**：Q(K^TV) 先算 KV 再乘 Q
4. **归一化**：除以 Z 保证数值合理性"""


# ---- 13. gpt2_block ----
ANNOTATIONS["gpt2_block"] = {}
ANNOTATIONS["gpt2_block"]["reference"] = """# ✅ SOLUTION

def gpt2_block(x: torch.Tensor, ln1_w: torch.Tensor, ln1_b: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, ln2_w: torch.Tensor, ln2_b: torch.Tensor, W_fc1: torch.Tensor, b_fc1: torch.Tensor, W_fc2: torch.Tensor, b_fc2: torch.Tensor, num_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    # GPT-2 Transformer Block = Self-Attention + FFN + LayerNorm + Residual
    # Pre-Norm 架构：LayerNorm 在注意力/FFN 之前（与原始 Transformer 的 Post-Norm 不同）

    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ============ 子层 1：Multi-Head Self-Attention ============

    # ---- Step 1.1: Pre-Norm ----
    # LayerNorm 在注意力之前，有助于训练稳定性
    mean1 = x.mean(dim=-1, keepdim=True)
    var1 = ((x - mean1) ** 2).mean(dim=-1, keepdim=True)
    x_norm1 = (x - mean1) / torch.sqrt(var1 + 1e-5)
    x_ln1 = ln1_w * x_norm1 + ln1_b

    # ---- Step 1.2: QKV 投影 ----
    Q = x_ln1 @ W_q
    K = x_ln1 @ W_k
    V = x_ln1 @ W_v

    # ---- Step 1.3: 拆分多头 ----
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K = K.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V = V.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    # ---- Step 1.4: 注意力计算 ----
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    attn = torch.softmax(scores, dim=-1)
    attn_out = attn @ V

    # ---- Step 1.5: 合并多头 + 输出投影 ----
    attn_out = attn_out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    attn_out = attn_out @ W_o

    # ---- Step 1.6: 残差连接 ----
    # 残差：让梯度直接流过，缓解深层网络的梯度消失
    x = x + attn_out

    # ============ 子层 2：Feed-Forward Network ============

    # ---- Step 2.1: Pre-Norm ----
    mean2 = x.mean(dim=-1, keepdim=True)
    var2 = ((x - mean2) ** 2).mean(dim=-1, keepdim=True)
    x_norm2 = (x - mean2) / torch.sqrt(var2 + 1e-5)
    x_ln2 = ln2_w * x_norm2 + ln2_b

    # ---- Step 2.2: FFN ----
    # GPT-2 FFN: Linear → GELU → Linear
    # 通常中间维度是 d_model 的 4 倍
    hidden = x_ln2 @ W_fc1 + b_fc1
    hidden = torch.nn.functional.gelu(hidden)
    ffn_out = hidden @ W_fc2 + b_fc2

    # ---- Step 2.3: 残差连接 ----
    x = x + ffn_out

    return x"""

ANNOTATIONS["gpt2_block"]["interview"] = """# ✅ INTERVIEW

def gpt2_block(x: torch.Tensor, ln1_w: torch.Tensor, ln1_b: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, ln2_w: torch.Tensor, ln2_b: torch.Tensor, W_fc1: torch.Tensor, b_fc1: torch.Tensor, W_fc2: torch.Tensor, b_fc2: torch.Tensor, num_heads: int, mask: torch.Tensor = None) -> torch.Tensor:
    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ============ 子层 1：Self-Attention ============

    # ---- Pre-Norm ----
    mean1 = x.mean(dim=-1, keepdim=True)
    var1 = ((x - mean1) ** 2).mean(dim=-1, keepdim=True)
    x_norm1 = (x - mean1) / torch.sqrt(var1 + 1e-5)
    x_ln1 = ln1_w * x_norm1 + ln1_b

    # ---- MHA ----
    Q = x_ln1 @ W_q
    K = x_ln1 @ W_k
    V = x_ln1 @ W_v
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K = K.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V = V.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # 手写 softmax
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    attn_out = attn @ V
    attn_out = attn_out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    attn_out = attn_out @ W_o

    # 残差
    x = x + attn_out

    # ============ 子层 2：FFN ============

    # ---- Pre-Norm ----
    mean2 = x.mean(dim=-1, keepdim=True)
    var2 = ((x - mean2) ** 2).mean(dim=-1, keepdim=True)
    x_norm2 = (x - mean2) / torch.sqrt(var2 + 1e-5)
    x_ln2 = ln2_w * x_norm2 + ln2_b

    # ---- FFN: Linear → GELU → Linear ----
    hidden = x_ln2 @ W_fc1 + b_fc1
    # GELU 近似：0.5 * x * (1 + tanh(sqrt(2/π) * (x + 0.044715 * x³)))
    hidden = torch.nn.functional.gelu(hidden)
    ffn_out = hidden @ W_fc2 + b_fc2

    # 残差
    x = x + ffn_out

    return x

# 面试追问：
# Q: Pre-Norm vs Post-Norm？
# A: Pre-Norm 训练更稳定（梯度更平滑），Post-Norm 理论上效果更好但难训练
# Q: 残差连接的作用？
# A: 缓解梯度消失，让深层网络可训练
# Q: FFN 的作用？
# A: 对每个位置独立做非线性变换，存储知识"""

ANNOTATIONS["gpt2_block"]["summary"] = """## 📝 核心思路总结

1. **Pre-Norm 架构**：LayerNorm 在子层之前，训练更稳定
2. **残差连接**：x + sublayer(x)，梯度的"高速公路"
3. **两个子层**：Self-Attention（建模关系）+ FFN（存储知识）
4. **GELU 激活**：比 ReLU 更平滑，GPT-2 的标准选择"""


# ---- 14. kv_cache ----
ANNOTATIONS["kv_cache"] = {}
ANNOTATIONS["kv_cache"]["reference"] = """# ✅ SOLUTION

def attention_with_kv_cache(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, cached_key: torch.Tensor = None, cached_value: torch.Tensor = None, mask: torch.Tensor = None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # KV Cache：自回归生成时的推理优化
    # 问题：生成每个 token 时都要重新计算所有 token 的 K, V → 重复计算
    # 解决：缓存已计算的 K, V，每次只计算新 token 的 Q, K, V

    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ---- Step 1: 计算当前 token 的 QKV ----
    Q = x @ W_q
    K_new = x @ W_k
    V_new = x @ W_v

    # ---- Step 2: 拆分多头 ----
    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K_new = K_new.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V_new = V_new.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    # ---- Step 3: 拼接缓存 ----
    # torch.cat 沿 seq 维度拼接：旧 KV + 新 KV
    # 首次调用时 cached 为 None，直接用新的
    if cached_key is not None:
        K = torch.cat([cached_key, K_new], dim=2)
        V = torch.cat([cached_value, V_new], dim=2)
    else:
        K = K_new
        V = V_new

    # ---- Step 4: 注意力计算 ----
    # Q 只有新 token 的 query，但 K, V 包含所有历史
    # scores shape: [B, H, new_len, total_len]
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attn = torch.softmax(scores, dim=-1)
    out = attn @ V

    # ---- Step 5: 合并 + 投影 ----
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    return out @ W_o, K, V"""

ANNOTATIONS["kv_cache"]["interview"] = """# ✅ INTERVIEW

def attention_with_kv_cache(x: torch.Tensor, W_q: torch.Tensor, W_k: torch.Tensor, W_v: torch.Tensor, W_o: torch.Tensor, num_heads: int, cached_key: torch.Tensor = None, cached_value: torch.Tensor = None, mask: torch.Tensor = None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # ---- Step 1: QKV 投影 ----
    # 只对当前新输入 x 做投影，不重复计算历史
    Q = x @ W_q
    K_new = x @ W_k
    V_new = x @ W_v

    Q = Q.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    K_new = K_new.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)
    V_new = V_new.view(batch_size, seq_len, num_heads, d_k).transpose(1, 2)

    # ---- Step 2: 拼接缓存 ----
    # 关键：沿 seq 维（dim=2）拼接
    # cached: [B, H, prev_len, D], new: [B, H, 1, D]
    # result: [B, H, prev_len+1, D]
    if cached_key is not None:
        K = torch.cat([cached_key, K_new], dim=2)
        V = torch.cat([cached_value, V_new], dim=2)
    else:
        K = K_new
        V = V_new

    # ---- Step 3: 注意力 ----
    # Q: [B, H, 1, D]（只有新 token）
    # K: [B, H, total_len, D]（所有历史 + 新 token）
    # scores: [B, H, 1, total_len]
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # 手写 softmax
    scores_max = scores.max(dim=-1, keepdim=True).values
    exp_scores = torch.exp(scores - scores_max)
    attn = exp_scores / exp_scores.sum(dim=-1, keepdim=True)

    out = attn @ V

    # ---- Step 4: 合并 + 投影 ----
    out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
    return out @ W_o, K, V

# 面试追问：
# Q: KV Cache 的作用？
# A: 避免重复计算历史 token 的 K, V，将生成复杂度从 O(n²) 降到 O(n)
# Q: 内存占用？
# A: 每层缓存 2 × batch × heads × seq_len × d_k 个 float
# Q: 如何优化 KV Cache 内存？
# A: GQA（减少 KV heads）、量化（int8/int4）、PagedAttention（vLLM）"""

ANNOTATIONS["kv_cache"]["summary"] = """## 📝 核心思路总结

1. **KV Cache 核心**：缓存历史 K, V，每次只计算新 token 的投影
2. **torch.cat 拼接**：沿 seq 维度拼接新旧 KV
3. **推理优化**：避免重复计算，生成复杂度 O(n²) → O(n)
4. **内存权衡**：用空间换时间，需注意 KV cache 内存管理"""


# ============================================================
# MAIN: Generate all notebooks
# ============================================================

TASKS = ["relu", "softmax", "linear", "layernorm", "attention", "mha",
         "batchnorm", "rmsnorm", "causal_attention", "gqa",
         "sliding_window", "linear_attention", "gpt2_block", "kv_cache"]


def main():
    for task_id in TASKS:
        print(f"\n=== Processing: {task_id} ===")

        # Get demo and judge code from existing notebook
        existing_nb = find_existing_nb(task_id, False)
        demo_code = ""
        judge_code = ""
        if existing_nb:
            demo_code, judge_code = extract_cells(existing_nb)

        # Get annotations
        ann = ANNOTATIONS.get(task_id)
        if not ann:
            print(f"  WARNING: No annotations for {task_id}, skipping")
            continue

        # Write reference version
        print("  Writing reference...")
        write_nb(task_id, "reference", ann["reference"], ann["summary"], demo_code, judge_code)

        # Write interview version
        print("  Writing interview...")
        write_nb(task_id, "interview", ann["interview"], ann["summary"], demo_code, judge_code)

    print("\n=== All done! ===")


if __name__ == "__main__":
    main()
