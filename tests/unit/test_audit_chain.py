from app.core.audit import canonical_event, next_hash, verify_chain, GENESIS

def _rows():
    rows, prev = [], GENESIS
    for i in range(3):
        c = canonical_event("p", f"2026-01-0{i+1}T00:00:00Z", "analyst", "finding", f"f{i}", "create", None, {"x": i})
        h = next_hash(prev, c)
        rows.append({"prev_hash": prev, "hash": h, "canonical": c}); prev = h
    return rows

def test_chain_verifies_and_tamper_fails():
    rows = _rows()
    assert verify_chain(rows) == (True, None)
    rows[1]["canonical"] = rows[1]["canonical"].replace('"x":1', '"x":999')
    ok, bad = verify_chain(rows)
    assert not ok and bad == 1
