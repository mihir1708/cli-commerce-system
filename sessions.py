from datetime import datetime


def start_customer_session(conn, cid):
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(sessionNo), 0) + 1 FROM sessions WHERE cid = ?", (cid,))
    session_no = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO sessions(cid, sessionNo, start_time) VALUES(?,?,?)",
        (cid, session_no, datetime.now().strftime("%Y-%m-%d")),
    )
    conn.commit()
    return session_no


def end_customer_session(conn, cid, session_no):
    cur = conn.cursor()
    cur.execute(
        "UPDATE sessions SET end_time = ? WHERE cid = ? AND sessionNo = ?",
        (datetime.now().strftime("%Y-%m-%d"), cid, session_no),
    )
    conn.commit()


