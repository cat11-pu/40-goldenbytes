"""goldenbytes.py：整数打包（基线：固定四字节，无差分、无重同步）。"""
from __future__ import annotations


class Packer:
    def __init__(self, version: int = 1):
        self.version = version
        self.encoded = 0
        self.decoded = 0

    def pack(self, numbers) -> bytes:
        """基线：每个数固定四字节大端。"""
        self.encoded = len(numbers)
        return b"".join(int(number).to_bytes(4, "big") for number in numbers)

    def unpack(self, blob: bytes) -> list:
        if len(blob) % 4 != 0:
            raise ValueError("truncated")
        values = [int.from_bytes(blob[index:index + 4], "big") for index in range(0, len(blob), 4)]
        self.decoded += len(values)
        return values

    def pack_delta(self, numbers) -> bytes:
        raise NotImplementedError("变长差分编码还没实现")

    def unpack_delta(self, blob: bytes) -> list:
        raise NotImplementedError("变长差分解码还没实现")

    def resync(self, blob: bytes) -> dict:
        raise NotImplementedError("截断重同步还没实现")

    def stats(self) -> dict:
        return {"version": self.version, "encoded": self.encoded, "decoded": self.decoded}
