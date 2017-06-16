#pragma once

#include <stddef.h>

namespace icu_system_collation {

// Generic FunctionPointer type
using FunctionPointer = void(*)(void);

// A small data structure used to describe a table of ICU entry points.
struct SymbolTable {
    size_t size;
    const char* const* entry_names;
    FunctionPointer* entry_addresses;
};

// Perform lazy initialization of the system ICU library and corresponding
// entry point addresses. Useful for FUNC_INIT entry points (see
// system_collation_wrappers.h for more details).
void DoLazyInit();

// Special symbol that is weakly-imported here. Its value will be nullptr
// unless system_collation_for_tests.cpp is also linked into the final
// executable / library.
extern const SymbolTable gSymbolsForTests __attribute__((weak));

}  // namespace icu_system_collation
