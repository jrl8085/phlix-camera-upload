"""Pairing codes and the brake on guessing them."""

from __future__ import annotations

import hmac
import secrets
import threading
import time
from collections import deque

from .config import normalise_code

#: Letters and digits that cannot be mistaken for one another when read off a
#: screen and typed on a phone: no I, L, O, U, 0 or 1.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTVWXYZ23456789"
CODE_LENGTH = 8


def new_code() -> str:
    """A fresh pairing code such as `K7QM-3XPD`."""
    raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
    return f"{raw[:4]}-{raw[4:]}"


def codes_match(expected: str, offered: str) -> bool:
    """Compare two codes ignoring case, dashes and spaces, in constant time."""
    left, right = normalise_code(expected), normalise_code(offered)
    if not left:
        return False
    return hmac.compare_digest(left.encode("ascii", "ignore"), right.encode("ascii", "ignore"))


class AttemptLimiter:
    """Slows down anyone guessing a pairing code or trying Plex tokens.

    A single address gets a handful of wrong tries a minute, whether it
    guesses the code or offers Plex sign-ins.

    Wrong codes from all addresses together get a much larger allowance,
    after which pairing with the code pauses for everyone. That stops a
    guesser who keeps changing address, and it is set high on purpose: the
    code is long enough that even this many tries, kept up for years, would
    not find it, while a low number would let anyone on the network keep the
    owner from pairing a phone. Pairing through Plex is never paused this
    way, because there is nothing in it to guess.
    """

    def __init__(self, per_address: int = 5, address_window: float = 60.0,
                 overall: int = 200, overall_window: float = 600.0, clock=time.monotonic):
        self._per_address = per_address
        self._address_window = address_window
        self._overall = overall
        self._overall_window = overall_window
        self._clock = clock
        self._lock = threading.Lock()
        self._by_address: dict[str, deque[float]] = {}
        self._all: deque[float] = deque()

    def _trim(self, now: float) -> None:
        while self._all and now - self._all[0] >= self._overall_window:
            self._all.popleft()
        for address in list(self._by_address):
            failures = self._by_address[address]
            while failures and now - failures[0] >= self._address_window:
                failures.popleft()
            if not failures:
                del self._by_address[address]

    def retry_after(self, address: str, by_code: bool = True) -> int:
        """Seconds this address must wait before another try; 0 if it may try now.

        `by_code` says the try is a pairing code, which the pause for
        everyone applies to; a Plex sign-in answers only for its own address.
        """
        now = self._clock()
        with self._lock:
            self._trim(now)
            waits = [0.0]
            if by_code and len(self._all) >= self._overall:
                waits.append(self._overall_window - (now - self._all[0]))
            failures = self._by_address.get(address)
            if failures and len(failures) >= self._per_address:
                waits.append(self._address_window - (now - failures[0]))
        wait = max(waits)
        return int(wait) + 1 if wait > 0 else 0

    def record_failure(self, address: str, by_code: bool = True) -> None:
        now = self._clock()
        with self._lock:
            self._trim(now)
            if by_code:
                self._all.append(now)
            self._by_address.setdefault(address, deque()).append(now)

    def record_success(self, address: str) -> None:
        with self._lock:
            self._by_address.pop(address, None)
