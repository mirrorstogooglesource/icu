#include "system_collation.h"

// Define U_DISABLE_RENAMING to 1 before including any ICU header to
// disable the symbol name renaming that adds a version- or platform-specific
// suffix to each API C function (e.g. ucol_open_59 instead of ucol_open).
#define U_DISABLE_RENAMING 1

// UCONFIG_NO_COLLATION must be undefined to ensure that ucol.h will properly
// declare all ucol_xxx() functions (and usearch.h all usearch_xxx() ones).
#undef UCONFIG_NO_COLLATION

#include "unicode/ucol.h"
#include "unicode/ucoleitr.h"
#include "unicode/usearch.h"
#include "unicode/uset.h"
#include "unicode/uvernum.h"

// A few sanity checks.
#ifndef U_ICU_VERSION_SUFFIX
#error "Missing U_ICU_VERSION_SUFFIX definition!"
#endif

#ifdef ucol_open
#error "ICU C-based APIs should not be versioned here!"
#endif

#include "logging.h"

// The following entry points are only used by the ICU collation test programms,
// not by Chrome itself.
#define LIST_ICU_ENTRY_POINTS(FUNC, PROC, FUNC_INIT) \
  FUNC(ucol_cloneBinary, int32_t, 4, (const UCollator*, uint8_t*, int32_t, UErrorCode*)) \
  PROC(ucol_closeElements, 1, (UCollationElements*)) \
  FUNC(ucol_equal, UBool, 5, (const UCollator*, const UChar*, int32_t, const UChar*, int32_t)) \
  FUNC(ucol_equals, UBool, 2, (const UCollator*, const UCollator*)) \
  FUNC_INIT(ucol_getBound, int32_t, 7, (const uint8_t*, int32_t, UColBoundMode, uint32_t, uint8_t*, int32_t, UErrorCode*)) \
  PROC(ucol_getContractionsAndExpansions, 5, (const UCollator*, USet*, USet*, UBool, UErrorCode*)) \
  FUNC_INIT(ucol_getDisplayName, int32_t, 5, (const char*, const char*, UChar*, int32_t, UErrorCode*)) \
  FUNC_INIT(ucol_getEquivalentReorderCodes, int32_t, 4, (int32_t, int32_t*, int32_t, UErrorCode*)) \
  FUNC_INIT(ucol_getKeywords, UEnumeration*, 1, (UErrorCode*)) \
  FUNC_INIT(ucol_getKeywordValues, UEnumeration*, 2, (const char*, UErrorCode*)) \
  FUNC_INIT(ucol_getKeywordValuesForLocale, UEnumeration*, 4, (const char*, const char*, UBool, UErrorCode)) \
  FUNC(ucol_getMaxExpansion, int32_t, 2, (const UCollationElements*, int32_t)) \
  FUNC(ucol_getMaxVariable, UColReorderCode, 1, (const UCollator*)) \
  FUNC(ucol_getOffset, int32_t, 1, (const UCollationElements*)) \
  FUNC(ucol_getReorderCodes, int32_t, 4, (const UCollator*, int32_t*, int32_t, UErrorCode*)) \
  FUNC(ucol_getRules, const UChar*, 2, (const UCollator*, int32_t*)) \
  FUNC(ucol_getRulesEx, int32_t, 4, (const UCollator*, UColRuleOption, UChar*, int32_t)) \
  FUNC(ucol_getShortDefinitionString, int32_t, 5, (const UCollator*, const char*, char*, int32_t, UErrorCode*)) \
  PROC(ucol_getUCAVersion, 2, (const UCollator*, UVersionInfo)) \
  FUNC(ucol_getUnsafeSet, int32_t, 3, (const UCollator*, USet*, UErrorCode*)) \
  FUNC(ucol_getVariableTop, int32_t, 2, (const UCollator*, UErrorCode*)) \
  PROC(ucol_getVersion, 2, (const UCollator*, UVersionInfo)) \
  FUNC(ucol_greater, UBool, 5, (const UCollator*, const UChar*, int32_t, const UChar*, int32_t)) \
  FUNC(ucol_greaterOrEqual, UBool, 5, (const UCollator*, const UChar*, int32_t, const UChar*, int32_t)) \
  FUNC_INIT(ucol_keyHashCode, int32_t, 2, (const uint8_t*, int32_t)) \
  FUNC_INIT(ucol_mergeSortkeys, int32_t, 6, (const uint8_t*, int32_t, const uint8_t*, int32_t, uint8_t*, int32_t)) \
  FUNC(ucol_next, int32_t, 2, (UCollationElements*, UErrorCode*)) \
  FUNC(ucol_nextSortKeyPart, int32_t, 6, (const UCollator*, UCharIterator*, uint32_t*, uint8_t*, int32_t, UErrorCode*)) \
  FUNC_INIT(ucol_normalizeShortDefinitionString, int32_t, 5, (const char*, char*, int32_t, UParseError*, UErrorCode*)) \
  FUNC_INIT(ucol_openAvailableLocales, UEnumeration*, 1, (UErrorCode*)) \
  FUNC_INIT(ucol_openBinary, UCollator*, 4, (const uint8_t*, int32_t, const UCollator*, UErrorCode*)) \
  FUNC(ucol_openElements, UCollationElements*, 4, (const UCollator*, const UChar*, int32_t, UErrorCode*)) \
  FUNC_INIT(ucol_openFromShortString, UCollator*, 4, (const char*, UBool, UParseError*, UErrorCode*)) \
  FUNC_INIT(ucol_openRules, UCollator*, 6, (const UChar*, int32_t, UColAttributeValue, UCollationStrength, UParseError*, UErrorCode*)) \
  PROC(ucol_prepareShortStringOpen, 4, (const char*, UBool, UParseError*, UErrorCode*)) \
  FUNC(ucol_previous, int32_t, 2, (UCollationElements*, UErrorCode*)) \
  FUNC_INIT(ucol_primaryOrder, int32_t, 1, (int32_t)) \
  PROC(ucol_reset, 1, (UCollationElements*)) \
  PROC(ucol_restoreVariableTop, 3, (UCollator*, const uint32_t, UErrorCode*)) \
  FUNC(ucol_safeClone, UCollator*, 4, (const UCollator*, void*, int32_t*, UErrorCode*)) \
  FUNC_INIT(ucol_secondaryOrder, int32_t, 1, (int32_t)) \
  PROC(ucol_setMaxVariable, 3, (UCollator*, UColReorderCode, UErrorCode*)) \
  PROC(ucol_setOffset, 3, (UCollationElements*, int32_t, UErrorCode*)) \
  PROC(ucol_setReorderCodes, 4, (UCollator*, const uint32_t*, int32_t, UErrorCode*)) \
  PROC(ucol_setText, 4, (UCollationElements*, const UChar*, int32_t, UErrorCode*)) \
  FUNC(ucol_setVariableTop, uint32_t, 4, (UCollator*, const UChar*, int32_t, UErrorCode*)) \
  FUNC(ucol_strcollIter, UCollationResult, 4, (const UCollator*, UCharIterator*, UCharIterator*, UErrorCode*)) \
  FUNC_INIT(ucol_tertiaryOrder, int32_t, 1, (int32_t)) \
  FUNC(usearch_following, int32_t, 3, (UStringSearch*, int32_t, UErrorCode*)) \
  FUNC(usearch_getAttribute, USearchAttributeValue, 2, (const UStringSearch*, USearchAttribute)) \
  FUNC(usearch_getBreakIterator, const UBreakIterator*, 1, (const UStringSearch*)) \
  FUNC(usearch_getMatchedStart, int32_t, 1, (const UStringSearch*)) \
  FUNC(usearch_getMatchedText, int32_t, 4, (const UStringSearch*, UChar*, int32_t, UErrorCode*)) \
  FUNC(usearch_getOffset, int32_t, 1, (const UStringSearch*)) \
  FUNC(usearch_getPattern, const UChar*, 2, (const UStringSearch*, int32_t*)) \
  FUNC(usearch_getText, const UChar*, 2, (const UStringSearch*, int32_t*)) \
  FUNC(usearch_last, int32_t, 2, (const UStringSearch*, UErrorCode*)) \
  FUNC(usearch_openFromCollator, UStringSearch*, 7, (const UChar*, int32_t, const UChar*, int32_t, const UCollator*, UBreakIterator*, UErrorCode*)) \
  FUNC(usearch_preceding, int32_t, 3, (UStringSearch*, int32_t, UErrorCode*)) \
  FUNC(usearch_previous, int32_t, 2, (const UStringSearch*, UErrorCode*)) \
  PROC(usearch_setAttribute, 4, (UStringSearch*, USearchAttribute, USearchAttributeValue, UErrorCode*)) \
  PROC(usearch_setBreakIterator, 3, (UStringSearch*, UBreakIterator*, UErrorCode*)) \
  PROC(usearch_setCollator, 3, (UStringSearch*, const UCollator*, UErrorCode*)) \

#define SYMBOL_TABLE icu_system_collation::gSymbolsForTests

#define SYMBOL_TABLE_EXPORT 1

#include "system_collation_entries.h"
#include "system_collation_wrappers.h"

// Special case for ucol_getTailoredSet(): This function returns a USet*
// instance created by the system library, but the ICU collation test later
// passed it to the Chromium version of uset_xxx() functions, resulting
// in a runtime crash.
//
// The corresponding test has been manually disabled, but to avoid seeing this
// again, provide an explicit wrapper that will use LOG_FATAL() to abort the
// current program immediately with a human-readable message explaining the
// issue. This will save many hours of debugging in case the problem
// surfaces again!
extern "C" USet* U_ICU_ENTRY_POINT_RENAME(ucol_getTailoredSet)
    (const UCollator* coll, UErrorCode* error) {
  LOG_FATAL("%s: This ICU function cannot be used when system collation is"
      "enabled. For details see third_party/icu/android/system_collation\n",
      __func__);
  (void)coll;
  *error = U_UNSUPPORTED_ERROR;
  return NULL;
}
