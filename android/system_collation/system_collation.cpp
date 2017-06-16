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
#include "system_icu_loader.h"

#include <assert.h>
#include <pthread.h>
#include <stdlib.h>

// The list of C-based ICU APIs required by Chromium itself.
// Adding new ones should be straightforward. Note that APIs used by unit-tests
// should go into system_collation_for_tests.cpp instead.
//
// NOTE: Try to keep the list in alphabetical order.
#define LIST_ICU_ENTRY_POINTS(FUNC, PROC, FUNC_INIT) \
  PROC(ucol_close, 1, (UCollator*)) \
  FUNC_INIT(ucol_countAvailable, int32_t, 0, ()) \
  FUNC(ucol_getAttribute, UColAttributeValue, 3, (const UCollator*, UColAttribute, UErrorCode*)) \
  FUNC_INIT(ucol_getAvailable, const char*, 1, (int32_t)) \
  FUNC_INIT(ucol_getFunctionalEquivalent, int32_t, 6, (char*, int32_t, const char*, const char*, UBool*, UErrorCode*)) \
  FUNC(ucol_getLocaleByType, const char*, 3, (const UCollator*, ULocDataLocaleType, UErrorCode*)) \
  FUNC(ucol_getSortKey, int32_t, 5, (const UCollator*, const UChar*, int32_t, uint8_t*, int32_t)) \
  FUNC(ucol_getStrength, UCollationStrength, 1, (const UCollator*)) \
  FUNC_INIT(ucol_open, UCollator*, 2, (const char*, UErrorCode*)) \
  PROC(ucol_setAttribute, 4, (UCollator*, UColAttribute, UColAttributeValue, UErrorCode*)) \
  PROC(ucol_setStrength, 2, (UCollator*, UCollationStrength)) \
  FUNC(ucol_strcoll, UCollationResult, 5, (const UCollator*, const UChar*, int32_t, const UChar*, int32_t)) \
  FUNC(ucol_strcollUTF8, UCollationResult, 6, (const UCollator*, const char*, int32_t, const char*, int32_t, UErrorCode*)) \
  PROC(usearch_close, 1, (UStringSearch*)) \
  FUNC(usearch_first, int32_t, 2, (UStringSearch*, UErrorCode*)) \
  FUNC(usearch_getCollator, UCollator*, 1, (const UStringSearch*)) \
  FUNC(usearch_getMatchedLength, int32_t, 1, (const UStringSearch*)) \
  FUNC(usearch_next, int32_t, 2, (UStringSearch*, UErrorCode*)) \
  FUNC_INIT(usearch_open, UStringSearch*, 7, (const UChar*, int32_t, const UChar*, int32_t, const char*, UBreakIterator*, UErrorCode*)) \
  PROC(usearch_reset, 1, (UStringSearch*)) \
  PROC(usearch_setOffset, 3, (UStringSearch*, int32_t, UErrorCode*)) \
  PROC(usearch_setPattern, 4, (UStringSearch*, const UChar*, int32_t, UErrorCode*)) \
  PROC(usearch_setText, 4, (UStringSearch*, const UChar*, int32_t, UErrorCode*)) \

#define SYMBOL_TABLE  sChromeSymbols

// Generate the sChromeSymbols symbol table.
#include "system_collation_entries.h"

namespace icu_system_collation {

namespace {

bool InitSymbolTable(const SymbolTable* table, const SystemIcuLoader* loader) {
  int unresolved = 0;
  for (size_t n = 0; n < table->size; ++n) {
    table->entry_addresses[n] = loader->GetIcuEntryPoint(table->entry_names[n]);
    if (!table->entry_addresses[n]) {
      unresolved++;
    }
  }
  if (unresolved > 0) {
    LOG_ERROR("Could not load system ICU library: %d unresolved symbols",
              unresolved);
  }
  return (unresolved == 0);
}

void InitializeSystemIcu() {
  // NOTE: gSymbolsForTests is a weakly-imported symbol. It will be NULL
  // if the system_collation_for_tests.cpp is not linked into the final
  // executable.
  if (&icu_system_collation::gSymbolsForTests != NULL) {
    // First, ensure all log messages are also sent to stderr.
    icu_system_collation::testing::SendLogToStderr();
  }

  static SystemIcuLoader* loader = nullptr;
  loader = SystemIcuLoader::GetInstance();
  if (!loader) {
    LOG_FATAL("No SystemIcuLoader instance!!?");
  }

  if (&icu_system_collation::gSymbolsForTests != NULL) {
    if (!InitSymbolTable(&gSymbolsForTests, loader)) {
      LOG_FATAL("Could not load system ICU library symbols for tests!");
    }
  }

  if (!InitSymbolTable(&sChromeSymbols, loader)) {
    LOG_FATAL("Could not load system ICU library symbols!");
  }
}

}  // namespace

void DoLazyInit() {
  static pthread_once_t sOnce = PTHREAD_ONCE_INIT;
  pthread_once(&sOnce, InitializeSystemIcu);
}

}  // namespace icu_system_collation

#include "system_collation_wrappers.h"
