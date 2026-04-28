
import os
import psycopg2
import psycopg2.extras
from datetime import date

#КОНФИГУРАЦИЯ
from connect import get_conn
from config import PAGE_SIZE

PAGE_SIZE = 5   

#ВСПОМОГАТЕЛЬНЫЕ ЭЛЕМЕНТЫ
SORT_FIELDS = {
    "1": ("first_name",  "By name"),
    "2": ("birthday",    "By birthday"),
    "3": ("created_at",  "By date added"),
}

COLORS = {
    "header":  "\033[1;36m",   
    "prompt":  "\033[1;33m",   
    "ok":      "\033[0;32m",   
    "err":     "\033[0;31m",   
    "dim":     "\033[0;90m",   
    "reset":   "\033[0m",
}

def c(text, color):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def hr(char="─", width=60):
    print(c(char * width, "dim"))

def clear():
    os.system("cls" if os.name == "nt" else "clear")


#ПОИСК КОНТАКТОВ
def fetch_contacts(conn, *, group_id=None, email_search=None,
                   sort_field="first_name", page=0):
    """
    Returns (rows, total_count).
    Applies group filter, email search,
    sorting and pagination via LIMIT/OFFSET.
    """
    where_clauses = []
    params = []

    if group_id is not None:
        where_clauses.append("c.group_id = %s")
        params.append(group_id)

    if email_search:
        where_clauses.append("c.email ILIKE %s")
        params.append(f"%{email_search}%")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    safe_sort = sort_field if sort_field in {f for f, _ in SORT_FIELDS.values()} else "first_name"
    order_sql = f"ORDER BY c.{safe_sort} ASC NULLS LAST, c.id ASC"

    base_query = f"""
        SELECT
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.birthday,
            c.created_at::date        AS added,
            g.name                    AS group_name,
            -- aggregate phones into one string
            STRING_AGG(
                p.number || ' (' || p.label || ')',
                ', '
                ORDER BY p.is_primary DESC, p.id
            )                         AS phones
        FROM contacts c
        LEFT JOIN groups  g ON g.id = c.group_id
        LEFT JOIN phones  p ON p.contact_id = c.id
        {where_sql}
        GROUP BY c.id, c.first_name, c.last_name, c.email,
                 c.birthday, c.created_at, g.name
        {order_sql}
    """

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT COUNT(*) AS n FROM ({base_query}) AS sub", params)
        total = cur.fetchone()["n"]

        cur.execute(
            base_query + " LIMIT %s OFFSET %s",
            params + [PAGE_SIZE, page * PAGE_SIZE],
        )
        rows = cur.fetchall()

    return rows, total


#ОТОБРАЖЕНИЕ КОНТАКТОВ
def print_contacts(rows, total, page, sort_label, group_name, email_search):
    clear()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    hr("═")
    print(c("PHONE BOOK", "header"))
    hr("═")

    filters = []
    if group_name:   filters.append(f"group: {group_name}")
    if email_search: filters.append(f"email contains \"{email_search}\"")
    filters.append(f"sort: {sort_label}")
    print(c("  Filters: " + " │ ".join(filters), "dim"))
    print(c(f"  Page {page + 1} of {total_pages}  ({total} contacts)", "dim"))
    hr()

    if not rows:
        print(c("No contacts found.", "err"))
    else:
        for i, r in enumerate(rows, start=page * PAGE_SIZE + 1):
            name = f"{r['first_name']} {r['last_name'] or ''}".strip()
            print(c(f"  {i:>3}. {name}", "ok"))

            if r["phones"]:
                print(f"       📞 {r['phones']}")
            if r["email"]:
                print(f"       ✉  {r['email']}")
            if r["birthday"]:
                print(f"       🎂 {r['birthday'].strftime('%d.%m.%Y')}")
            if r["group_name"]:
                print(f"       🏷  {r['group_name']}")
            print(c(f"       added: {r['added']}", "dim"))
            hr("·", 40)

    hr()


