def format_self_contained_item_pretty(
    item,
    *,
    line_width_chars: int,
    space_padding: int,
    max_output_len: int | None = None,
    trunc_str: str = "...(TRUNC.)",
    indent: int = 0,
    debug: bool = False,
) -> str:
    """
    Pretty-format `item` inside a self-contained box with wrapping, padding,
    and optional truncation.

    Args:
        item: str or object convertible to str.
        line_width_chars: total width including borders.
        space_padding: left/right spaces inside the borders.
        max_output_len: if not None, maximum characters (with trunc marker).
        trunc_str: marker appended when truncation occurs.
        indent: left indent before the left border (non-negative).
        debug: if True, prints detailed debug info.

    Returns:
        Formatted string with box borders.
    """
    if indent < 0:
        raise ValueError("indent must be non-negative")

    s_full = str(item)

    # --- normalize newlines so \r\n and \r become \n ---
    s_full = s_full.replace("\r\n", "\n").replace("\r", "\n")

    # --- truncation ---
    if max_output_len is not None and len(s_full) > max_output_len:
        keep_len = max_output_len - len(trunc_str)
        if keep_len < 0:
            keep_len = 0
        s_kept = s_full[:keep_len] + trunc_str
    else:
        s_kept = s_full

    # --- geometry ---
    content_width = line_width_chars - 2 - space_padding * 2
    if content_width <= 0:
        raise ValueError("line_width_chars too small for padding")

    paras = s_kept.split("\n")

    # --- wrap paragraphs ---
    wrapped_lines: list[str] = []
    for para in paras:
        if para == "":
            wrapped_lines.append("")  # blank line
            continue
        start = 0
        while start < len(para):
            wrapped_lines.append(para[start:start+content_width])
            start += content_width

    # --- render ---
    lines = []
    border = "+" + "-" * (line_width_chars - 2) + "+"
    lines.append(" " * indent + border)
    for seg in wrapped_lines:
        line = "|" + " " * space_padding
        line += seg.ljust(content_width)
        line += " " * space_padding + "|"
        lines.append(" " * indent + line)
    lines.append(" " * indent + border)

    return "\n".join(lines)


def format_title(
        title_str,
        divider_char='#',
        side_char='|',
        line_width=29,
        n_topbottom_dividers=2,
        indent=0
):
    """
    Centers `title_str` within a single boxed line bounded by `side_char`, with
    `n_topbottom_dividers` full-width divider lines above and below using `divider_char`.
    Returns a single string with newlines. Respects `indent` by prepending spaces to every line.
    """
    if not isinstance(divider_char, str) or len(divider_char) != 1:
        raise ValueError("divider_char must be a single character.")
    if not isinstance(side_char, str) or len(side_char) != 1:
        raise ValueError("side_char must be a single character.")
    if not isinstance(line_width, int) or line_width <= 2:
        raise ValueError("line_width must be an int > 2.")
    if not isinstance(n_topbottom_dividers, int) or n_topbottom_dividers < 0:
        raise ValueError("n_topbottom_dividers must be a non-negative int.")
    if not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative int.")

    indent_str = " " * indent
    divider_line = divider_char * line_width
    divider_block = ((indent_str + divider_line) + "\n") * n_topbottom_dividers

    title_len = len(title_str)
    linespace_for_padding = line_width - 2 - title_len
    if linespace_for_padding < 0:
        # If too long, we print as-is without clipping (caller controls width)
        # but never break the box structure; we let it overflow naturally.
        linespace_for_padding = 0
    left_pad = linespace_for_padding // 2
    extra_pad = linespace_for_padding % 2
    side_pad = " " * left_pad

    title_line = f"{side_char}{side_pad}{title_str}{side_pad}{' ' * extra_pad}{side_char}"
    title_line = indent_str + title_line + "\n"

    return divider_block + title_line + divider_block
