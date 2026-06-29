from __future__ import annotations
import time
import tracemalloc
import threading
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.state import State, GOAL_STATE

# Global lock so only one thread uses tracemalloc at a time
# (tracemalloc is process-wide and not thread-safe)
_tracemalloc_lock = threading.Lock()


class SolveResult:
    def __init__(
        self,
        path: List[str],
        expanded_nodes: int,
        generated_nodes: int,
        depth: int,
        execution_time: float,
        memory_mb: float,
        message: str = "",
        success: bool = True,
    ) -> None:
        self.path = path
        self.expanded_nodes = expanded_nodes
        self.generated_nodes = generated_nodes
        self.depth = depth
        self.execution_time = execution_time
        self.memory_mb = memory_mb
        self.message = message
        self.success = success

    @staticmethod
    def failure(
        message: str, time_taken: float = 0.0, memory_mb: float = 0.0
    ) -> "SolveResult":
        return SolveResult(
            path=[],
            expanded_nodes=0,
            generated_nodes=0,
            depth=0,
            execution_time=time_taken,
            memory_mb=memory_mb,
            message=message,
            success=False,
        )

    @staticmethod
    def not_applicable(message: str) -> "SolveResult":
        return SolveResult(
            path=[],
            expanded_nodes=0,
            generated_nodes=0,
            depth=0,
            execution_time=0.0,
            memory_mb=0.0,
            message=message,
            success=False,
        )


class BaseAlgorithm(ABC):
    name: str = "Base"
    category: str = "Search"

    def __init__(self) -> None:
        self._expanded = 0
        self._generated = 0

    def solve(
        self,
        initial: Tuple[int, ...],
        goal: Tuple[int, ...] = GOAL_STATE,
        heuristic: Optional[callable] = None,
    ) -> SolveResult:
        """
        Solve the puzzle and return a SolveResult.
        Thread-safe: uses a lock around tracemalloc so multiple solver
        threads cannot corrupt the memory-tracing state.
        """
        self._expanded = 0
        self._generated = 0

        start_time = time.perf_counter()
        peak_mb = 0.0

        # Use tracemalloc only if we can acquire the lock immediately;
        # otherwise skip memory measurement (avoids cross-thread crashes).
        measure_mem = _tracemalloc_lock.acquire(blocking=False)
        if measure_mem:
            try:
                tracemalloc.start()
            except Exception:
                measure_mem = False
                _tracemalloc_lock.release()

        try:
            result = self._solve(State(board=initial), State(board=goal), heuristic)
        except MemoryError:
            elapsed = time.perf_counter() - start_time
            if measure_mem:
                try:
                    _, peak = tracemalloc.get_traced_memory()
                    peak_mb = peak / 1024 / 1024
                finally:
                    try:
                        tracemalloc.stop()
                    except Exception:
                        pass
                    _tracemalloc_lock.release()
            return SolveResult.failure(
                "Out of memory.", time_taken=elapsed, memory_mb=peak_mb
            )
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            if measure_mem:
                try:
                    tracemalloc.stop()
                except Exception:
                    pass
                _tracemalloc_lock.release()
            return SolveResult.failure(
                f"Algorithm error: {exc}", time_taken=elapsed, memory_mb=0.0
            )

        elapsed = time.perf_counter() - start_time

        if measure_mem:
            try:
                _, peak = tracemalloc.get_traced_memory()
                peak_mb = peak / 1024 / 1024
            except Exception:
                peak_mb = 0.0
            finally:
                try:
                    tracemalloc.stop()
                except Exception:
                    pass
                _tracemalloc_lock.release()

        if result is None:
            return SolveResult.failure(
                "No solution found.", time_taken=elapsed, memory_mb=peak_mb
            )

        return SolveResult(
            path=result.get_path(),
            expanded_nodes=self._expanded,
            generated_nodes=self._generated,
            depth=result.depth,
            execution_time=elapsed,
            memory_mb=peak_mb,
        )

    @abstractmethod
    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[callable],
    ) -> Optional[State]:
        """Internal solve implementation. Returns goal State or None."""
        ...