#ФИЛЬТР
def menu_filter(conn, state):
    """Prompts user to select a group for filtering."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()

    print(c("\n  Filter by group", "header"))
    print("   0. All groups")
    for g in groups:
        print(f"   {g['id']}. {g['name']}")

    choice = input(c("  Select number (Enter = no change): ", "prompt")).strip()
    if choice == "0":
        state["group_id"]   = None
        state["group_name"] = None
        state["page"]       = 0
    elif choice.isdigit():
        gid = int(choice)
        found = next((g for g in groups if g["id"] == gid), None)
        if found:
            state["group_id"]   = gid
            state["group_name"] = found["name"]
            state["page"]       = 0
        else:
            print(c("  Group not found.", "err"))


def menu_email_search(state):
    """Sets partial email search."""
    print(c("\n  Search by email (partial match)", "header"))
    term = input(c("  Enter part of email (Enter = clear): ", "prompt")).strip()
    state["email_search"] = term or None
    state["page"]         = 0


def menu_sort(state):
    """Selects sort field."""
    print(c("\n  Sort by", "header"))
    for key, (_, label) in SORT_FIELDS.items():
        print(f"   {key}. {label}")

    choice = input(c("  Select (Enter = no change): ", "prompt")).strip()
    if choice in SORT_FIELDS:
        field, label        = SORT_FIELDS[choice]
        state["sort_field"] = field
        state["sort_label"] = label
        state["page"]       = 0


#ГЛАВНЫЙ ЦИКЛ
def print_help():
    cmds = [
        ("next",   "next page"),
        ("prev",   "previous page"),
        ("filter", "filter by group"),
        ("search", "search by email"),
        ("sort",   "change sort order"),
        ("reset",  "clear all filters"),
        ("quit",   "exit"),
    ]
    print(c("\n  Commands:", "header"))
    for cmd, desc in cmds:
        print(f"   {c(cmd, 'prompt'):<20} — {desc}")
    print()


def main():
    try:
        conn = get_conn()
    except Exception as e:
        print(c(f"Could not connect to database: {e}", "err"))
        return

    state = {
        "page":         0,
        "group_id":     None,
        "group_name":   None,
        "email_search": None,
        "sort_field":   "first_name",
        "sort_label":   "By name",
    }

    print_help()

    while True:
        try:
            rows, total = fetch_contacts(
                conn,
                group_id     = state["group_id"],
                email_search = state["email_search"],
                sort_field   = state["sort_field"],
                page         = state["page"],
            )
        except Exception as e:
            print(c(f"Query error: {e}", "err"))
            break

        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        print_contacts(
            rows, total, state["page"],
            state["sort_label"],
            state["group_name"],
            state["email_search"],
        )

        cmd = input(c("  > ", "prompt")).strip().lower()

        if cmd in ("quit", "q", "exit"):
            print(c("\n  Goodbye! \n", "ok"))
            break

        elif cmd in ("next", "n"):
            if state["page"] < total_pages - 1:
                state["page"] += 1
            else:
                print(c("  This is the last page.", "dim"))
                input("  (Enter)")

        elif cmd in ("prev", "p"):
            if state["page"] > 0:
                state["page"] -= 1
            else:
                print(c("  This is the first page.", "dim"))
                input("  (Enter)")

        elif cmd in ("filter", "f"):
            menu_filter(conn, state)

        elif cmd in ("search", "s"):
            menu_email_search(state)

        elif cmd == "sort":
            menu_sort(state)

        elif cmd in ("reset", "r"):
            state.update({
                "page": 0, "group_id": None, "group_name": None,
                "email_search": None, "sort_field": "first_name",
                "sort_label": "By name",
            })

        elif cmd in ("help", "?"):
            print_help()
            input(c("  (Press Enter to continue)", "dim"))

        else:
            print(c(f"  Unknown command: \"{cmd}\". Type help.", "err"))
            input(c("  (Enter)", "dim"))

    conn.close()


if __name__ == "__main__":
    main()