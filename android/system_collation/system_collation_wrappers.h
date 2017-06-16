// This header is used to generate function wrappers that will be
// called by the Chromium code, and which will redirect to the corresponding
// system ICU entry point through a function pointer.
//
// IMPORTANT: You should have included "system_collation_wrappers.h" before
//            this header!!
//
// For example, something equivalent to:
//
//    UCollator* ucol_open(const char* locale_name, UErrorCode* error) {
//        return (*__ptr_to_system_ucol_open)(locale_name, error);
//    }
//
// Where __ptr_to_system_ucol_open is a global variable that points to the
// equivalent 'ucol_open' symbol from the system ICU library (which may be
// be versioned, or use a platform-specific suffix, see the implementation
// of icu::SystemIcuLoader for all the gory details).
//
// The __ptr_to_system_XXX values are initialized lazily by calling the
// InitializeSystemIcu() function throud a pthread_once() call.
//
// Functions that take a UCollator* or UStringSearch* pointer as parameters
// do not use pthread_once() for performance reasons (see the distinction
// between FUNC and FUNC_INIT below).
//
// The function pointers are actually stored in a global array (s_icu_entries)
// as generic icu::FunctionPointer values, and thus need to be cast to the
// appropriate pointer-to-function type before invoking them. In other words:
//
//    __ptr_to_system_ucol_open
//
// is really:
//    reinterpret_cast<Fn_ucol_open_t>(s_icu_entries[k_ucol_open])
//
// Where:
//    - 'Fn_ucol_open_t' is the UCollator*(*)(const char*, UErrorCode*) type.
//
//    - 'k_ucol_open' is an enum value corresponding to the 'ucol_open' index
//      inside the 's_icu_entries' array.
//

// This macro is used to list all ICU entry points that are going to be wrapped
// by this shim. The |FUNC|, |PROC| and |FUNC_INIT| parameters are themselves
// macros that must accept a certain number of parameters:
//
//   FUNC(name, result_type, num_params, param_type_list)
//      Where |name| is the name of the wrapped ICU function, without any
//      versioning/platform suffix, |result_type| is the type of its result
//      (and must not be 'void', see PROC()), |num_params| is the number of
//      parameters the function takes, while |param_type_list| is a
//      parentheses-enclosed list of function parameter types. For example,
//      a function declared as:
//
//           int32_t foo(Bar* bar, const char* attribute);
//
//      can be wrapped with a line that says:
//
//           FUNC(foo, int32_t, 2, (Bar*, const char*))
//
//      NOTE: |num_params| should always be the number of items in
//            |param_type_list| or a compilation error will happen.
//
//   PROC(name, num_params, param_type_list)
//      Same as FUNC() except that the wrapped function is a procedure, i.e.
//      doesn't return anything (i.e. its result type is 'void').
//
//   FUNC_INIT(name, result_type, num_params, param_type_list)
//      Same as FUNC(), except that the function will try to lazy-initialize
//      the shim by loading the system ICU library through dlopen() and
//      using dlsym() to resolve symbols. This shall only be used for a few
//      functions that can be called without any pointer to an ICU-specific
//      C-based opaque pointer.
//
#pragma once

#ifndef SYMBOL_TABLE
#error "SYMBOL_TABLE must be defined before including this header"
#endif

#ifndef LIST_ICU_ENTRY_POINTS
#error "LIST_ICU_ENTRY_POINTS must be defined before including this header"
#endif

// Set to 1 to enable tracing entry/exit of each wrapper.
#define TRACE 0

#if TRACE
#include "logging.h"
#define LOG_ENTRY(...)  LOG_INFO(__VA_ARGS__)
#else
#define LOG_ENTRY(...)  ((void)0)
#endif

// Enforce expansion of the argument through the pre-processor.
// This is handy when using ## to assemble tokens and macro calls.
#define EXPAND_(x) x

// Each SIGNATURE_XX macro takes a comma-separated list of parameter types,
// and generates a corresponding function signature. These are designed to
// be used with EXPAND_() as in: EXPAND_(SIGNATURE_##num_params param_types)
#define SIGNATURE_0() ()
#define SIGNATURE_1(A)   (A a)
#define SIGNATURE_2(A, B)  (A a, B b)
#define SIGNATURE_3(A, B, C) (A a, B b, C c)
#define SIGNATURE_4(A, B, C, D) (A a, B b, C c, D d)
#define SIGNATURE_5(A, B, C, D, E) (A a, B b, C c, D d, E e)
#define SIGNATURE_6(A, B, C, D, E, F) (A a, B b, C c, D d, E e, F f)
#define SIGNATURE_7(A, B, C, D, E, F, G) (A a, B b, C c, D d, E e, F f, G g)

