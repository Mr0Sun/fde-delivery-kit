# 让类型注解延迟求值（注解以字符串形式保存，兼容更多写法，也让导入更快）
from __future__ import annotations

# 标准库：用于读取命令行参数
import sys
# 标准库：跨平台地处理文件路径
from pathlib import Path

# 第三方库：PyMuPDF，用来读取 PDF（安装名 pymupdf）
import pymupdf
# 第三方库：python-docx，用来读取 Word 文档（安装名 python-docx，导入名 docx）
from docx import Document


# 从 PDF 文件中提取全部纯文本
def extract_pdf(path: str | Path) -> str:
    # 打开 PDF 文件，返回一个文档对象
    doc = pymupdf.open(path)
    # 准备一个空列表，按页保存提取出来的文字
    parts: list[str] = []
    # 遍历每一页，把每页文字都装进parts
    for page in doc:
        # get_text() 取出当前页的文字（不含图片内容），追加到列表
        parts.append(page.get_text())
    # 关闭文档，释放文件句柄
    doc.close()
    # 用换行符把所有页的文字拼成一个字符串返回
    return "\n".join(parts)


# 从 .docx 文件中提取全部段落文本
def extract_docx(path: str | Path) -> str:
    # 打开 Word 文档，返回 Document 对象
    doc = Document(path)
    # 准备列表，按段落保存文字
    parts: list[str] = []
    # 遍历每个段落，把段落文字都装进parts
    for para in doc.paragraphs:
        # para.text 取得该段落的纯文本
        parts.append(para.text)
    # 用换行拼接所有段落返回
    return "\n".join(parts)


# 程序入口：argv 是命令行参数列表，argv[0] 是脚本名，argv[1] 是文件路径
def main(argv: list[str]) -> int:
    # 参数个数不是 2（只给了脚本名、没给文件路径）时，打印用法
    if len(argv) != 2:
        # 提示用户正确用法
        print("用法：python -m fde_delivery_kit.parse <文件路径>")
        # 返回非 0 值，表示命令执行失败
        return 1

    # 取出用户传入的路径并转成 Path 对象
    path = Path(argv[1])
    # 取小写后缀名，例如 ".pdf"
    suffix = path.suffix.lower()
    # 这里按.pdf / .docx分发，其他后缀报错退出
    if suffix not in [".pdf", ".docx"]:
        # 告诉用户不支持该文件类型
        print(f"不支持的文件类型：{suffix}")
        # 同样返回 1 表示失败
        return 1

    # 是 PDF 就调用 extract_pdf
    if suffix == ".pdf":
        text = extract_pdf(path)
    # 是 Word 就调用 extract_docx
    elif suffix == ".docx":
        text = extract_docx(path)
    # 理论上走不到这里（上面已拦截非法后缀），仅作兜底
    else:
        raise ValueError(f"不支持的文件类型：{suffix}")
    # 打印提取出来的全部文本
    print(text)
    # 返回 0 表示成功
    return 0


# 只有"直接运行本文件"时才执行下面这行；被其他模块 import 时不执行
if __name__ == "__main__":
    # 把 main 的返回值作为进程退出码交给系统
    raise SystemExit(main(sys.argv))
