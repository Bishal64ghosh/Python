#!/usr/bin/env python3
"""
Exploit: "The Twitching Patient" CTF
Vulnerability: Biased ECDSA nonce (k uses only 30 bytes = 240 bits)
Attack: Hidden Number Problem via LLL lattice reduction
Dependency: sympy (pip install sympy)

Run: python3 exploit_twitching_patient.py
"""

import hashlib
import socket
import time
from sympy import Matrix

HOST = "40.81.29.254"
PORT = 8073
ORDER  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
BIT_LENGTH = 256
NUM_SIGS = 25   # Only need ~20-25 signatures for reliable recovery


def modinv(a, m):
    return pow(a, -1, m)


# ── Collect signatures from server ───────────────────────────────────────────

def collect_signatures(n=NUM_SIGS):
    print(f"[*] Connecting to {HOST}:{PORT} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.settimeout(15)

    buf = b""
    def readline():
        nonlocal buf
        while b"\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("disconnected")
            buf += chunk
        line, buf = buf.split(b"\n", 1)
        return line.decode(errors="replace").strip()

    # Read banner until we see the prompt
    for _ in range(25):
        line = readline()
        print(" ", line)
        if line.startswith(">"):
            break

    signatures = []
    for i in range(n):
        msg = f"form_{i:05d}".encode()
        msg_hex = msg.hex()
        z = int.from_bytes(hashlib.sha256(msg).digest(), "big")

        sock.sendall(f"SIGN {msg_hex}\n".encode())

        # Read: "Form #N signed.\nr = ...\ns = ...\n> "
        l1 = readline()  # "Form #N signed."
        l2 = readline()  # "r = ..."
        l3 = readline()  # "s = ..."
        try: readline()  # prompt ">"
        except: pass

        r = int(l2.split("=")[1].strip())
        s = int(l3.split("=")[1].strip())
        signatures.append((z, r, s))

        if (i + 1) % 5 == 0:
            print(f"[+] {i+1}/{n} signatures collected")

    sock.sendall(b"EXIT\n")
    sock.close()
    return signatures


# ── Lattice attack (HNP via BV construction) ──────────────────────────────────

def attack(signatures):
    """
    ECDSA biased-nonce attack.

    Since k = int.from_bytes(v[:30], 'big') % n and v is SHA-256 output,
    we have k < 2^240 << n ~ 2^256.

    From s*k ≡ z + r*d (mod n):
        k ≡ s⁻¹z + s⁻¹r·d  (mod n)
        k = u_i + t_i·d + a_i·n  for some integer a_i

    Since k < 2^240, we build the lattice:

        B = | n  0  … 0  0  0 |  ← m rows
            | 0  n  … 0  0  0 |
            |        …        |
            | t₁ t₂ … tₘ 1  0 |  ← encodes d
            | u₁ u₂ … uₘ 0  n |  ← encodes bias offset

    A short vector in the LLL-reduced lattice has the form:
        (k₁-u₁, k₂-u₂, …, kₘ-uₘ, d, -1) scaled appropriately.
    The m-th entry (0-indexed) gives ±d mod n.
    """
    n = ORDER
    m = len(signatures)

    ts, us = [], []
    for (z, r, s) in signatures:
        sinv = modinv(s, n)
        ts.append(sinv * r % n)
        us.append(sinv * z % n)

    # Build (m+2) × (m+2) matrix
    rows = []
    for i in range(m):
        row = [0] * (m + 2)
        row[i] = n
        rows.append(row)
    rows.append(ts + [1, 0])
    rows.append(us + [0, n])

    print(f"[*] Running LLL on {m+2}×{m+2} lattice ...")
    t0 = time.time()
    L = Matrix(rows).lll()
    print(f"[*] LLL done in {time.time()-t0:.1f}s")

    # Extract d candidates from column m of each row
    candidates = set()
    for i in range(L.shape[0]):
        val = int(L[i, m])
        candidates.add(val % n)
        candidates.add((-val) % n)

    return candidates


def verify(d_cand, signatures):
    """Check that d_cand produces nonces all < 2^240."""
    n = ORDER
    K = 2**240
    for (z, r, s) in signatures[:5]:
        sinv = modinv(s, n)
        k = sinv * (z + r * d_cand) % n
        if k >= K:
            return False
    return True


def to_flag(d_int):
    """Integer → bytes, try to decode as ASCII flag."""
    length = (d_int.bit_length() + 7) // 8
    try:
        return d_int.to_bytes(length, "big")
    except Exception:
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    sigs = collect_signatures(NUM_SIGS)
    print(f"\n[*] Attacking with {len(sigs)} signatures ...")

    candidates = attack(sigs)
    print(f"[*] Checking {len(candidates)} d candidates ...")

    for d_cand in candidates:
        if d_cand == 0:
            continue
        if verify(d_cand, sigs):
            flag_bytes = to_flag(d_cand)
            if flag_bytes:
                print(f"\n[!!!] PRIVATE KEY (d) = {d_cand}")
                print(f"[!!!] FLAG (hex)       = {flag_bytes.hex()}")
                try:
                    print(f"[!!!] FLAG            = {flag_bytes.decode()}")
                except Exception:
                    print(f"[!!!] FLAG (bytes)    = {flag_bytes}")
                return

    print("[-] No flag found — try increasing NUM_SIGS or re-running.")


if __name__ == "__main__":
    main()