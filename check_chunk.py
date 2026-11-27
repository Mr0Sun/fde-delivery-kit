"""分块结果自检：把 W1D5 的 5 条过关标准写成可执行断言。

用法（在 fde-delivery-kit 仓库根目录跑）：
    uv run python check_chunk.py

先跑一次，此时 chunk() 还是 NotImplementedError，看到红色是正常的。
写完 chunk() 再跑，5 条全过才算过关。
"""
# 让类型注解延迟求值（注解按字符串保存，导入更快，也便于写前向引用）
from __future__ import annotations

# 从自己写的模块里导入被检查的 chunk() 函数
from fde_delivery_kit.chunk import chunk
# 导入 docx 抽取函数，用来拿到原文做比对
from fde_delivery_kit.parse import extract_docx

# 被检查的分块参数：块大小 500 字
SIZE = 500
# 相邻块允许的重叠字数
OVERLAP = 50
# 被测样本文件（相对仓库根目录）
DOCX = "samples/阴阳师超鬼王.docx"
# 允许作为块尾的字符集合：中文句读 + 英文标点 + 换行
BOUNDARY = "。！？；!?;\n"  # 句读与换行：块尾允许落在这里
# 每个块必须携带的 4 个键（缺一个就没法定位，直接判失败）
NEED = {"index", "text", "start", "end"}


# 自检主流程：任何一条失败都返回 1，全过返回 0
def main() -> int:
    # 先把 docx 抽成一整段字符串，后面用它做原文比对
    text = extract_docx(DOCX)
    # 打印原文长度和参数，方便对照结果
    print(f"原文 {len(text)} 字，size={SIZE}，overlap={OVERLAP}\n")

    # 还没实现时 chunk() 会抛 NotImplementedError，这里单独捕获给出提示
    try:
        blocks = chunk(text, SIZE, OVERLAP)
    # 捕获"未实现"异常，说明这是红灯而不是代码写错
    except NotImplementedError:
        # 提示先去实现 chunk()
        print("chunk() 还是 NotImplementedError —— 这是红灯，先去实现它")
        # 返回 1，让 CI / 命令行能看到失败
        return 1

    # 返回空列表说明没切出任何块，直接判失败
    if not blocks:
        # 打印失败原因
        print("[0] 失败：返回了空列表")
        # 提前退出
        return 1

    # 找出缺少必需键的块（用集合包含关系判断）
    lack = [i for i, b in enumerate(blocks) if not NEED <= set(b)]
    # 有缺键就给出位置并退出，后面的检查都没法做
    if lack:
        # 打印缺少的键名和出问题的块位置
        print(f"[0] 失败：这些块缺少必需键 {sorted(NEED)}，位置 {lack}")
        # 返回失败
        return 1

    # 收集未通过的条目编号，最后统一汇报
    fails: list[str] = []
    # 按 start 排序，保证"相邻"是按原文顺序比较，而不是按返回顺序
    blocks = sorted(blocks, key=lambda b: b["start"])

    # 1 长度：每块不超过 size
    over = [b["index"] for b in blocks if len(b["text"]) > SIZE]
    # 打印第 1 条结果：有超长块就列出块号
    print(f"[1] 每块长度 <= {SIZE}：{'通过' if not over else f'失败，超长块 {over}'}")
    # 有超长块就记一条失败
    if over:
        # 记录失败条目
        fails.append("1")

    # 2 原文一致：text[start:end] 必须等于这块自己的 text
    bad2 = [b["index"] for b in blocks if text[b["start"]:b["end"]] != b["text"]]
    # 打印第 2 条结果：切片对不上就列出块号
    print(f"[2] 原文切片与块内容一致：{'通过' if not bad2 else f'失败，块 {bad2}'}")
    # 有对不上的块就记失败
    if bad2:
        # 记录失败条目
        fails.append("2")

    # 3 覆盖：index 从 0 连续、起于 0、止于文末、相邻无空洞
    idx_ok = [b["index"] for b in blocks] == list(range(len(blocks)))
    # 首块必须从 0 开始，末块必须收在原文末尾
    cover_ok = blocks[0]["start"] == 0 and blocks[-1]["end"] == len(text)
    # 找出"后一块起点 > 前一块终点"的位置，那就是漏掉的空洞
    gaps = [
        (blocks[i - 1]["index"], blocks[i]["index"])
        for i in range(1, len(blocks))
        if blocks[i]["start"] > blocks[i - 1]["end"]
    ]
    # 打印 index 是否从 0 连续
    print(f"[3] index 从 0 连续：{'通过' if idx_ok else '失败'}")
    # 打印首尾覆盖情况
    print(f"[3] 首块起于 0、末块止于文末：{'通过' if cover_ok else '失败'}")
    # 打印是否存在空洞，有就给出相邻块号
    print(f"[3] 相邻块无空洞：{'通过' if not gaps else f'失败，空洞位于 {gaps}'}")
    # 三个子条件全过才算第 3 条通过
    if not (idx_ok and cover_ok and not gaps):
        # 记录失败条目
        fails.append("3")

    # 4 重叠：相邻两块的重叠量不得超过 overlap
    over_ov = [
        # 重叠量 = 前一块终点 − 后一块起点，连同块号一起记录
        (blocks[i - 1]["index"], blocks[i - 1]["end"] - blocks[i]["start"])
        for i in range(1, len(blocks))
        # 只保留重叠超过上限的
        if blocks[i - 1]["end"] - blocks[i]["start"] > OVERLAP
    ]
    # 打印第 4 条结果：超限就列出块号和实际重叠量
    print(f"[4] 相邻重叠 <= {OVERLAP}：{'通过' if not over_ov else f'失败，{over_ov}'}")
    # 有超限就记失败
    if over_ov:
        # 记录失败条目
        fails.append("4")

    # 5 边界：非硬切块的块尾必须落在句读/换行上
    soft = [
        # 收集"不是硬切"且"块尾字符不在允许集合里"的块号
        b["index"]
        # 最后一块不收尾要求，因为它可能正好收在文末的半句上
        for b in blocks[:-1]
        # split=True 是块内硬切，本来就允许断在任何位置，不参与本条
        if not b.get("split") and b["text"][-1] not in BOUNDARY
    ]
    # 打印达标比例：总块数 −1（最后一块）− 未达标数
    print(
        f"[5] 块尾落在句读/换行：{len(blocks) - 1 - len(soft)}/{len(blocks) - 1} 达标"
        # 有未达标块时追加块号
        + ("" if not soft else f"，未达标块 {soft}")
    )
    # 有未达标块就记失败
    if soft:
        # 记录失败条目
        fails.append("5")

    # 统计所有块的字符总数，用来算膨胀率
    total = sum(len(b["text"]) for b in blocks)
    # 打印块数、总字符、膨胀率（相对原文多出来的比例）
    print(f"\n块数 {len(blocks)}，总字符 {total}，膨胀率 {(total / len(text) - 1) * 100:.1f}%")
    # 汇总结论：全过或列出未通过的条目编号
    print("结论：" + ("5 条全过" if not fails else f"未通过第 {fails} 条"))
    # 全部通过返回 0，否则返回 1 作为进程退出码
    return 0 if not fails else 1


# 直接运行本文件时执行自检（被 import 时不执行）
if __name__ == "__main__":
    # 把 main() 的返回值当作进程退出码
    raise SystemExit(main())
