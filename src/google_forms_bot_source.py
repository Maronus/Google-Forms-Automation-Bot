#!/usr/bin/env python3
"""
maronus v1.0 — google forms automation
"""

# ─── Bootstrap: auto-install missing packages ─────────────────────────
import subprocess as _sp, sys as _sys


def _ensure(module_name, package_name=None):
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
    except ImportError:
        print(f"  Installing {package_name}...")
        cmds = [
            [_sys.executable, "-m", "pip", "install", "-q", package_name, "--break-system-packages"],
            [_sys.executable, "-m", "pip", "install", "-q", package_name],
            [_sys.executable, "-m", "pip", "install", "--user", "-q", package_name, "--break-system-packages"],
            [_sys.executable, "-m", "pip", "install", "--user", "-q", package_name],
        ]
        for cmd in cmds:
            try:
                _sp.check_call(cmd, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
                return
            except Exception:
                pass


_ensure("requests")
_ensure("rich")

# ─── Imports ──────────────────────────────────────────────────────────
import os
import io
import sys
import re
import json
import time
import random
import threading

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

import requests
from rich.console import Console
from rich.text import Text
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
)
from rich.table import Table
from rich.columns import Columns
from rich.align import Align

console = Console(force_terminal=True)
VERSION = "1.0.0"

# ─── Raw Keyboard Input ──────────────────────────────────────────────

def _getch():
    """Read a single keypress cross-platform (handles arrow keys)."""
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'up'
            if ch2 == b'P': return 'down'
            return None
        if ch == b'\r': return 'enter'
        if ch == b'\x08': return 'backspace'
        if ch == b'\x03': sys.exit(0)
        try:
            return ch.decode('utf-8')
        except:
            return None
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
            if ch == '\r': return 'enter'
            if ch == '\x7f' or ch == '\x08': return 'backspace'
            if ch == '\x03': sys.exit(0)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ─── Arabic / RTL Support ────────────────────────────────────────────


def _has_arabic(text):
    return any("\u0600" <= ch <= "\u06FF" for ch in str(text))


def _r(text):
    """Reshape Arabic/RTL text for correct terminal display."""
    if not text or not _has_arabic(text):
        return str(text)
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:
        _ensure("arabic_reshaper")
        _ensure("bidi", "python-bidi")
        import arabic_reshaper
        from bidi.algorithm import get_display
    reshaped = arabic_reshaper.reshape(str(text))
    bidi = get_display(reshaped)
    return "\u200f" + bidi


# ─── Theme ────────────────────────────────────────────────────────────

BLUE = "#3b82f6"
DARK_BLUE = "#1d4ed8"
GREEN = "#22c55e"
RED = "#ef4444"
AMBER = "#f59e0b"
DIM = "#666666"


# ─── Pixel Font & Banner ─────────────────────────────────────────────

FONT = {
    "m": [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
    ],
    "a": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
    ],
    "r": [
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 0, 0, 1],
    ],
    "o": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    "n": [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
    ],
    "u": [
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    "s": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
}


def _render_pixel_text(text, spacing=1):
    rows = ["", "", ""]
    for ci, ch in enumerate(text):
        bmp = FONT.get(ch)
        if not bmp:
            for rr in range(3):
                rows[rr] += "   "
            continue
        w = len(bmp[0])
        for x in range(w):
            t, b = bmp[0][x], bmp[1][x]
            rows[0] += "\u2588" if t and b else "\u2580" if t else "\u2584" if b else " "
        for x in range(w):
            t, b = bmp[2][x], bmp[3][x]
            rows[1] += "\u2588" if t and b else "\u2580" if t else "\u2584" if b else " "
        for x in range(w):
            rows[2] += "\u2580" if bmp[4][x] else " "
        if ci < len(text) - 1:
            for rr in range(3):
                rows[rr] += " " * spacing
    return rows


