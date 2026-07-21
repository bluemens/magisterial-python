# Cursor pagination. Every /v1 list endpoint returns
# {"data": [...], "next_cursor": "...", "has_more": bool}; pages expose the
# raw fields plus iteration helpers that follow the cursor automatically.

from __future__ import annotations

from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
)

T = TypeVar("T")


class SyncPage(Generic[T]):
    """One page of results. Iterate the page itself for its items, or
    ``auto_paging_iter()`` to walk every page transparently."""

    def __init__(
        self,
        data: List[T],
        next_cursor: Optional[str],
        has_more: bool,
        fetch_next: Callable[[str], "SyncPage[T]"],
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._fetch_next = fetch_next

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return (
            f"SyncPage(data={len(self.data)} items, has_more={self.has_more})"
        )

    def next_page(self) -> Optional["SyncPage[T]"]:
        if not self.has_more or not self.next_cursor:
            return None
        return self._fetch_next(self.next_cursor)

    def auto_paging_iter(self) -> Iterator[T]:
        page: Optional[SyncPage[T]] = self
        while page is not None:
            yield from page.data
            page = page.next_page()


class AsyncPage(Generic[T]):
    """Async counterpart of :class:`SyncPage`."""

    def __init__(
        self,
        data: List[T],
        next_cursor: Optional[str],
        has_more: bool,
        fetch_next: Callable[[str], Awaitable["AsyncPage[T]"]],
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._fetch_next = fetch_next

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return (
            f"AsyncPage(data={len(self.data)} items, has_more={self.has_more})"
        )

    async def next_page(self) -> Optional["AsyncPage[T]"]:
        if not self.has_more or not self.next_cursor:
            return None
        return await self._fetch_next(self.next_cursor)

    async def auto_paging_iter(self) -> AsyncIterator[T]:
        page: Optional[AsyncPage[T]] = self
        while page is not None:
            for item in page.data:
                yield item
            page = await page.next_page()
