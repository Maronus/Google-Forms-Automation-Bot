#!/usr/bin/env python3
"""
encrypt.py — Obfuscate maronus.py into a single unreadable .py file.

The output file still runs as a normal Python script on any platform
(Windows, Linux, macOS, Termux) but the source code is not visible.

Approach:
  source → XOR with key → zlib compress → base64 encode → loader stub

Usage:
    python encrypt.py                       # creates maronus_dist.py
    python encrypt.py -o my_tool.py         # custom output name
    python encrypt.py -k "my_secret_key"    # custom encryption key
"""

import argparse
import base64
import os
import sys
import zlib


DEFAULT_KEY = b"m@r0nu$_x0r_k3y_2024!_s3cur3"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR data with a repeating key."""
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def encrypt_source(source: str, key: bytes) -> bytes:
    """Encrypt source: encode → XOR → compress → base64."""
    raw = source.encode("utf-8")
    xored = xor_bytes(raw, key)
    compressed = zlib.compress(xored, 9)
    encoded = base64.b64encode(compressed)
    return encoded


def build_loader(payload: bytes, key: bytes) -> str:
    """Build the self-decrypting loader script."""
    key_b64 = base64.b64encode(key).decode("ascii")
    loader = f'''#!/usr/bin/env python3
# maronus — encrypted build (do not edit)
import base64 as _b,zlib as _z
_k=_b.b64decode(b"{key_b64}")
_d=_b.b64decode({payload})
_d=_z.decompress(_d)
_d=bytes(b^_k[i%len(_k)]for i,b in enumerate(_d))
exec(_d.decode("utf-8"))
'''
    return loader


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt maronus.py into an obfuscated Python file"
    )
    parser.add_argument(
        "-i", "--input",
        default="maronus.py",
        help="Input source file (default: maronus.py)",
    )
    parser.add_argument(
        "-o", "--output",
        default="maronus_dist.py",
        help="Output encrypted file (default: maronus_dist.py)",
    )
    parser.add_argument(
        "-k", "--key",
        default=None,
        help="Custom XOR encryption key (default: built-in key)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"  ✗ Input file not found: {args.input}")
        sys.exit(1)

    key = args.key.encode("utf-8") if args.key else DEFAULT_KEY

    with open(args.input, "r", encoding="utf-8") as f:
        source = f.read()

    payload = encrypt_source(source, key)
    loader = build_loader(payload, key)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(loader)

    src_size = len(source)
    out_size = len(loader)

    print()
    print(f"  [OK] Encrypted: {args.input} -> {args.output}")
    print(f"  Source size:  {src_size:,} bytes")
    print(f"  Output size:  {out_size:,} bytes")
    print(f"  Compression:  {out_size / src_size * 100:.0f}%")
    print()
    print(f"  Run with:  python {args.output}")
    print()


if __name__ == "__main__":
    main()
