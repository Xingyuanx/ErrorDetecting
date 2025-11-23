--[[
  RawBlock(el)
  将 Markdown 文档中的 HTML <table> 片段解析为 AST 并注入到文档块中，
  后续由 Table(el) 针对列内容自动设置对齐。
]]
function RawBlock(el)
  local fmt = el.format or ""
  if string.find(fmt, "html", 1, true) then
    local s = el.text or ""
    local sl = string.lower(s)
    if string.match(sl, "^%s*<table") then
      local doc = pandoc.read(s, "html")
      return doc.blocks
    end
  end
end

--[[
  Table(el)
  自动设置表格列对齐：
  - 数值型列（≥60% 单元格为数字/小数/百分比）右对齐；
  - 其他列左对齐。
  说明：对齐通过修改 el.colspecs[i].align 完成，最终由 Pandoc 写出为 GFM 的 :---/---: 等标记。
]]
function Table(el)
  local function cell_text(cell)
    return pandoc.utils.stringify(cell)
  end
  local function is_numeric(s)
    s = (s or ""):gsub("%s+", "")
    if s == "" then return false end
    if s:match("^[+-]?%d+[%.,]?%d*%%?$") then return true end
    return false
  end
  local texts_by_col = {}
  local function collect_row(row)
    for i, cell in ipairs(row.cells or {}) do
      local t = cell_text(cell)
      texts_by_col[i] = texts_by_col[i] or {}
      table.insert(texts_by_col[i], t)
    end
  end
  for _, row in ipairs((el.head and el.head.rows) or {}) do collect_row(row) end
  for _, body in ipairs(el.bodies or {}) do
    for _, row in ipairs(body.rows or {}) do collect_row(row) end
  end
  for _, row in ipairs((el.foot and el.foot.rows) or {}) do collect_row(row) end

  for i, cs in ipairs(el.colspecs or {}) do
    local cells = texts_by_col[i] or {}
    local total, numeric = 0, 0
    for _, v in ipairs(cells) do
      total = total + 1
      if is_numeric(v) then numeric = numeric + 1 end
    end
    if total > 0 and (numeric / total) >= 0.6 then
      cs.align = pandoc.AlignRight
    else
      cs.align = pandoc.AlignLeft
    end
  end
  return el
end