# Sentinel to distinguish "no value provided" from item=None
_MISSING = object()

def format_self_contained_item_pretty(
        item=_MISSING,   # sentinel so None can be a printable value
        line_width_chars=100,
        max_output_len_chars=None,
        space_padding=5,
        startline_format_char='|',
        endline_format_char='|',
        truncation_str='...(TRUNC.)',
        start_and_end_divider_Char='-',  # adds a top and bottom divider to visually separate the value
        indent=0  # NEW: number of spaces to prepend to each line
):
    """
    Takes input item and turns it into a str wrapped into lines with left and right boundary characters, space padding, and dividers at the start and end to visually self-encapsulate the item within the string 
    (e.g. for printing values that must appear to be self-contained for easy visual parsing).
    
    New behavior:
    - Adds a full line of `block_boundary_char` repeated to line_width_chars at the start and end.
    - Indent param adds spaces to the beginning of every line.
    """
    # --- check inputs ---
    if item is _MISSING:
        raise ValueError("input item is required (None is allowed).")
    if callable(item):
        raise ValueError("Invalid type passed to formatter: callables not allowed.")
    if not isinstance(truncation_str, str):
        raise ValueError("truncation_str must be a str.")
    if not isinstance(line_width_chars, int) or line_width_chars <= 0:
        raise ValueError("line_width_chars must be a positive int.")
    if not isinstance(space_padding, int) or space_padding < 0:
        raise ValueError("space_padding must be a non-negative int.")
    if not isinstance(startline_format_char, str) or len(startline_format_char) != 1:
        raise ValueError("startline_format_char must be a single character string.")
    if not isinstance(endline_format_char, str) or len(endline_format_char) != 1:
        raise ValueError("endline_format_char must be a single character string.")
    if not isinstance(start_and_end_divider_Char, str) or len(start_and_end_divider_Char) != 1:
        raise ValueError("block_boundary_char must be a single character string.")
    if not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative int.")

    # --- Compute chars available from the line width for the actual value ---
    # 2 boundary chars + 2*space_padding take up space in the lines
    content_width = line_width_chars - 2 - (2 * space_padding)
    if content_width <= 0:
        raise ValueError(
            "Not enough width for content; increase `line_width_chars` or reduce `space_padding`."
        )

    # --- Apply truncation if indicated ---
    full = str(item)

    if max_output_len_chars is not None:
        if max_output_len_chars < 0:
            raise ValueError("`max_output_len_chars` must be non-negative if provided.")
        if len(full) > max_output_len_chars:
            if max_output_len_chars >= len(truncation_str):
                keep = max_output_len_chars - len(truncation_str)
            else:
                keep = 0

            # Avoid splitting the marker across lines
            if keep > 0:
                remainder = keep % content_width
                if remainder != 0 and (remainder + len(truncation_str) > content_width):
                    keep -= remainder

            item_str = full[:max(keep, 0)] + truncation_str
        else:
            item_str = full
    else:
        item_str = full

    # --- Split into fixed-width segments ---
    segments = [
        item_str[i: i + content_width]
        for i in range(0, len(item_str), content_width)
    ] or [""]  # ensure at least one line if item_str is empty

    # --- Build formatted lines with exact width ---
    lines = []
    for seg in segments:
        line = (
            f"{startline_format_char}"
            f"{' ' * space_padding}"
            f"{seg.ljust(content_width)}"
            f"{' ' * space_padding}"
            f"{endline_format_char}"
        )
        if len(line) != line_width_chars:
            if len(line) > line_width_chars:
                line = line[:line_width_chars]
            else:
                line = line + (" " * (line_width_chars - len(line)))
        lines.append(line)

    # --- Add top and bottom boundary lines ---
    boundary_line = start_and_end_divider_Char * line_width_chars

    # --- Apply indent to every line ---
    indent_str = " " * indent
    lines_with_indent = [indent_str + l for l in [boundary_line] + lines + [boundary_line]]

    return "\n".join(lines_with_indent)


def format_title(
        title_str,
        divider_char='#',
        side_char='|',
        line_width=29,
        n_topbottom_dividers=2,
):
    divider_line = divider_char * line_width + '\n'
    divider_lines = divider_line * n_topbottom_dividers

    title_len = len(title_str)
    linespace_for_padding = line_width - 2 - title_len
    len_title_side_pad = linespace_for_padding // 2
    extra_pad = linespace_for_padding % 2

    title_side_pad = ' ' * len_title_side_pad
    # Add extra space if needed
    title_line = f"{side_char}{title_side_pad}{title_str}{title_side_pad}{' ' * extra_pad}{side_char}\n"

    return (divider_lines + title_line + divider_lines)[:-1] # get rid of last newline from adding second divider str