def display_banner():
    rows_main = _render_pixel_text("maro", spacing=1)
    rows_tail = _render_pixel_text("nus", spacing=1)
    console.print()
    for i in range(3):
        t = Text("    ")
        for ch in rows_main[i]:
            t.append(ch, style="bold white" if ch.strip() else "")
        t.append(" ")
        for ch in rows_tail[i]:
            t.append(ch, style="#888888" if ch.strip() else "")
        console.print(t)
    sub = Text("    ")
    sub.append("google forms automation", style="dim")
    sub.append("  @maronus", style=f"dim {BLUE}")
    console.print(sub)
    console.print()


# ─── UI Helpers ──────────────────────────────────────────────────────


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def ask(prompt, default=None):
    t = Text()
    t.append("  > ", style=f"bold {BLUE}")
    t.append(prompt, style="bold white")
    if default is not None:
        t.append(f" ({default})", style="dim")
    t.append(": ", style="dim")
    console.print(t, end="")
    try:
        val = input("").strip()
    except EOFError:
        val = ""
    return val if val else (str(default) if default is not None else "")


def ask_int(prompt, default=None, min_val=1, max_val=None):
    while True:
        val = ask(prompt, default)
        try:
            n = int(val)
            if n < min_val:
                msg(f"Must be at least {min_val}", "err")
                continue
            if max_val is not None and n > max_val:
                msg(f"Must be at most {max_val}", "err")
                continue
            return n
        except ValueError:
            msg("Enter a valid number", "warn")


def ask_float(prompt, default=None, min_val=0.0):
    while True:
        val = ask(prompt, default)
        try:
            f = float(val)
            if f < min_val:
                msg(f"Must be at least {min_val}", "err")
                continue
            return f
        except ValueError:
            msg("Enter a valid number", "warn")


def ask_yn(prompt, default=True):
    suffix = "Y/n" if default else "y/N"
    while True:
        val = ask(f"{prompt} [{suffix}]")
        if not val:
            return default
        low = val.lower().strip()
        if low in ("y", "yes"):
            return True
        if low in ("n", "no"):
            return False
        msg("Please type 'y' or 'n'", "warn")


def ask_choice(prompt, choices, default=None):
    labels = " / ".join(f"[{c[0].upper()}]{c[1:]}" for c in choices)
    valid = [c[0].upper() for c in choices]
    while True:
        val = ask(f"{prompt} {labels}", default)
        if val and val.strip().upper()[0] in valid:
            return val.strip().upper()[0]
        msg(f"Please type one of: {', '.join(valid)}", "warn")


def msg(text, kind="info"):
    icons = {"ok": ">", "err": "x", "warn": "!", "info": "-"}
    colors = {"ok": GREEN, "err": RED, "warn": AMBER, "info": DIM}
    t = Text()
    t.append(f"  {icons.get(kind, '-')} ", style=f"bold {colors.get(kind, DIM)}")
    t.append(str(text), style="white" if kind != "err" else RED)
    console.print(t)


def section(title):
    console.print()
    t = Text()
    t.append(f"  --- {title} ", style=f"bold {BLUE}")
    t.append("-" * max(40 - len(title), 5), style=f"dim {DARK_BLUE}")
    console.print(t)
    console.print()


def spinner_run(message, func, *args, **kwargs):
    result = [None]
    error = [None]

    def _target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            error[0] = e

    th = threading.Thread(target=_target, daemon=True)
    th.start()
    chars = "|/-\\"
    i = 0
    while th.is_alive():
        t = Text()
        t.append(f"  {chars[i % len(chars)]} ", style=f"bold {BLUE}")
        t.append(message, style="dim")
        console.print(t, end="\r")
        time.sleep(0.1)
        i += 1
        th.join(0.01)
    console.print(" " * 60, end="\r")
    if error[0]:
        raise error[0]
    return result[0]


# ─── Google Forms Parser ─────────────────────────────────────────────

FORM_URL_RE = [
    re.compile(r"https?://docs\.google\.com/forms/d/e/([A-Za-z0-9_-]+)"),
    re.compile(r"https?://docs\.google\.com/forms/d/([A-Za-z0-9_-]+)"),
]

