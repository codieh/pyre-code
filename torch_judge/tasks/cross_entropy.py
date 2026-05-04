"""Cross-Entropy Loss task."""

TASK = {
    "title": "Cross-Entropy Loss",
    "difficulty": "Easy",
    "description_en": "Implement cross-entropy loss for classification.\n\nCross-entropy measures the difference between predicted logits and true class labels. It is the standard loss for classification tasks.\n\n**Signature:** `cross_entropy_loss(logits, targets) -> Tensor`\n\n**Parameters:**\n- `logits` — raw scores (B, C) where C is the number of classes\n- `targets` — ground-truth class indices (B,)\n\n**Returns:** scalar mean loss\n\n**Constraints:**\n- Must be numerically stable (handle large logits)\n- Use log-sum-exp trick for stability",
    "description_zh": "实现分类交叉熵损失。\n\n交叉熵衡量预测 logits 与真实类别标签之间的差异，是分类任务的标准损失函数。\n\n**签名:** `cross_entropy_loss(logits, targets) -> Tensor`\n\n**参数:**\n- `logits` — 原始分数 (B, C)，C 为类别数\n- `targets` — 真实类别索引 (B,)\n\n**返回:** 标量平均损失\n\n**约束:**\n- 必须数值稳定（处理大 logits）\n- 使用 log-sum-exp 技巧保证稳定性",
    "function_name": "cross_entropy_loss",
    "hint": "1. `log_probs = logits - logsumexp(logits, dim=-1, keepdim=True)`\n2. `return -log_probs[arange(B), targets].mean()`",
    "hint_zh": "1. `log_probs = logits - logsumexp(logits, dim=-1, keepdim=True)`\n2. `return -log_probs[arange(B), targets].mean()`",
    "tests": [
        {
            "name": "Matches F.cross_entropy",
            "code": "\nimport torch\ntorch.manual_seed(0)\nlogits = torch.randn(4, 10)\ntargets = torch.randint(0, 10, (4,))\nout = {fn}(logits, targets)\nref = torch.nn.functional.cross_entropy(logits, targets)\nassert torch.allclose(out, ref, atol=1e-5), f'Mismatch: {out.item():.4f} vs {ref.item():.4f}'\n"
        },
        {
            "name": "Numerical stability",
            "code": "\nimport torch\nlogits = torch.tensor([[1000., 0., 0.], [0., 1000., 0.]])\ntargets = torch.tensor([0, 1])\nout = {fn}(logits, targets)\nassert not torch.isnan(out), 'NaN with large logits'\nassert not torch.isinf(out), 'Inf with large logits'\nassert out.item() < 0.01, 'Should be ~0 for confident correct predictions'\n"
        },
        {
            "name": "Scalar output",
            "code": "\nimport torch\nout = {fn}(torch.randn(8, 5), torch.randint(0, 5, (8,)))\nassert out.dim() == 0, 'Loss must be a scalar'\n"
        },
        {
            "name": "Gradient flow",
            "code": "\nimport torch\nlogits = torch.randn(8, 5, requires_grad=True)\ntargets = torch.randint(0, 5, (8,))\n{fn}(logits, targets).backward()\nassert logits.grad is not None, 'logits.grad is None'\n"
        }
    ],
    "solution": '''# 交叉熵损失 = -log(softmax(logits)[target])
# 直接算: -log(exp(logits[target]) / sum(exp(logits)))
# 但 exp(大 logits) 会溢出！所以用 log-sum-exp 恒等式:
#   log(softmax(x)) = x - log(sum(exp(x))) = x - logsumexp(x)

def cross_entropy_loss(logits, targets):
    # 第一步: 用 log-sum-exp 技巧计算 log-softmax（数值稳定）
    # logsumexp(logits, dim=-1) 计算 log(sum_j exp(z_j))，内部做了防溢出处理
    # keepdim=True 保持维度为 (B, 1)，方便和 (B, C) 的 logits 广播
    log_probs = logits - torch.logsumexp(logits, dim=-1, keepdim=True)

    # 第二步: 选出每个样本对应正确类别的 log 概率
    # torch.arange(B) 生成行索引 [0, 1, ..., B-1]
    # targets 是每行的列索引 → 得到 log_probs[i, targets[i]]
    # .mean() 对 batch 维度求平均
    return -log_probs[torch.arange(targets.shape[0]), targets].mean()''',
}