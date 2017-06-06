// Define U_DISABLE_RENAMING to 1 before including any ICU header to
// disable the symbol name renaming that adds a version- or platform-specific
// suffix to each API C function (e.g. ucol_open_59 instead of ucol_open).
#define U_DISABLE_RENAMING 1

// UCONFIG_NO_COLLATION must be undefined to ensure that ucol.h will properly
// declare all ucol_xxx() functions (and usearch.h all usearch_xxx() ones).
#undef UCONFIG_NO_COLLATION

#include "unicode/ucol.h"
#include "unicode/usearch.h"
#include "unicode/uvernum.h"

// A few sanity checks.
#ifndef U_ICU_VERSION_SUFFIX
#error "Missing U_ICU_VERSION_SUFFIX definition!"
#endif

#ifdef ucol_open
#error "ICU C-based APIs should not be versioned here!"
#endif

#include "system_icu_loader.h"

#include <assert.h>
#include <pthread.h>

// Set to 1 to enable traces during development / debugging.
#define TRACE  0

#if TRACE
#include <android/log.h>
#define LOG(...) \
    __android_log_print(ANDROID_LOG_INFO, "SystemCollation", __VA_ARGS__)
#else
#define LOG(...) ((void)0)
#endif

// The following macros are used to generate function wrappers that will be
// called by the Chromium code, and which will redirect to the corresponding
// system ICU entry point through a function pointer.
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
// IMPORTANT: At the moment, only the APIs required by Chromium are listed
//            here, but adding new ones should be straightforward.
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

namespace {

// Compute the number of entry points with an enum type.
// I.e. this defines k_ucol_open as the index of the 'ucol_open'
// function pointer inside 's_icu_entries' which is declared later.
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

using icu::FunctionPointer;
using icu::SystemIcuLoader;

// The table of function pointers to the system ICU library entry points.
FunctionPointer s_icu_entries[kNumEntries];

void InitializeSystemIcu() {
  static SystemIcuLoader* loader = nullptr;
  loader = SystemIcuLoader::CreateInstance();
  assert(loader);

  // Populate s_icu_entries now.
  for (int n = 0; n < kNumEntries; ++n) {
    s_icu_entries[n] = loader->GetIcuEntryPoint(kEntryNames[n]);
  }
}

// The pthread_once_t instance used to lazily initialize the function
// pointers.
pthread_once_t s_once_control = PTHREAD_ONCE_INIT;

}  // namespace

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
//  --> reinterpret_cast<Fn_ucol_open_t>(s_icu_entries[k_ucol_open])(a, b)
#define WRAPPED_CALL(name, num_params, param_types) \
  reinterpret_cast<Fn_ ## name ## _t>(s_icu_entries[ k_ ## name ])\
      EXPAND_(CALL_##num_params param_types)

// Used to define a simple function wrapper with LIST_ICU_ENTRY_POINTS
// E.g. FUNC_WRAPPER(ucol_open, UCollator*, 2, (const char*, UErrorCode*))
// -->
//   U_STABLE UCollator* U_EXPORT2 ucol_open_59(const char* a, UErrorCode* b) {
//     return reinterpret_cast<Fn_ucol_open_t>(
//         s_icu_entries[k_ucol_open])(a, b);
//   }
#define FUNC_WRAPPER(name, return_type, num_params, param_types) \
WRAPPER_DECLARATION(name, return_type, num_params, param_types) { \
    LOG("Entering %s", #name); \
    return_type result = WRAPPED_CALL(name, num_params, param_types); \
    LOG("Exiting %s", #name); \
    return result; \
}

// Used to define a simple procedure wrapper with LIST_ICU_ENTRY_POINTS
// E.g. PROC_WRAPPER(ucol_close, 1, (UCollator*))
// -->
//   U_STABLE void U_EXPORT2 ucol_close(UCollator* a) {
//     reinterpret_cast<Fn_ucol_close_t>(
//         s_icu_entries[k_ucol_close])(a);
//   }
#define PROC_WRAPPER(name, num_params, param_types) \
WRAPPER_DECLARATION(name, void, num_params, param_types) { \
    LOG("Entering %s", #name); \
    WRAPPED_CALL(name, num_params, param_types); \
    LOG("Exiting %s", #name); \
}

// Same as FUNC_WRAPPER() except that this ensures that InitializeSystemIcu()
// was called at least once.
// E.g. FUNC_INIT_WRAPPER(ucol_open, UCollator*, 2, (const char*, UErrorCode*))
// -->
//   U_STABLE UCollator* U_EXPORT2 ucol_open_59(const char* a, UErrorCode* b) {
//     pthread_once(&s_once_control, InitializeSystemIcu);
//     return reinterpret_cast<Fn_ucol_open_t>(
//         s_icu_entries[k_ucol_open])(a, b);
//   }
#define FUNC_INIT_WRAPPER(name, return_type, num_params, param_types) \
WRAPPER_DECLARATION(name, return_type, num_params, param_types) { \
    LOG("Entering %s", #name); \
    pthread_once(&s_once_control, InitializeSystemIcu); \
    return_type result = WRAPPED_CALL(name, num_params, param_types); \
    LOG("Exiting %s", #name); \
    return result; \
}

// All exported wrapper are C functions
extern "C" {

// Generate all the wrappers.
LIST_ICU_ENTRY_POINTS(FUNC_WRAPPER, PROC_WRAPPER, FUNC_INIT_WRAPPER)

}  // extern "C"

#undef FUNC_WRAPPER
#undef PROC_WRAPPER
#undef FUNC_INIT_WRAPPER
