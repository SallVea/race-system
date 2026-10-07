#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║   VeloX: Roblox Mountain Racing Management  ║
║   Created by Sall | Race Management System  ║
╚══════════════════════════════════════════════╝
"""

import sys
import os
import json
import re
import time
import datetime
import requests

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.style import Style
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

# ─── Menu backend: curses built-in (fallback to numbered) ─────────────────────
import curses
MENU_BACKEND = "curses"

console = Console()

# ─── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = "velox_data.json"
TROPHY_MAP = {1: "🥇", 2: "🥈", 3: "🥉"}
DISCORD_GOLD_COLOR = 0xF1C40F
DISCORD_CYAN_COLOR = 0x00D4FF

POSITION_POINTS_DEFAULT = {
    1: 100,
    2: 80,
    3: 60,
    4: 50,
    5: 40,
    6: 30,
    7: 20,
    8: 10,
}

# ─── ASCII Banner ─────────────────────────────────────────────────────────────
BANNER = r"""
 ██╗   ██╗███████╗██╗      ██████╗ ██╗  ██╗
 ██║   ██║██╔════╝██║     ██╔═══██╗╚██╗██╔╝
 ██║   ██║█████╗  ██║     ██║   ██║ ╚███╔╝ 
 ╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║ ██╔██╗ 
  ╚████╔╝ ███████╗███████╗╚██████╔╝██╔╝ ██╗
   ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
  ██████╗  █████╗  ██████╗███████╗    
  ██╔══██╗██╔══██╗██╔════╝██╔════╝    
  ██████╔╝███████║██║     █████╗      
  ██╔══██╗██╔══██║██║     ██╔══╝      
  ██║  ██║██║  ██║╚██████╗███████╗    
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝   
  ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗ 
  ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝
  ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

SUB_BANNER = "⚡  R O B L O X   M O U N T A I N   R A C I N G   M A N A G E M E N T  ⚡"


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def clear():
    os.system("clear" if os.name != "nt" else "cls")


def show_banner():
    clear()
    banner_text = Text(BANNER)
    banner_text.stylize("bold cyan")
    console.print(banner_text)

    sub = Text(SUB_BANNER, justify="center")
    sub.stylize("bold magenta")
    console.print(sub)
    console.print(Rule(style="bright_cyan"))


def validate_webhook_url(url: str) -> bool:
    pattern = r"^https://discord(?:app)?\.com/api/webhooks/\d+/[\w-]+"
    return bool(re.match(pattern, url.strip()))


def neon_panel(content, title="", subtitle="", border_style="cyan"):
    return Panel(
        content,
        title=f"[bold magenta]{title}[/]" if title else "",
        subtitle=f"[dim cyan]{subtitle}[/]" if subtitle else "",
        border_style=border_style,
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    )


def status_indicator(msg: str, style: str = "green"):
    console.print(f"  [bold {style}]◉[/] [white]{msg}[/]")


