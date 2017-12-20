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

static const int32_t gMaxFastInt = 10000;

// Return the number of decimal digits needed to print |value|.
// Results are only guaranteed if |value| in in [0..10000) range.
static int32_t digitCount(int value) {
  return 1 + (value >= 10) + (value >= 100) + (value >= 1000);
}

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
    if (positiveValue >= gMaxFastInt) {
        return range.getMax();
    }
    return range.pin(digitCount(positiveValue));
}

UBool
SmallIntFormatter::canFormat(
        int32_t positiveValue, const IntDigitCountRange &range) {
    return (positiveValue < gMaxFastInt && range.getMin() <= 4);
}

UnicodeString &
SmallIntFormatter::format(
        int32_t smallPositiveValue,
        const IntDigitCountRange &range,
        UnicodeString &appendTo) {
    int32_t digits = range.pin(digitCount(smallPositiveValue));

    // Always emit at least '0'
    if (digits == 0) {
        return appendTo.append((UChar) 0x30);
    }
    // Sanity check
    if (digits > 4) {
        digits = 4;
    }
    // Write up to 4 digits in |chars| array, from the end of the
    // array so that the result doesn't need reversal.
    UChar chars[4];
    for (int n = 0; n < digits; ++n) {
        chars[3 - n] = (UChar)(0x30 + smallPositiveValue % 10);
        smallPositiveValue /= 10;
    }
    return appendTo.append(chars, 4 - digits, digits);
}

U_NAMESPACE_END

