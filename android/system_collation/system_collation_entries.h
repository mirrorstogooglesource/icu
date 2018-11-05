// This header is used to define a single icu_system_collation::SymbolTable
// entry. Before including it, you should define two macros:
//
//    SYMBOL_TABLE: The name of the symbol table variable that will be
//                  defined here. The variable will be in the icu_system_icu
//                  namespace.
//
//    SYMBOL_TABLE_EXPORT:
//         Define this to 1 to ensure the symbol table variable is
//         exported from the current compilation unit. Otherwise, it will
//         be 'static'.
//
//    LIST_ICU_ENTRY_POINTS:
//         A macro used to list the ICU entry points, and that takes
//         three parameters, each one of them being a macro that takes
//         an unversioned ICU symbol name as its first parameter. See
//         the comments in system_collation_wrappers.h for more details.
//
#pragma once

#ifndef SYMBOL_TABLE
#error "SYMBOL_TABLE must be defined before including this header"
#endif

#ifndef LIST_ICU_ENTRY_POINTS
#error "LIST_ICU_ENTRY_POINTS must be defined before including this header"
#endif

namespace {

// Compute the number of entry points with an enum type.
// I.e. this defines k_ucol_open as the index of the 'ucol_open'
// function pointer inside 'sEntryAddresses' which is declared later.
enum {
#define LIST_NAME(name, ...) k_ ## name,
LIST_ICU_ENTRY_POINTS(LIST_NAME, LIST_NAME, LIST_NAME)
#undef LIST_NAME
  kNumEntries  // Must be last, do not remove.
};

// An array of un-versioned entry names.
// E.g. kEntryNames[k_ucol_open] == "ucol_open"
static const char* const kEntryNames[kNumEntries] = {
#define ENTRY_NAME(name, ...) #name,
LIST_ICU_ENTRY_POINTS(ENTRY_NAME, ENTRY_NAME, ENTRY_NAME)
#undef ENTRY_NAME
};

// Define the function pointer types specific to each entry point.
// They are named Fn_<entry_point>_t.
#define FUNC_PTR_TYPE(name, return_type, num_params, param_types) \
  using Fn_ ## name ## _t = return_type (*) param_types;

#define PROC_PTR_TYPE(name, num_params, param_types) \
  using Fn_ ## name ## _t = void (*) param_types;

LIST_ICU_ENTRY_POINTS(FUNC_PTR_TYPE, PROC_PTR_TYPE, FUNC_PTR_TYPE)
#undef FUNC_PTR_TYPE
#undef PROC_PTR_TYPE

// The table of function pointers to the system ICU library entry points.
icu_system_collation::FunctionPointer sEntryAddresses[kNumEntries];

}  // namespace

#if !SYMBOL_TABLE_EXPORT
static
#endif
const icu_system_collation::SymbolTable SYMBOL_TABLE = {
  static_cast<size_t>(kNumEntries),
  kEntryNames,
  sEntryAddresses,
};

