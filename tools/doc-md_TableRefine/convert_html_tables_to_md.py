import os
import re
import html
import argparse
import subprocess

def html_to_text(s):
    """
    将 HTML 片段转为纯文本：删除标签、反转义实体、压缩空白。
    """
    s = re.sub(r"<[^>]+>", " ", s, flags=re.S)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def convert_table(table_html):
    """
    将一个 HTML <table> 转换为 Markdown 管道表格。
    仅处理 <tr> 与 <td>/<th>，复杂嵌套将被拍平为文本。
    """
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.I | re.S)
    parsed_rows = []
    for r in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, flags=re.I | re.S)
        parsed_rows.append([html_to_text(c) for c in cells])
    if not parsed_rows:
        return table_html
    widths = [max(len(row[i]) if i < len(row) else 0 for row in parsed_rows) for i in range(max(len(r) for r in parsed_rows))]
    def mk_row(vals):
        padded = [ (vals[i] if i < len(vals) else "").strip() for i in range(len(widths)) ]
        return "| " + " | ".join(padded) + " |"
    header = parsed_rows[0]
    # 自动对齐：数值型列右对齐，其他列左对齐；少数关键词列居中
    def is_numeric(s):
        s = re.sub(r"\s+", "", s or "")
        return bool(re.match(r"^[+-]?\d+(?:[\.,]\d+)?%?$", s))
    def decide_align(col_idx):
        head = header[col_idx] if col_idx < len(header) else ""
        if re.search(r"^(id|编号)$", head, flags=re.I):
            return ":---:"
        if re.search(r"(日期|时间|版本)", head, flags=re.I):
            return ":---:"
        col_vals = [row[col_idx] for row in parsed_rows[1:] if col_idx < len(row)]
        total = len(col_vals)
        numeric = sum(1 for v in col_vals if is_numeric(v))
        if total and numeric / total >= 0.6:
            return "---:"
        return ":---"
    sep = "| " + " | ".join([decide_align(i) for i in range(len(widths))]) + " |"
    body = parsed_rows[1:]
    out = [mk_row(header), sep]
    for br in body:
        out.append(mk_row(br))
    return "\n".join(out)

def process_file(path):
    """
    处理单个 Markdown 文件：将其中所有 HTML <table> 替换为 Markdown 表格。
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    def repl(m):
        return convert_table(m.group(0))
    new_content = re.sub(r"<table[^>]*>.*?</table>", repl, content, flags=re.I | re.S)
    new_content = refine_pipe_tables(new_content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

def run_pandoc_docx_to_md(docx_path, md_path, media_dir, lua_filter_path=None):
    """
    使用 Pandoc 将 docx 转为 GFM Markdown，并提取图片到指定 media 目录；
    可选附加 Lua 过滤器以增强表格处理。
    """
    os.makedirs(media_dir, exist_ok=True)
    cmd = [
        'pandoc', docx_path,
        '-f', 'docx', '-t', 'gfm',
        '-o', md_path,
        f'--extract-media={media_dir}'
    ]
    if lua_filter_path:
        cmd.extend(['--lua-filter', lua_filter_path])
    subprocess.run(cmd, check=True)

def split_cells(line):
    parts = [p.strip() for p in line.strip().strip('|').split('|')]
    return parts

def refine_pipe_tables(content):
    """
    检测并重写 Markdown 管道表格的分隔行，根据列内容自动设置对齐。
    """
    lines = content.splitlines()
    i = 0
    out = []
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|'):
            # 收集连续的表格行
            start = i
            block = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                block.append(lines[i])
                i += 1
            if len(block) >= 2:
                header = split_cells(block[0])
                # 统计列对齐
                def is_numeric(s):
                    s = re.sub(r"\s+", "", s or "")
                    return bool(re.match(r"^[+-]?\d+(?:[\.,]\d+)?%?$", s))
                def decide_align(col_idx):
                    head = header[col_idx] if col_idx < len(header) else ""
                    if re.search(r"^(id|编号)$", head, flags=re.I):
                        return ":---:"
                    if re.search(r"(日期|时间|版本)", head, flags=re.I):
                        return ":---:"
                    # 收集该列的正文值
                    col_vals = []
                    for r in block[2:]:  # 跳过原分隔行
                        cells = split_cells(r)
                        if col_idx < len(cells):
                            col_vals.append(cells[col_idx])
                    total = len(col_vals)
                    numeric = sum(1 for v in col_vals if is_numeric(v))
                    if total and numeric / total >= 0.6:
                        return "---:"
                    return ":---"
                aligns = [decide_align(ci) for ci in range(len(header))]
                sep = "| " + " | ".join(aligns) + " |"
                # 重写块：保留 header，替换 sep，其余行原样
                new_block = [block[0], sep] + block[2:]
                out.extend(new_block)
            else:
                out.extend(block)
        else:
            out.append(line)
            i += 1
    return "\n".join(out)

def iter_target_files(root: str, include_ext=(".md",)):
    if os.path.isfile(root):
        if os.path.splitext(root)[1].lower() in include_ext:
            yield root
        return
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in include_ext:
                yield os.path.join(dirpath, fn)

def main():
    """
    按用户指定文件列表进行转换：
    - 支持 .docx：同名输出 .md，图片提取到相邻 media 目录；
    - 支持 .md：进行 HTML 表格转换与管道表格对齐优化；
    - 支持一次传入多个文件路径；不进行递归查找。
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True, help='待处理文件路径列表（支持 .docx 与 .md）')
    ap.add_argument('--media', default='media', help='docx 转换时图片提取目录名（相对输出目录）')
    args = ap.parse_args()

    # 计算 Lua 过滤器绝对路径（用于 Pandoc）
    lua_filter = os.path.join(os.path.dirname(__file__), 'html_table_to_md.lua')
    if not os.path.isfile(lua_filter):
        lua_filter = None

    for user_path in args.files:
        path = os.path.normpath(user_path)
        ext = os.path.splitext(path)[1].lower()
        if ext == '.docx':
            out_md = os.path.join(os.path.dirname(path), os.path.splitext(os.path.basename(path))[0] + '.md')
            media_dir = os.path.join(os.path.dirname(out_md), args.media)
            run_pandoc_docx_to_md(path, out_md, media_dir, lua_filter_path=lua_filter)
            process_file(out_md)
        elif ext == '.md':
            process_file(path)
        else:
            # 非支持类型，忽略
            continue

if __name__ == "__main__":
    main()