def _curses_menu(stdscr, title: str, options: list[str]) -> int:
    """Inner curses menu — returns selected index or -1 on Escape/q."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)

    current = 0
    n = len(options)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        row = 1
        for tl in title.strip().splitlines():
            if row < h:
                try:
                    stdscr.addstr(row, 2, tl[:w-3], curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
            row += 1
        row += 1

        # Draw options
        for i, opt in enumerate(options):
            if row >= h - 1:
                break
            prefix = " ▶  " if i == current else "    "
            line = f"{prefix}{opt}"[:w-3]
            attr = curses.color_pair(2) | curses.A_BOLD if i == current else curses.color_pair(1)
            try:
                stdscr.addstr(row, 2, line, attr)
            except curses.error:
                pass
            row += 1

        # Footer hint
        if h > 2:
            try:
                stdscr.addstr(h - 1, 2, " ↑↓ Navigasi  |  Enter Pilih  |  q Batal "[:w-3], curses.A_DIM)
            except curses.error:
                pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')):
            current = (current - 1) % n
        elif key in (curses.KEY_DOWN, ord('j')):
            current = (current + 1) % n
        elif key in (curses.KEY_ENTER, 10, 13):
            return current
        elif key in (ord('q'), 27):
            return -1


def arrow_menu(title: str, options: list[str], back_label: str = None) -> int:
    """
    Arrow-key interactive menu using built-in curses.
    Returns the index of the chosen option (0-based), or -1 if cancelled/back.
    """
    if back_label:
        full_options = options + [f"← {back_label}"]
    else:
        full_options = options

    try:
        idx = curses.wrapper(_curses_menu, title, full_options)
    except Exception:
        # Fallback: numbered menu if curses fails
        console.print(f"\n  [bold cyan]{title}[/]\n")
        for i, opt in enumerate(full_options, 1):
            console.print(f"  [bold magenta]{i}.[/] {opt}")
        while True:
            raw = Prompt.ask("\n  [bold cyan]Pilih nomor[/]")
            try:
                n = int(raw) - 1
                if 0 <= n < len(full_options):
                    idx = n
                    break
            except ValueError:
                pass
            console.print("  [red]Input tidak valid, coba lagi.[/]")

    if idx == -1:
        return -1
    if back_label and idx == len(full_options) - 1:
        return -1
    return idx


# ══════════════════════════════════════════════════════════════════════════════
#  DATA PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "mode": None,
        "players": [],
        "point_config": {},
        "sessions": [],
        "leaderboard": {},
    }


def save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        status_indicator(f"Data disimpan ke [cyan]{DATA_FILE}[/]", "green")
    except IOError as e:
        status_indicator(f"Gagal menyimpan data: {e}", "red")


# ══════════════════════════════════════════════════════════════════════════════
#  LEADERBOARD TABLE
# ══════════════════════════════════════════════════════════════════════════════

def build_leaderboard_table(leaderboard: dict, title: str = "🏆 LEADERBOARD") -> Table:
    table = Table(
        title=f"[bold yellow]{title}[/]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        header_style="bold magenta",
        show_lines=True,
        min_width=50,
    )
    table.add_column("Pos", justify="center", style="bold yellow", no_wrap=True, width=6)
    table.add_column("Nama Player", style="bold white", no_wrap=True)
    table.add_column("Total Poin", justify="right", style="bold cyan", width=12)

    sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

    for rank, (player, points) in enumerate(sorted_board, 1):
        trophy = TROPHY_MAP.get(rank, f"#{rank}")
        row_style = ""
        if rank == 1:
            row_style = "bold yellow on dark_goldenrod"
        elif rank == 2:
            row_style = "bold white on grey23"
        elif rank == 3:
            row_style = "bold dark_orange on grey15"
        table.add_row(str(trophy), player, str(points), style=row_style)

    return table


def build_session_result_table(session_results: list, title: str = "Hasil Sesi") -> Table:
    table = Table(
        title=f"[bold cyan]{title}[/]",
        box=box.SIMPLE_HEAVY,
        border_style="magenta",
        header_style="bold cyan",
        show_lines=False,
        min_width=45,
    )
    table.add_column("Posisi", justify="center", style="bold magenta", width=9)
    table.add_column("Nama Player", style="white")
    table.add_column("Poin", justify="right", style="bold yellow", width=8)

    for entry in session_results:
        pos = entry.get("position", "?")
        trophy = TROPHY_MAP.get(pos, f"#{pos}")
        player = entry.get("player", "-")
        pts = entry.get("points", 0)
        table.add_row(f"{trophy} {pos}", player, str(pts) if pts is not None else "-")

    return table


# ══════════════════════════════════════════════════════════════════════════════
#  DISCORD WEBHOOK
# ══════════════════════════════════════════════════════════════════════════════

def format_leaderboard_codeblock(leaderboard: dict, sessions: list = None) -> str:
    """
    Format leaderboard codeblock.
    Jika sessions diberikan, tampilkan kolom poin per sesi (S1, S2, ...) + Total.
    Jika tidak, tampilkan format sederhana Nama Player + Poin.
    """
    sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

    if sessions:
        # ── Build per-session poin map ──────────────────────────────────────
        # sessions = list of {session_name, results: [{player, points, ...}]}
        num_sessions = len(sessions)
        # player -> [poin_sesi1, poin_sesi2, ...]
        session_pts: dict[str, list[int]] = {p: [0] * num_sessions for p in leaderboard}
        for s_idx, sess in enumerate(sessions):
            for entry in sess.get("results", []):
                player = entry.get("player", "")
                pts = entry.get("points", 0) or 0
                if player in session_pts:
                    session_pts[player][s_idx] = pts

        # ── Build header ────────────────────────────────────────────────────
        # Nama Player col = 18 char, each Sn col = 5 char, Total = 7 char
        sesi_headers = "  ".join(f"S{i+1:1d}" for i in range(num_sessions))
        header = f"{'Pos':<5} {'Nama Player':<18}  {sesi_headers}  {'Total':>6}"
        sep    = "─" * len(header)

        lines = [header, sep]
        for rank, (player, total) in enumerate(sorted_board, 1):
            trophy_text = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank} ")
            pts_cols = "  ".join(f"{session_pts[player][i]:>3}" for i in range(num_sessions))
            lines.append(f"{trophy_text:<5} {player:<18}  {pts_cols}  {total:>6}")
    else:
        # ── Format sederhana tanpa histori sesi ────────────────────────────
        header = f"{'Pos':<5} {'Nama Player':<20} {'Poin':>8}"
        sep    = "─" * 36
        lines  = [header, sep]
        for rank, (player, points) in enumerate(sorted_board, 1):
            trophy_text = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank} ")
            lines.append(f"{trophy_text:<5} {player:<20} {points:>8}")

    return "\n".join(lines)


def format_session_codeblock(session_results: list) -> str:
    lines = []
    lines.append(f"{'Pos':<5} {'Nama Player':<20} {'Poin':>8}")
    lines.append("─" * 36)
    for entry in session_results:
        pos = entry.get("position", "?")
        trophy_text = {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, f"#{pos} ")
        player = entry.get("player", "-")
        pts = entry.get("points", "")
        lines.append(f"{trophy_text:<5} {player:<20} {str(pts):>8}")
    return "\n".join(lines)


def count_wins_mode_b(sessions: list) -> dict:
    """
    Hitung jumlah kemenangan (Juara 1 / Posisi 1) tiap pemain
    dari semua sesi Mode B.
    Kembalikan dict: {nama_player: jumlah_win}
    """
    win_count: dict[str, int] = {}
    for sess in sessions:
        for entry in sess.get("results", []):
            if entry.get("position") == 1:
                player = entry.get("player", "")
                if player:
                    win_count[player] = win_count.get(player, 0) + 1
    # Pastikan semua pemain yang pernah tampil terdaftar (meski 0 win)
    for sess in sessions:
        for entry in sess.get("results", []):
            player = entry.get("player", "")
            if player and player not in win_count:
                win_count[player] = 0
    return win_count


def format_wincount_codeblock(win_count: dict) -> str:
    """
    Format tabel rekapitulasi Win untuk Discord (Mode B).
    Tanpa kolom Pos — hanya Nama Player dan Win.
    Diurutkan dari Win terbanyak.
    """
    sorted_wins = sorted(win_count.items(), key=lambda x: x[1], reverse=True)
    header = f"{'Nama Player':<25} {'Win':>4}"
    sep    = "─" * 32
    lines  = [header, sep]
    for player, wins in sorted_wins:
        lines.append(f"{player:<25} {wins:>4}")
    return "\n".join(lines)



def send_discord_webhook(
    webhook_url: str,
    mode_label: str,
    session_name: str,
    session_results: list,
    leaderboard: dict = None,
    mode_code: str = "A",
    sessions: list = None,
):
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    color = DISCORD_GOLD_COLOR if mode_code == "A" else DISCORD_CYAN_COLOR

    fields = [
        {
            "name": "🎮  Mode & Sesi",
            "value": f"**{mode_label}** — `{session_name}`",
            "inline": False,
        },
    ]

    # Hanya tampilkan field Hasil Sesi jika ada data hasil sesi
    if session_results:
        session_block = format_session_codeblock(session_results)
        fields.append({
            "name": f"📋  Hasil Sesi ({session_name})",
            "value": f"```\n{session_block}\n```",
            "inline": False,
        })

    if leaderboard:
        # Mode A: Papan peringkat kumulatif dengan kolom per-sesi
        lb_block = format_leaderboard_codeblock(leaderboard, sessions=sessions)
        fields.append({
            "name": "🏆  Papan Peringkat Kumulatif",
            "value": f"```\n{lb_block}\n```",
            "inline": False,
        })

    if sessions and mode_code == "B":
        # Mode B: Rekap Win — hitung otomatis dari semua sesi
        win_count = count_wins_mode_b(sessions)
        win_block = format_wincount_codeblock(win_count)
        total_sesi = len(sessions)
        fields.append({
            "name": f"🏆  Rekap Kemenangan ({total_sesi} Sesi)",
            "value": f"```\n{win_block}\n```",
            "inline": False,
        })

    embed = {
        "title": "⚡ RACING LEADERBOARD — VeloX Race Master ⚡",
        "description": (
            "```\n"
            "╔══════════════════════════════════╗\n"
            "║          RACING RESULTS          ║\n"
            "╚══════════════════════════════════╝\n"
            "```"
        ),
        "color": color,
        "fields": fields,
        "footer": {
            "text": "Race Management System • Created by Sall",
            "icon_url": "https://i.imgur.com/AfFp7pu.png",
        },
        "timestamp": ts,
    }

    payload = {
        "content": "@everyone",
        "allowed_mentions": {"parse": ["everyone"]},
        "embeds": [embed],
    }

    try:
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[bold cyan]Mengirim ke Discord..."),
            transient=True,
        ) as progress:
            task = progress.add_task("send", total=None)
            resp = requests.post(webhook_url, json=payload, timeout=10)
            progress.update(task, completed=True)

        if resp.status_code in (200, 204):
            status_indicator("Berhasil dikirim ke Discord! ✅", "green")
        else:
            status_indicator(
                f"Discord error [{resp.status_code}]: {resp.text[:120]}", "red"
            )
    except requests.exceptions.ConnectionError:
        status_indicator("Koneksi gagal — periksa internet Anda.", "red")
    except requests.exceptions.Timeout:
        status_indicator("Request timeout saat mengirim webhook.", "yellow")
    except requests.exceptions.RequestException as e:
        status_indicator(f"Error webhook: {e}", "red")


# ══════════════════════════════════════════════════════════════════════════════
#  POINT CONFIGURATION (MODE A)
# ══════════════════════════════════════════════════════════════════════════════

def configure_points(num_positions: int) -> dict:
    console.print(
        neon_panel(
            f"[bold white]Konfigurasi poin untuk [cyan]{num_positions}[/] posisi.\n"
            "[dim]Tekan Enter untuk gunakan nilai default.[/]",
            title="⚙  KONFIGURASI POIN",
            border_style="magenta",
        )
    )
    point_config = {}
    for pos in range(1, num_positions + 1):
        default = POSITION_POINTS_DEFAULT.get(pos, max(0, 10 - pos))
        raw = Prompt.ask(
            f"  [cyan]Poin untuk Posisi [bold magenta]#{pos}[/][/]",
            default=str(default),
        )
        try:
            point_config[pos] = int(raw)
        except ValueError:
            point_config[pos] = default
            console.print(f"  [yellow]Input tidak valid, menggunakan default: {default}[/]")
    return point_config


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION INPUT — ARROW KEY SELECTION (MODE A)
# ══════════════════════════════════════════════════════════════════════════════

def input_session_mode_a(
    session_name: str,
    players: list[str],
    point_config: dict,
) -> list[dict]:
    """
    Returns a list of {position, player, points} dicts.
    """
    num_pos = len(point_config)
    results = []
    remaining_players = players.copy()

    console.print(
        neon_panel(
            f"[bold white]Sesi: [cyan]{session_name}[/]\n"
            f"[dim]Pilih pemain untuk setiap posisi menggunakan ↑↓ + Enter.[/]",
            title="🏁  INPUT HASIL SESI",
            border_style="cyan",
        )
    )

    for pos in range(1, num_pos + 1):
        if not remaining_players:
            console.print("  [yellow]Tidak ada pemain tersisa.[/]")
            break

        trophy = TROPHY_MAP.get(pos, f"#{pos}")
        console.print(f"\n  [bold yellow]Posisi {trophy} {pos}:[/]")

        chosen_idx = arrow_menu(
            f"Pilih pemain untuk Posisi #{pos}:",
            remaining_players,
        )
        if chosen_idx < 0:
            console.print("  [red]Dibatalkan.[/]")
            break

        chosen_player = remaining_players[chosen_idx]
        pts = point_config.get(pos, 0)
        results.append({"position": pos, "player": chosen_player, "points": pts})
        remaining_players.pop(chosen_idx)
        status_indicator(
            f"Posisi #{pos} → [bold magenta]{chosen_player}[/] mendapat [bold cyan]{pts}[/] poin",
            "green",
        )

    return results


# ══════════════════════════════════════════════════════════════════════════════
#  MODE A — CHAMPIONSHIP ACCUMULATION
# ══════════════════════════════════════════════════════════════════════════════

def mode_a_championship(webhook_url: str, data: dict):
    show_banner()
    console.print(
        neon_panel(
            "[bold white]Mode A: [cyan]Sistem Poin (Championship Akumulasi)[/]\n"
            "[dim]Poin dikumpulkan lintas sesi. Pemimpin ditentukan dari total poin.[/]",
            title="⚡  MODE A — CHAMPIONSHIP",
            border_style="cyan",
        )
    )
    time.sleep(0.5)

    # ── Player list ──────────────────────────────────────────────────────────
    if data.get("players") and data["mode"] == "A":
        use_existing = Confirm.ask(
            "\n  [cyan]Gunakan daftar pemain sebelumnya?[/]", default=True
        )
        if not use_existing:
            data["players"] = []
            data["leaderboard"] = {}
    else:
        data["players"] = []
        data["leaderboard"] = {}

    if not data["players"]:
        console.print(
            neon_panel(
                "[dim]Masukkan nama pemain satu per satu. Ketik [bold]selesai[/] untuk lanjut.[/]",
                title="👥  DAFTAR PEMAIN",
                border_style="magenta",
            )
        )
        while True:
            name = Prompt.ask("  [cyan]Nama pemain[/] [dim](atau 'selesai')[/]")
            if name.lower() in ("selesai", "done", "exit", "q"):
                break
            name = name.strip()
            if not name:
                continue
            if name in data["players"]:
                console.print(f"  [yellow]'{name}' sudah ada.[/]")
            else:
                data["players"].append(name)
                if name not in data["leaderboard"]:
                    data["leaderboard"][name] = 0
                status_indicator(f"[bold white]{name}[/] ditambahkan ✓", "green")

    if len(data["players"]) < 2:
        console.print("  [red]Minimal 2 pemain diperlukan.[/]")
        input("\n  Tekan Enter untuk kembali...")
        return

    # ── Point config ─────────────────────────────────────────────────────────
    if not data.get("point_config") or data["mode"] != "A":
        num_pos = len(data["players"])
        data["point_config"] = configure_points(num_pos)

    data["mode"] = "A"
    save_data(data)

    # ── Session loop ─────────────────────────────────────────────────────────
    while True:
        show_banner()
        console.print(Align.center(build_leaderboard_table(data["leaderboard"])))
        console.print()

        action = arrow_menu(
            "📋  Menu Sesi Championship",
            [
                "🏁  Tambah Sesi Baru",
                "📊  Lihat Leaderboard",
                "📤  Kirim Leaderboard ke Discord",
                "🔄  Reset Semua Data",
                "🚪  Kembali ke Menu Utama",
            ],
        )

        if action == 0:  # Tambah Sesi Baru
            session_num = len(data.get("sessions", [])) + 1
            session_name = Prompt.ask(
                f"  [cyan]Nama Sesi[/]",
                default=f"Race Sesi {session_num}",
            )

            point_config_int = {int(k): v for k, v in data["point_config"].items()}
            results = input_session_mode_a(
                session_name, data["players"], point_config_int
            )

            if not results:
                console.print("  [yellow]Tidak ada hasil untuk disimpan.[/]")
                input("  Tekan Enter lanjut...")
                continue

            # Accumulate
            for entry in results:
                player = entry["player"]
                pts = entry["points"]
                data["leaderboard"][player] = data["leaderboard"].get(player, 0) + pts

            session_record = {
                "session_name": session_name,
                "results": results,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            if "sessions" not in data:
                data["sessions"] = []
            data["sessions"].append(session_record)
            save_data(data)

            # Show result
            console.print()
            console.print(Align.center(build_session_result_table(results, title=session_name)))
            console.print()
            console.print(Align.center(build_leaderboard_table(data["leaderboard"])))
            console.print()

            if Confirm.ask("  [cyan]Kirim hasil sesi ini ke Discord?[/]", default=True):
                send_discord_webhook(
                    webhook_url=webhook_url,
                    mode_label="Mode A — Championship",
                    session_name=session_name,
                    session_results=results,
                    leaderboard=data["leaderboard"],
                    mode_code="A",
                    sessions=data["sessions"],
                )
            input("\n  Tekan Enter untuk lanjut...")

        elif action == 1:  # Lihat Leaderboard
            console.print(Align.center(build_leaderboard_table(data["leaderboard"])))
            input("\n  Tekan Enter untuk lanjut...")

        elif action == 2:  # Kirim ke Discord
            if not data["leaderboard"]:
                console.print("  [yellow]Leaderboard masih kosong.[/]")
            else:
                send_discord_webhook(
                    webhook_url=webhook_url,
                    mode_label="Mode A — Championship (Full Update)",
                    session_name="Standings Update",
                    session_results=[],
                    leaderboard=data["leaderboard"],
                    mode_code="A",
                    sessions=data["sessions"],
                )
            input("\n  Tekan Enter untuk lanjut...")

        elif action == 3:  # Reset
            if Confirm.ask(
                "  [bold red]⚠  Yakin reset SEMUA data championship?[/]", default=False
            ):
                data["players"] = []
                data["leaderboard"] = {}
                data["sessions"] = []
                data["point_config"] = {}
                data["mode"] = None
                save_data(data)
                status_indicator("Data direset.", "yellow")
                input("  Tekan Enter...")
            return

        elif action == 4 or action < 0:  # Kembali
            return


# ══════════════════════════════════════════════════════════════════════════════
#  MODE B — SINGLE / STANDALONE SESSION
# ══════════════════════════════════════════════════════════════════════════════

def mode_b_single(webhook_url: str, data: dict):
    show_banner()
    console.print(
        neon_panel(
            "[bold white]Mode B: [cyan]Sistem Single (Per-Sesi Standalone)[/]\n"
            "[dim]Setiap sesi berdiri sendiri. Poin tidak diakumulasi.[/]",
            title="⚡  MODE B — STANDALONE SESSION",
            border_style="magenta",
        )
    )
    time.sleep(0.5)
    data["mode"] = "B"

    all_session_results = []

    while True:
        show_banner()
        console.print(
            neon_panel(
                f"[dim]Total sesi telah diinput: [bold cyan]{len(all_session_results)}[/][/]",
                title="📋  MODE B — SESSION MANAGER",
                border_style="magenta",
            )
        )

        if all_session_results:
            console.print(
                Align.center(
                    build_session_result_table(
                        all_session_results[-1]["results"],
                        title=f"Sesi Terakhir: {all_session_results[-1]['session_name']}",
                    )
                )
            )

        action = arrow_menu(
            "📋  Pilih Aksi:",
            [
                "🏁  Input Sesi Baru",
                "📋  Lihat Semua Sesi",
                "📤  Selesai & Kirim Hasil ke Discord",
                "🚪  Kembali ke Menu Utama",
            ],
        )

        if action == 0:  # Input Sesi Baru
            session_name = Prompt.ask(
                "  [cyan]Nama Sesi[/] [dim](mis: 'Kualifikasi Sesi 1')[/]",
                default=f"Sesi {len(all_session_results)+1}",
            )

            console.print(
                neon_panel(
                    "[dim]Masukkan hasil per posisi.\n"
                    "Ketik [bold]selesai[/] pada nama pemain untuk menghentikan input posisi.[/]",
                    title=f"🏁  INPUT — {session_name}",
                    border_style="cyan",
                )
            )

            results = []
            pos = 1
            used_players = set()
            while True:
                trophy = TROPHY_MAP.get(pos, f"#{pos}")
                player = Prompt.ask(
                    f"  [bold cyan]Posisi {trophy} {pos}[/] — nama pemain [dim]('selesai' untuk stop)[/]"
                ).strip()

                if player.lower() in ("selesai", "done", "q", ""):
                    break
                if player in used_players:
                    console.print(f"  [yellow]'{player}' sudah dimasukkan untuk sesi ini.[/]")
                    continue

                used_players.add(player)
                results.append({"position": pos, "player": player, "points": None})
                status_indicator(f"Posisi #{pos} → [bold magenta]{player}[/]", "green")
                pos += 1

            if results:
                console.print()
                console.print(Align.center(build_session_result_table(results, title=session_name)))
                console.print()
                if Confirm.ask("  [cyan]Simpan sesi ini?[/]", default=True):
                    record = {
                        "session_name": session_name,
                        "results": results,
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                    all_session_results.append(record)
                    if "sessions" not in data:
                        data["sessions"] = []
                    data["sessions"].append(record)
                    save_data(data)
                    status_indicator("Sesi disimpan! ✅", "green")
            else:
                console.print("  [yellow]Tidak ada data untuk disimpan.[/]")
            input("\n  Tekan Enter untuk lanjut...")

        elif action == 1:  # Lihat Semua Sesi
            if not all_session_results:
                console.print("  [yellow]Belum ada sesi.[/]")
            else:
                for sr in all_session_results:
                    console.print(
                        Align.center(
                            build_session_result_table(
                                sr["results"], title=sr["session_name"]
                            )
                        )
                    )
                    console.print()
            input("  Tekan Enter untuk lanjut...")

        elif action == 2:  # Selesai & Kirim
            if not all_session_results:
                console.print("  [yellow]Tidak ada sesi untuk dikirim.[/]")
                input("  Tekan Enter...")
                continue

            # Hitung rekap win dari semua sesi
            win_count = count_wins_mode_b(all_session_results)
            total_sesi = len(all_session_results)

            # Tampilkan preview rekap win di terminal sebelum kirim
            console.print()
            recap_table = Table(
                title="[bold yellow]🏆 Rekap Kemenangan (Mode B)[/]",
                box=box.DOUBLE_EDGE,
                border_style="cyan",
                header_style="bold magenta",
                show_lines=True,
                min_width=40,
            )
            recap_table.add_column("Nama Player", style="bold white")
            recap_table.add_column("Win", justify="right", style="bold cyan", width=8)
            for player, wins in sorted(win_count.items(), key=lambda x: x[1], reverse=True):
                recap_table.add_row(player, str(wins))
            console.print(Align.center(recap_table))
            console.print()

            # Satu pesan webhook berisi nama sesi terakhir + rekap win semua sesi
            sesi_names = ", ".join(sr["session_name"] for sr in all_session_results)
            console.print(f"  [dim]📤 Mengirim rekap [bold cyan]{total_sesi} sesi[/] ke Discord...[/]")
            send_discord_webhook(
                webhook_url=webhook_url,
                mode_label="Mode B — Standalone",
                session_name=sesi_names,
                session_results=[],           # Tidak kirim detail per-sesi
                leaderboard=None,
                mode_code="B",
                sessions=all_session_results, # Win dihitung di sini
            )

            status_indicator(
                f"Rekap [bold]{total_sesi}[/] sesi berhasil dikirim! ✅", "green"
            )
            input("\n  Tekan Enter untuk lanjut...")
            return

        elif action == 3 or action < 0:  # Kembali
            return


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════

def main_menu(webhook_url: str, data: dict):
    while True:
        show_banner()
        console.print(
            neon_panel(
                f"  [dim]Webhook:[/] [green]{webhook_url[:60]}{'...' if len(webhook_url)>60 else ''}[/]\n"
                f"  [dim]Data File:[/] [cyan]{os.path.abspath(DATA_FILE)}[/]",
                title="🏎  VELOX RACE MASTER",
                subtitle="Roblox Mountain Racing Management",
                border_style="bright_cyan",
            )
        )

        idx = arrow_menu(
            "🚀  Pilih Mode Pertandingan:",
            [
                "⚡  Mode A — Sistem Poin (Championship / Akumulasi)",
                "🏁  Mode B — Sistem Single (Standalone Per-Sesi)",
                "📊  Lihat Data Tersimpan",
                "🔗  Ganti Webhook URL",
                "🚪  Keluar",
            ],
        )

        if idx == 0:
            mode_a_championship(webhook_url, data)
        elif idx == 1:
            mode_b_single(webhook_url, data)
        elif idx == 2:
            show_saved_data(data)
        elif idx == 3:
            webhook_url = input_webhook_url(current=webhook_url)
        elif idx in (4, -1):
            show_banner()
            console.print(
                Align.center(
                    neon_panel(
                        "[bold cyan]Terima kasih telah menggunakan VeloX Race Master!\n"
                        "[dim]Created by Sall • Roblox Mountain Racing[/]",
                        title="👋  SAMPAI JUMPA",
                        border_style="magenta",
                    )
                )
            )
            time.sleep(1.5)
            sys.exit(0)


def show_saved_data(data: dict):
    show_banner()
    console.print(
        neon_panel(
            f"[dim]Mode:[/] [cyan]{data.get('mode', 'Belum diset')}[/]\n"
            f"[dim]Jumlah Pemain:[/] [bold]{len(data.get('players', []))}[/]\n"
            f"[dim]Total Sesi:[/] [bold]{len(data.get('sessions', []))}[/]",
            title="📊  DATA TERSIMPAN",
            border_style="cyan",
        )
    )

    if data.get("leaderboard"):
        console.print(Align.center(build_leaderboard_table(data["leaderboard"])))

    if data.get("sessions"):
        console.print(f"\n  [bold magenta]Riwayat Sesi:[/]")
        for i, s in enumerate(data["sessions"], 1):
            ts = s.get("timestamp", "-")
            console.print(
                f"  [dim]{i}.[/] [cyan]{s['session_name']}[/] [dim]— {ts[:19]}[/]"
            )

    input("\n  Tekan Enter untuk kembali...")


# ══════════════════════════════════════════════════════════════════════════════
#  WEBHOOK INPUT
# ══════════════════════════════════════════════════════════════════════════════

def input_webhook_url(current: str = "") -> str:
    show_banner()
    console.print(
        neon_panel(
            "[bold white]Masukkan Discord Webhook URL.\n"
            "[dim]Format: https://discord.com/api/webhooks/ID/TOKEN[/]",
            title="🔗  DISCORD WEBHOOK",
            border_style="magenta",
        )
    )

    if current:
        console.print(f"  [dim]URL saat ini: {current}[/]\n")

    while True:
        url = Prompt.ask("  [cyan]Webhook URL[/]", default=current or "")
        url = url.strip()
        if not url:
            console.print("  [red]URL tidak boleh kosong.[/]")
            continue
        if not validate_webhook_url(url):
            console.print(
                "  [red]Format URL tidak valid.[/] [dim]Contoh format:\n"
                "  https://discord.com/api/webhooks/123456789/abcDEFxyz...[/]"
            )
            continue
        status_indicator("URL valid ✓", "green")
        return url


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    try:
        show_banner()

        # Intro delay
        console.print(
            Align.center(
                "[bold dim cyan]Memuat sistem...[/]"
            )
        )
        time.sleep(0.8)

        data = load_data()

        # Webhook URL
        webhook_url = input_webhook_url()

        main_menu(webhook_url, data)

    except KeyboardInterrupt:
        console.print("\n\n  [bold yellow]⚠  Program dihentikan oleh pengguna (Ctrl+C).[/]")
        sys.exit(0)


if __name__ == "__main__":
    main()