// Each CALL_XX macro takes a comma-separated list of parameter types,
// and generates the corresponding call parameter list, using the variable
// names introduced by the corresponding SIGNATURE_XX macro. They are also
// designed to be used with EXPAND_().
#define CALL_0() ()
#define CALL_1(A) (a)
#define CALL_2(A, B) (a, b)
#define CALL_3(A, B, C) (a, b, c)
#define CALL_4(A, B, C, D) (a, b, c, d)
#define CALL_5(A, B, C, D, E) (a, b, c, d, e)
#define CALL_6(A, B, C, D, E, F) (a, b, c, d, e, f)
#define CALL_7(A, B, C, D, E, F, G) (a, b, c, d, e, f, g)

// Generate the name of a given wrapper and it parameter signature.
// E.g. WRAPPER_NAME_AND_SIGNATURE(ucol_open, 2, (const char*, UErrorCode*))
//   --> ucol_open_59(const char* a, UErrorCode* b)
#define WRAPPER_NAME_AND_SIGNATURE(name, num_params, param_types) \
  U_ICU_ENTRY_POINT_RENAME(name) EXPAND_(SIGNATURE_##num_params param_types)

// Generate the function declaration of a wrapper.
// E.g. WRAPPER_DECLARATION(ucol_close, void, 1, (UCollator*))
// -->
//   U_STABLE void U_EXPORT2 ucol_close_59(UCollator* a)
#define WRAPPER_DECLARATION(name, return_type, num_params, param_types) \
  U_STABLE return_type U_EXPORT2 WRAPPER_NAME_AND_SIGNATURE(name, num_params, param_types)

// Generate a call to a given wrapped entry through a function pointer call.
// Should only be used inside a block started by WRAPPER_NAME_AND_SIGNATURE.
// E.g. WRAPPED_CALL(ucol_open, 2, (const char*, UErrorCode*))
//  --> reinterpret_cast<Fn_ucol_open_t>(sEntryAddresses[k_ucol_open])(a, b)
#define WRAPPED_CALL(name, num_params, param_types) \
  reinterpret_cast<Fn_ ## name ## _t>(sEntryAddresses[ k_ ## name ])\
      EXPAND_(CALL_##num_params param_types)

// Used to define a simple function wrapper with LIST_ICU_ENTRY_POINTS
// E.g. FUNC_WRAPPER(ucol_open, UCollator*, 2, (const char*, UErrorCode*))
// -->
//   U_STABLE UCollator* U_EXPORT2 ucol_open_59(const char* a, UErrorCode* b) {
//     return reinterpret_cast<Fn_ucol_open_t>(
//         sEntryAddresses[k_ucol_open])(a, b);
//   }
#define FUNC_WRAPPER(name, return_type, num_params, param_types) \
WRAPPER_DECLARATION(name, return_type, num_params, param_types) { \
    LOG_ENTRY("Entering %s", #name); \
    return_type result = WRAPPED_CALL(name, num_params, param_types); \
    LOG_ENTRY("Exiting %s", #name); \
    return result; \
}

// Used to define a simple procedure wrapper with LIST_ICU_ENTRY_POINTS
// E.g. PROC_WRAPPER(ucol_close, 1, (UCollator*))
// -->
//   U_STABLE void U_EXPORT2 ucol_close(UCollator* a) {
//     reinterpret_cast<Fn_ucol_close_t>(
//         sEntryAddresses[k_ucol_close])(a);
//   }
#define PROC_WRAPPER(name, num_params, param_types) \
WRAPPER_DECLARATION(name, void, num_params, param_types) { \
    LOG_ENTRY("Entering %s", #name); \
    WRAPPED_CALL(name, num_params, param_types); \
    LOG_ENTRY("Exiting %s", #name); \
}

// Same as FUNC_WRAPPER() except that this ensures that InitializeSystemIcu()
// was called at least once.
// E.g. FUNC_INIT_WRAPPER(ucol_open, UCollator*, 2, (const char*, UErrorCode*))
// -->
//   U_STABLE UCollator* U_EXPORT2 ucol_open_59(const char* a, UErrorCode* b) {
//     pthread_once(&s_once_control, InitializeSystemIcu);
//     return reinterpret_cast<Fn_ucol_open_t>(
//         sEntryAddresses[k_ucol_open])(a, b);
//   }
#define FUNC_INIT_WRAPPER(name, return_type, num_params, param_types) \
WRAPPER_DECLARATION(name, return_type, num_params, param_types) { \
    LOG_ENTRY("Entering %s", #name); \
    icu_system_collation::DoLazyInit(); \
    return_type result = WRAPPED_CALL(name, num_params, param_types); \
    LOG_ENTRY("Exiting %s", #name); \
    return result; \
}

// Generate all the wrappers.
LIST_ICU_ENTRY_POINTS(FUNC_WRAPPER, PROC_WRAPPER, FUNC_INIT_WRAPPER)

#undef FUNC_WRAPPER
#undef PROC_WRAPPER
#undef FUNC_INIT_WRAPPER
#undef WRAPPED_CALL
#undef WRAPPER_DECLARATION
#undef WRAPPER_NAME_AND_SIGNATURE
