// © 2016 and later: Unicode, Inc. and others.
// License & terms of use: http://www.unicode.org/copyright.html
/*
 * Copyright (C) 2015, International Business Machines
 * Corporation and others.  All Rights Reserved.
 *
 * file name: smallintformatter.cpp
 */

#include "unicode/unistr.h"

#include "smallintformatter.h"

// Maximal number of decimal digits that can be generated by the ::format()
// method below.
static constexpr int kMaxDigits = 6;

// The corresponding decimal limit, anything greater or equal than this
// value cannot be fast-formatted. Must be 10^kMaxDigits.
static constexpr int32_t kMaxFastInt = 1000000;

// Return the number of decimal digits needed to print |value|.
// Results are only guaranteed if |value| in in [0..kMaxFastInt) range.
static constexpr int digitCount(int32_t value) {
  if (value >= 1000) {
    return 4 + (value >= 10000) + (value >= 100000);
  } else {
    return 1 + (value >= 10) + (value >= 100);
  }
}

static_assert(digitCount(0) == 1, "digitCount() is invalid");
static_assert(digitCount(1) == 1, "digitCount() is invalid");
static_assert(digitCount(9) == 1, "digitCount() is invalid");
static_assert(digitCount(10) == 2, "digitCount() is invalid");
static_assert(digitCount(99) == 2, "digitCount() is invalid");
static_assert(digitCount(100) == 3, "digitCount() is invalid");
static_assert(digitCount(999) == 3, "digitCount() is invalid");
static_assert(digitCount(1000) == 4, "digitCount() is invalid");
static_assert(digitCount(9999) == 4, "digitCount() is invalid");
static_assert(digitCount(10000) == 5, "digitCount() is invalid");
static_assert(digitCount(99999) == 5, "digitCount() is invalid");
static_assert(digitCount(100000) == 6, "digitCount() is invalid");
static_assert(digitCount(999999) == 6, "digitCount() is invalid");

U_NAMESPACE_BEGIN


IntDigitCountRange::IntDigitCountRange(int32_t min, int32_t max) {
    fMin = min < 0 ? 0 : min;
    fMax = max < fMin ? fMin : max;
}

int32_t
IntDigitCountRange::pin(int32_t digitCount) const {
    return digitCount < fMin ? fMin : (digitCount < fMax ? digitCount : fMax);
}

int32_t
SmallIntFormatter::estimateDigitCount(
        int32_t positiveValue, const IntDigitCountRange &range) {
    if (positiveValue >= kMaxFastInt) {
        return range.getMax();
    }
    return range.pin(digitCount(positiveValue));
}

UBool
SmallIntFormatter::canFormat(
        int32_t positiveValue, const IntDigitCountRange &range) {
    return (positiveValue < kMaxFastInt && range.getMin() <= kMaxDigits);
}

UnicodeString &
SmallIntFormatter::format(
        int32_t smallPositiveValue,
        const IntDigitCountRange &range,
        UnicodeString &appendTo) {
    int digits = range.pin(digitCount(smallPositiveValue));

    // Always emit at least '0'
    if (digits == 0) {
        return appendTo.append((UChar) 0x30);
    }
    // Sanity check
    if (digits > kMaxDigits) {
        digits = kMaxDigits;
    }
    // Write up to kMaxDigits digits in |chars| array, from the end of the
    // array so that the result doesn't need reversal.
    UChar chars[kMaxDigits];
    for (int n = 0; n < digits; ++n) {
        chars[kMaxDigits - 1 - n] = (UChar)(0x30 + smallPositiveValue % 10);
        smallPositiveValue /= 10;
    }
    return appendTo.append(chars, kMaxDigits - digits, digits);
}

U_NAMESPACE_END