Q_TYPES = {
    0: "short_answer",
    1: "paragraph",
    2: "multiple_choice",
    3: "dropdown",
    4: "checkboxes",
    5: "linear_scale",
    7: "grid",
    9: "date",
    10: "time",
}

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _resolve_url(url):
    url = url.strip()
    is_known = any(p.search(url) for p in FORM_URL_RE)
    if not is_known:
        try:
            r = requests.head(url, allow_redirects=True, timeout=15, headers=HTTP_HEADERS)
            return r.url
        except Exception:
            try:
                r = requests.get(url, allow_redirects=True, timeout=15, headers=HTTP_HEADERS)
                return r.url
            except Exception:
                pass
    return url


def _extract_form_id(url):
    url = url.strip()
    m = FORM_URL_RE[0].search(url)
    if m:
        return m.group(1), True
    m = FORM_URL_RE[1].search(url)
    if m:
        return m.group(1), False
    return None, False


def _normalize_url(url):
    fid, pub = _extract_form_id(url)
    if not fid:
        raise ValueError("Invalid Google Form URL")
    prefix = "https://docs.google.com/forms/d" + ("/e/" if pub else "/") + fid
    return prefix + "/viewform", prefix + "/formResponse"


def _parse_question(item):
    try:
        tid = item[3]
        q = {
            "id": item[0],
            "title": item[1] or "(untitled)",
            "description": item[2] or "",
            "type": Q_TYPES.get(tid, f"unknown_{tid}"),
            "type_id": tid,
            "required": False,
            "entry_ids": [],
            "options": [],
        }
        if item[4]:
            for sub in item[4]:
                if sub is None:
                    continue
                q["entry_ids"].append(sub[0])
                if len(sub) > 2 and sub[2]:
                    q["required"] = True
                if len(sub) > 1 and sub[1]:
                    for opt in sub[1]:
                        if opt and len(opt) > 0 and opt[0] is not None:
                            q["options"].append(str(opt[0]))
                if tid == 5 and len(sub) > 3 and sub[3]:
                    labels = sub[3]
                    q["scale_labels"] = {
                        "low": labels[0] if labels[0] else "",
                        "high": labels[1] if len(labels) > 1 and labels[1] else "",
                    }
        return q
    except (IndexError, TypeError):
        return None


def parse_form(url):
    url = _resolve_url(url)
    view_url, submit_url = _normalize_url(url)

    resp = requests.get(view_url, headers=HTTP_HEADERS, timeout=30)
    resp.raise_for_status()

    m = re.search(
        r"var\s+FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>",
        resp.text,
        re.DOTALL,
    )
    if not m:
        raise ValueError("Could not extract form data. Make sure the form is public.")

    data = json.loads(m.group(1).strip())

    title = ""
    try:
        title = data[1][8] or ""
    except (IndexError, TypeError):
        pass
    if not title:
        try:
            title = data[3] or ""
        except (IndexError, TypeError):
            title = "Untitled Form"

    desc = ""
    try:
        desc = data[1][0] or ""
    except (IndexError, TypeError):
        pass

    questions = []
    try:
        items = data[1][1]
        if items:
            for item in items:
                q = _parse_question(item)
                if q and q["entry_ids"]:
                    questions.append(q)
    except (IndexError, TypeError):
        pass

    if not questions:
        raise ValueError("No questions found. The form may be empty or restricted.")

    return {
        "title": title,
        "description": desc,
        "submit_url": submit_url,
        "questions": questions,
    }


# ─── Distribution Helpers ────────────────────────────────────────────


def _get_options_for_q(q):
    if q["type"] in ("multiple_choice", "dropdown", "checkboxes"):
        return list(q["options"])
    if q["type"] == "linear_scale":
        return list(q["options"]) if q["options"] else [str(i) for i in range(1, 6)]
    return []


