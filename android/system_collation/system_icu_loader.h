#ifndef USYSTEM_ICU_LOADER_H
#define USYSTEM_ICU_LOADER_H

namespace icu_system_collation {

using FunctionPointer = void(*)(void);

// An abstract interface to load the system version of the ICU library, then
// find ICUC entry points in it. The implementation is subtle due to the way
// the library was configured and installed on the platform.
//
// Usage is simple:
//
//  1) Call SystemIcuLoader::GetInstance() to retrieve the instance.
//
//  2) Call GetIcuEntryPoint() repeatedly on it to find the address of
//     ICU C-based API functions based on their unversioned name.
//
class SystemIcuLoader {
public:
  virtual ~SystemIcuLoader() = default;

  // Return the address of the entry point for the ICU4C function |name|,
  // which should not use any platform or versioning suffix (i.e. should be
  // 'ucol_open' instead of 'ucol_open_59' or 'ucol_open_cr'. Return the
  // entry point's address if any, of nullptr if not found.
  virtual FunctionPointer GetIcuEntryPoint(const char* name) const = 0;

  // Return the singleton instance for this process. This tries to locate
  // the system ICU library, and the corresponding version suffix that is
  // applied to its entry points, initialize it, then return a pointer to the
  // corresponding instance on success. will be nullptr if the library cannot
  // be located or initialized properly.
  static SystemIcuLoader* GetInstance();
};

}  // namespace icu_system_collation

#endif
