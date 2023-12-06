# pylint: disable=unused-import
# pylint: disable=no-member
# ruff: noqa: F401
import gc
MPY = True
try:
    import machine  # type: ignore
except ModuleNotFoundError:
    MPY = False


class Memory:
    @property
    def free(self):
        return gc.mem_free() if MPY else 0  # type: ignore[attr-defined]

    @property
    def alloc(self):
        return gc.mem_alloc() if MPY else 0  # type: ignore[attr-defined]