def _show_options(options):
    for i, opt in enumerate(options, 1):
        console.print(Text(f"      [{i}] {_r(opt)}", style="white"))
    console.print()


def _manual_split(options, total):
    dist = {}
    remaining = total
    available_options = list(options)
    
    while remaining > 0 and available_options:
        if len(available_options) == 1:
            opt = available_options[0]
            dist[opt] = remaining
            t = Text()
            t.append("  > ", style=f"bold {BLUE}")
            t.append(f"{_r(opt)} : {remaining} (remainder)", style="white")
            console.print(t)
            break

        selected_idx = 0
        typing_mode = False
        typed_text = ""
        lines_drawn = 0

        while True:
            out = Text()
            out.append(f"\n  Select an answer to distribute ({remaining} users remaining):\n", style=f"bold {BLUE}")
            for i, opt in enumerate(available_options):
                if i == selected_idx:
                    if typing_mode:
                        out.append(f"  > {_r(opt)}  -- how many? {typed_text}_\n", style=f"bold {GREEN}")
                    else:
                        out.append(f"  > {_r(opt)}\n", style=f"bold {GREEN}")
                else:
                    out.append(f"    {_r(opt)}\n", style="white")

            if lines_drawn > 0:
                sys.stdout.write(f"\033[{lines_drawn}A\r\033[J")
                sys.stdout.flush()

            lines_drawn = out.plain.count("\n")
            console.print(out, end="")

            key = _getch()
            if not key:
                continue

            if not typing_mode:
                if key == 'up':
                    selected_idx = max(0, selected_idx - 1)
                elif key == 'down':
                    selected_idx = min(len(available_options) - 1, selected_idx + 1)
                elif key == 'enter':
                    typing_mode = True
                    typed_text = ""
            else:
                if key == 'enter':
                    if typed_text.lower() == 'all':
                        count = remaining
                    else:
                        try:
                            count = int(typed_text)
                        except ValueError:
                            count = -1

                    if 0 <= count <= remaining:
                        opt = available_options[selected_idx]
                        dist[opt] = count
                        remaining -= count

                        sys.stdout.write(f"\033[{lines_drawn}A\r\033[J")
                        sys.stdout.flush()

                        t = Text()
                        t.append("  > ", style=f"bold {BLUE}")
                        t.append(f"{_r(opt)} : {count}", style="white")
                        console.print(t)
                        available_options.pop(selected_idx)
                        if selected_idx >= len(available_options) and available_options:
                            selected_idx = len(available_options) - 1
                        break
                    else:
                        typed_text = ""
                elif key == 'backspace':
                    typed_text = typed_text[:-1]
                elif len(key) == 1 and key.isprintable():
                    typed_text += key

    for opt in options:
        if opt not in dist:
            dist[opt] = 0

    return dist

# ─── Live Table Rendering ─────────────────────────────────────────────


def _trunc(text, maxlen=18):
    """Truncate text and add ... if it exceeds maxlen."""
    s = str(text) if text else ""
    s = _r(s)
    if len(s) > maxlen:
        return s[:maxlen - 3] + "..."
    return s


