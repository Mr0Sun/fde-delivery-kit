from __future__ import annotations

import sys
from bisect import bisect_right
from pathlib import Path

from .parse import extract_docx, extract_pdf

BOUNDARY = "。！？；!?;\n"


def chunk(text: str, size: int = 500, overlap: int = 50) -> list[dict]:
    """把整篇文本切成带 index 的块列表。

    返回：[{"index": 0, "text": "...", "start": 0, "end": 500}, ...]
    start / end 是这一块在原文里的起止下标，text[start:end] 必须等于这块的 text。

    切法：优先以「行尾」（含换行符）为切点装箱，保证块尾落在句读/换行上；
    单行本身超过 size 时才在行内硬切，这类块带 split=True。
    """
    if size <= 0:
        raise ValueError("size 必须大于 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap 必须满足 0 <= overlap < size")

    n = len(text)
    if n == 0:
        return []

    # 所有可用切点：每行行尾（含 \n），最后一行的行尾是文末
    unit_ends: list[int] = []
    i = 0
    while i < n:
        j = text.find("\n", i)
        if j == -1:
            unit_ends.append(n)
            break
        unit_ends.append(j + 1)
        i = j + 1

    blocks: list[dict] = []
    pos = 0
    while pos < n:
        # 找出「能装进 size」的最远行尾；没有就说明当前行太长，只能硬切
        first = bisect_right(unit_ends, pos)
        j = bisect_right(unit_ends, pos + size) - 1
        if j >= first:
            end = unit_ends[j]
            split = False
        else:
            end = _retreat(text, pos, min(pos + size, n), overlap)
            split = True

        block = {"index": len(blocks), "text": text[pos:end], "start": pos, "end": end}
        if split:
            block["split"] = True
        blocks.append(block)

        if end >= n:  # 已经盖到文末，不用再滑
            break

        # 下一块从 end 往回 overlap 开始：重叠不超过 overlap，且不会留空洞
        pos = max(end - overlap, pos + 1)

    return blocks


def _retreat(text: str, start: int, end: int, overlap: int) -> int:
    """把硬切点向左回退到句读上，回退量不超过 overlap；找不到就原样返回。"""
    floor = max(start + 1, end - overlap)
    for k in range(end - 1, floor - 1, -1):
        if text[k] in BOUNDARY:
            return k + 1
    return end


def main(argv: list[str]) -> int:
    """用法：uv run python -m fde_delivery_kit.chunk <文件路径> [size] [overlap]"""
    # 1) 参数不够就打印用法、return 1（照 parse.py 的 main 写）
    # 2) 按后缀选 extract_pdf / extract_docx，抽不出就 return 1
    # 3) 调 chunk()，每块按 "--- #{index} [{start}:{end}] ---" 分块打印
    raise NotImplementedError("main() 还没写")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
