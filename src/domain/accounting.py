# src/domain/accounting.py

"""
Enterprise Credit Risk Engine - Domain Layer: Accounting

This module enforces absolute deterministic precision for all ledger-adjacent 
operations. It strictly bans standard floating-point (float64) types to 
eliminate binary state leakage and rounding corruption.

Financial Theory & Complexity:
- Theory: Ledger operations must be perfectly reversible and immune to IEEE 754 
  floating-point approximation errors. 
- Complexity: O(1) time complexity for instantiation and arithmetic, with a 
  negligible constant-time overhead for Decimal quantization mapping.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any, Union


class FinancialAmount:
    """
    A strictly controlled fixed-precision data type representing monetary values.
    Enforces quantization to two decimal places (0.01) utilizing ROUND_HALF_UP.
    """
    
    _PRECISION_STEP = Decimal("0.01")

    def __init__(self, value: Union[str, int, Decimal, "FinancialAmount"]) -> None:
        """
        Initializes a FinancialAmount, violently rejecting standard floats.
        
        Args:
            value: The monetary amount as a string, integer, Decimal, or FinancialAmount.
            
        Raises:
            TypeError: If a primitive Python float is passed.
            ValueError: If the value cannot be converted to a valid Decimal.
        """
        if isinstance(value, float):
            raise TypeError(
                "CRITICAL OVERRIDE: Primitive 'float' types are strictly banned in the domain layer. "
                f"Received: {value}. Provide a string, integer, or Decimal."
            )
            
        if isinstance(value, FinancialAmount):
            self._amount: Decimal = value._amount
            return

        try:
            raw_decimal = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValueError(f"Cannot cast {value} to a FinancialAmount. Detail: {str(e)}")

        self._amount = raw_decimal.quantize(self._PRECISION_STEP, rounding=ROUND_HALF_UP)

    @property
    def value(self) -> Decimal:
        """Returns the quantized internal Decimal value."""
        return self._amount

    def __add__(self, other: Any) -> "FinancialAmount":
        if not isinstance(other, (FinancialAmount, str, int, Decimal)):
            return NotImplemented
        return FinancialAmount(self._amount + FinancialAmount(other)._amount)

    def __sub__(self, other: Any) -> "FinancialAmount":
        if not isinstance(other, (FinancialAmount, str, int, Decimal)):
            return NotImplemented
        return FinancialAmount(self._amount - FinancialAmount(other)._amount)

    def __mul__(self, multiplier: Union[str, int, Decimal]) -> "FinancialAmount":
        """
        Multiplies the financial amount by a scalar (e.g., a rate or ratio).
        Rejects float multipliers to maintain deterministic output.
        """
        if isinstance(multiplier, float):
            raise TypeError("Multipliers cannot be standard floats.")
        
        scalar = Decimal(multiplier)
        raw_result = self._amount * scalar
        return FinancialAmount(raw_result)

    def __truediv__(self, divisor: Union[str, int, Decimal]) -> "FinancialAmount":
        if isinstance(divisor, float):
            raise TypeError("Divisors cannot be standard floats.")
            
        scalar = Decimal(divisor)
        if scalar == Decimal("0"):
            raise ValueError("Division by zero in financial operation.")
            
        raw_result = self._amount / scalar
        return FinancialAmount(raw_result)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (FinancialAmount, str, int, Decimal)):
            return self._amount == FinancialAmount(other)._amount
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, (FinancialAmount, str, int, Decimal)):
            return self._amount < FinancialAmount(other)._amount
        raise TypeError(f"Cannot compare FinancialAmount with {type(other)}")

    def __le__(self, other: Any) -> bool:
        if isinstance(other, (FinancialAmount, str, int, Decimal)):
            return self._amount <= FinancialAmount(other)._amount
        raise TypeError(f"Cannot compare FinancialAmount with {type(other)}")
        
    def __gt__(self, other: Any) -> bool:
        return not self.__le__(other)
        
    def __ge__(self, other: Any) -> bool:
        return not self.__lt__(other)

    def __repr__(self) -> str:
        return f"FinancialAmount('{self._amount}')"

    def __str__(self) -> str:
        return str(self._amount)