def print_live_table(total, answer_lists, form):
    import shutil
    w, _ = shutil.get_terminal_size()
    if w < 90:
        return

    # Calculate max cell width based on terminal width and number of columns
    num_cols = sum(1 for q in form["questions"] if str(q["id"]) in answer_lists)
    if num_cols == 0:
        num_cols = 1
    cell_max = max(10, min(22, (w - 12) // (num_cols + 1)))

    table = Table(show_header=True, header_style=f"bold {BLUE}", border_style=DIM, padding=(0, 1))
    table.add_column("User", style=f"bold {BLUE}", width=8, no_wrap=True)

    # Columns left-to-right in question order
    for q in form["questions"]:
        qid = str(q["id"])
        if qid in answer_lists:
            title_str = str(q.get('title', ''))
            short_title = _trunc(title_str, cell_max)
            table.add_column(short_title, style="white", max_width=cell_max, no_wrap=True)

    if not answer_lists:
        table.add_column("Status", style="white")
        for i in range(total):
            table.add_row(f"User {i+1}", "...")
    else:
        for i in range(total):
            row = [f"User {i+1}"]
            for q in form["questions"]:
                qid = str(q["id"])
                if qid in answer_lists:
                    ans = answer_lists[qid][i]
                    if ans:
                        row.append(_trunc(str(ans), cell_max))
                    else:
                        row.append("-")
            table.add_row(*row)

    console.print(table)
    console.print()


def _animate_shuffle(total, answer_lists, form):
    import time
    for _ in range(12):
        clear()
        display_banner()
        fake_lists = {}
        for q, ans in answer_lists.items():
            tmp = list(ans)
            random.shuffle(tmp)
            fake_lists[q] = tmp

        print_live_table(total, fake_lists, form)
        t = Text()
        t.append("  - ", style=f"bold {BLUE}")
        t.append("Shuffling all profiles for submission...", style="white")
        console.print(t)
        time.sleep(0.12)



# ─── Linked Distribution Builder ─────────────────────────────────────


def build_answers(form, total):
    """Walk through every question and build ordered answer lists.

    Choice questions  → manual split (assign counts to each option).
    Text questions    → every response written individually.

    Returns answer_lists: dict mapping q_id → list of N answers (None = skipped).
    """
    answer_lists = {}
    total_q = len(form["questions"])

    for qi, q in enumerate(form["questions"], 1):
        clear()
        display_banner()
        print_live_table(total, answer_lists, form)
        
        section(f"Question {qi} of {total_q}")

        # Header
        t = Text()
        t.append(f"  Q{qi}/{total_q}  ", style=f"bold {BLUE}")
        t.append(_r(q["title"]), style="bold white")
        if q["required"]:
            t.append("  *required", style=f"bold {RED}")
        else:
            t.append("  optional", style=f"dim {GREEN}")
        console.print(t)

        type_label = q["type"].replace("_", " ").title()
        console.print(Text(f"         Type: {type_label}", style="dim"))
        if q["description"]:
            console.print(Text(f"         {_r(q['description'])}", style="dim"))
        console.print()

        q_id = str(q["id"])

        # ── Text questions: individual answers ──
        if q["type"] in ("paragraph", "short_answer"):
            answers = [None] * total
            
            write_count = total
            if not q["required"]:
                write_count = ask_int(f"How many responses for this question? (0-{total})", min_val=0, max_val=total)
            
            if write_count > 0:
                console.print()
                for i in range(write_count):
                    val = ask(f"Response {i + 1}/{write_count}")
                    while not val and q["required"]:
                        msg("Cannot be empty", "warn")
                        val = ask(f"Response {i + 1}/{write_count}")
                    answers[i] = val if val else ""
            
            answer_lists[q_id] = answers
            msg(f"  {write_count} answers recorded", "ok")
            continue

        # ── Optional: skip entirely ──
        if not q["required"]:
            skip = ask_yn("Skip this question?", default=False)
            if skip:
                msg("Skipped", "info")
                continue

        # ── Choice questions: interactive menu ──
        options = _get_options_for_q(q)
        if not options:
            msg("Enter possible answers, one per line. Empty to finish.", "info")
            options = []
            while True:
                val = ask(f"Answer {len(options) + 1}")
                if not val:
                    if not options:
                        msg("Must enter at least one", "warn")
                        continue
                    break
                options.append(val)

        if not options:
            msg("No options, skipping", "warn")
            continue

        dist = _manual_split(options, total)

        # Expand distribution to ordered answer list
        answers = []
        for answer, count in dist.items():
            answers.extend([answer] * count)
        while len(answers) < total:
            answers.append(list(dist.keys())[-1])
        answers = answers[:total]

        answer_lists[q_id] = answers

    return answer_lists


def generate_linked_sets(answer_lists, total):
    """Create response sets from answer lists, positions preserved, then shuffle."""
    slots = [{} for _ in range(total)]
    for q_id, answers in answer_lists.items():
        for i in range(total):
            if i < len(answers) and answers[i] is not None:
                slots[i][q_id] = answers[i]
    random.shuffle(slots)
    return slots


# ─── Timer ───────────────────────────────────────────────────────────


def configure_timer(total):
    section("Timer Configuration")

    use_timer = ask_yn("Use a timer between responses?", default=False)
    if not use_timer:
        return None

    console.print()
    timer_type = ask_choice("Timer type", ["Regular", "Irregular"])

    config = {
        "irregular": timer_type == "I",
        "delay_seconds": 0,
        "min_seconds": 0,
        "max_seconds": 0,
    }

    console.print()
    if timer_type == "R":
        delay = ask_float("Delay between responses (seconds)", min_val=0.5)
        config["delay_seconds"] = delay
        config["min_seconds"] = delay
        config["max_seconds"] = delay
    else:
        min_d = ask_float("Min delay between responses (seconds)", min_val=0.5)
        max_d = ask_float("Max delay between responses (seconds)", min_val=min_d)
        config["min_seconds"] = min_d
        config["max_seconds"] = max_d
        config["delay_seconds"] = (min_d + max_d) / 2

    return config


def _get_delay(cfg):
    if not cfg:
        return 0
    if cfg["irregular"]:
        return random.uniform(cfg["min_seconds"], cfg["max_seconds"])
    return cfg["delay_seconds"]


# ─── Pre-Submission Summary ──────────────────────────────────────────


def show_pre_summary(form, answer_lists, total, timer_config):
    clear()
    display_banner()

    section("Submission Summary")

    msg(f"Form Title: {_r(form['title'])}", "info")
    msg(f"Submits:    {total}", "info")
    console.print()

    # Show the table as the summary
    print_live_table(total, answer_lists, form)

    if timer_config:
        if timer_config["irregular"]:
            td = f"Irregular, {timer_config['min_seconds']:.0f}s - {timer_config['max_seconds']:.0f}s"
        else:
            td = f"Regular, {timer_config['delay_seconds']:.0f}s between responses"
        msg(f"Timer: {td}", "info")
    else:
        msg("Timer: off (all at once)", "info")


# ─── Submission Engine ───────────────────────────────────────────────


def _build_post_data(form, response):
    data = []
    for q in form["questions"]:
        q_id = str(q["id"])
        if q_id not in response:
            continue
        value = response[q_id]
        if not q["entry_ids"]:
            continue
        eid = q["entry_ids"][0]

        if q["type"] == "date" and isinstance(value, str) and "-" in value:
            parts = value.split("-")
            if len(parts) == 3:
                data.append((f"entry.{eid}_year", parts[0]))
                data.append((f"entry.{eid}_month", parts[1]))
                data.append((f"entry.{eid}_day", parts[2]))
        elif q["type"] == "time" and isinstance(value, str) and ":" in value:
            parts = value.split(":")
            if len(parts) >= 2:
                data.append((f"entry.{eid}_hour", parts[0]))
                data.append((f"entry.{eid}_minute", parts[1]))
        elif q["type"] == "checkboxes" and isinstance(value, list):
            for v in value:
                data.append((f"entry.{eid}", str(v)))
        else:
            data.append((f"entry.{eid}", str(value)))
    return data


def _submit_one(form, response):
    data = _build_post_data(form, response)
    try:
        r = requests.post(form["submit_url"], data=data, headers=HTTP_HEADERS, timeout=30)
        return r.status_code == 200, r.status_code
    except requests.RequestException:
        return False, 0


def submit_all(form, response_sets, timer_config):
    """Submit all responses with progress bar and estimated time remaining."""
    total = len(response_sets)
    success = 0
    fail = 0
    start_time = time.time()

    section("Submitting")

    # Estimate total time
    avg_delay = 0
    if timer_config:
        avg_delay = (timer_config["min_seconds"] + timer_config["max_seconds"]) / 2
    est_total = total * (1.5 + avg_delay)
    if est_total >= 60:
        msg(f"Estimated time: ~{est_total / 60:.0f} minutes", "info")
    else:
        msg(f"Estimated time: ~{est_total:.0f} seconds", "info")
    console.print()

    with Progress(
        SpinnerColumn(style=BLUE),
        TextColumn("[bold white]{task.description}"),
        BarColumn(complete_style=BLUE, finished_style=GREEN),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("  Sending...", total=total)

        for i, resp in enumerate(response_sets):
            ok, _ = _submit_one(form, resp)
            if ok:
                success += 1
            else:
                fail += 1
            progress.advance(task)

            # Estimated time remaining
            elapsed = time.time() - start_time
            est = ""
            if i > 0:
                avg_per = elapsed / (i + 1)
                remaining_sec = (total - i - 1) * avg_per
                if remaining_sec >= 60:
                    est = f" ~{remaining_sec / 60:.0f}m left"
                elif remaining_sec > 5:
                    est = f" ~{remaining_sec:.0f}s left"

            progress.update(
                task,
                description=f"  Sending ({success}+ {fail}x){est}",
            )

            # Timer delay
            if timer_config and (i + 1) < total:
                delay = _get_delay(timer_config)
                remaining = delay
                while remaining > 0:
                    progress.update(
                        task,
                        description=f"  Waiting {remaining:.0f}s...",
                    )
                    step = min(1.0, remaining)
                    time.sleep(step)
                    remaining -= step
                progress.update(task, description="  Sending...")

    elapsed = time.time() - start_time
    return success, fail, elapsed


# ─── Post-Submission Results ─────────────────────────────────────────


def show_results(success, fail, total):
    section("Results")
    msg(f"Sent:   {success}/{total}", "ok" if fail == 0 else "info")
    if fail:
        msg(f"Failed: {fail}", "err")
    console.print()
    msg("Done!", "ok")


# ─── Main ────────────────────────────────────────────────────────────


def main():
    clear()
    display_banner()

    # 1 — URL
    url = ask("URL / Link")
    if not url:
        msg("No URL provided", "err")
        return

    # 2 — Parse form
    console.print()
    try:
        form = spinner_run("Parsing form...", parse_form, url)
    except Exception as e:
        msg(f"Failed to parse form: {e}", "err")
        return

    msg(f"Form Title: {_r(form['title'])}", "ok")
    msg(f"Questions:  {len(form['questions'])}", "ok")

    # 3 — How many submits?
    console.print()
    total = ask_int("How many submits do you want?", min_val=1)

    # 4 — Explain linked system
    console.print()
    msg("Linked Distribution System:", "info")
    msg(f"  {total} virtual users are created (User 1 to User {total})", "info")
    msg("  Each user keeps their answers across all questions", "info")
    msg("  The order you assign answers is the order users get them", "info")
    msg("  All responses are shuffled before submission", "info")

    # 5 — Build answer lists (question by question)
    answer_lists = build_answers(form, total)

    if not answer_lists:
        msg("No responses configured", "err")
        return

    # 6 — Shuffle animation (right after last question)
    _animate_shuffle(total, answer_lists, form)
    clear()
    display_banner()
    msg("Profiles shuffled!", "ok")
    console.print()

    # 7 — Timer
    timer_config = configure_timer(total)

    # 8 — Pre-submission summary (table + info)
    show_pre_summary(form, answer_lists, total, timer_config)

    console.print()
    if not ask_yn("Proceed with submission?", default=True):
        msg("Cancelled", "warn")
        return

    # 9 — Generate linked sets & submit
    response_sets = generate_linked_sets(answer_lists, total)
    success, fail, elapsed = submit_all(form, response_sets, timer_config)

    # 9 — Results
    show_results(success, fail, total)
    console.print()


# ─── Entry Point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        msg("Interrupted. Goodbye!", "warn")
        sys.exit(0)
