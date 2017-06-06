#include "system_icu_loader.h"

#include <android/log.h>

#include <dirent.h>
#include <dlfcn.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

namespace icu {

namespace {

// Generic and specialized logging functions.
void LogGeneric(android_LogPriority prio, const char* fmt, va_list args) {
  __android_log_vprint(prio, "IcuSystemLoader", fmt, args);
}

void LogInfo(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  LogGeneric(ANDROID_LOG_INFO, fmt, args);
  va_end(args);
}

void LogError(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  LogGeneric(ANDROID_LOG_ERROR, fmt, args);
  va_end(args);
}

void LogFatal(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  LogGeneric(ANDROID_LOG_FATAL, fmt, args);
  va_end(args);
}

// An Android-specific implementation of the SystemIcuLoader interface.
//
// On Android, the system ICU library is implemented by the following
// native shared libraries: libicuuc.so and libicui18n.so, which are
// typically stored under /system/lib (though other paths are possible
// on mixed 32/64 systems).
//
// Since Android N (API level 24), dlopen() will only open a small
// set of system libraries corresponding to the native public APIs
// exposed by the NDK. There is however a "grey list" of system libraries
// that still work with dlopen(), though the NDK doesn't provide
// headers / link-time libraries for them.
//
// libicuuc.so and libi18n.so are part of the grey list, because many
// important third-party applications rely on them (due to their size),
// and the Android system team has decided to continue supporting this
// in the future, through the use of a special helper static library
// that must be linked into the third-party application code.
//
// However, this helper re-implements *all* of ICU C entry points, and
// using it for Chromium would result in link-time conflicts.
//
// The code in system_collation.cpp is essentially a small re-implementation
// of the same idea, but that only exposes / redirects collation-related APIs.
//
// The AndroidSystemIcuLoader handles the gory detail of finding the
// libraries and the right entry points in it.
//
// All symbols exported by the library use a version-specific prefix
// (e.g. ucol_open_55 instead of ucol_open), and there are plans to
// change this to a platform-specific one (e.g. ucol_open_android)
// in the future.
//
// Finding the right suffix is performed by the Init() method.
// It will be used by GetIcuEntryPoint() to append the suffix when
// using ::dlsym() to find its corresponding address.
//
class AndroidSystemIcuLoader : public SystemIcuLoader {
 public:
  // Destructor.
  virtual ~AndroidSystemIcuLoader() {
    if (handle_i18n_) {
      ::dlclose(handle_i18n_);
    }
    if (handle_common_) {
      ::dlclose(handle_common_);
    }
  }

  // Try to load the system library and find the corresponding
  // version- or platform-specific suffix. Return true on success,
  // false otherwise.
  bool Init() {
    handle_common_ = ::dlopen("libicuuc.so", RTLD_LOCAL);
    if (!handle_common_) {
      LogError("Could not open system ICU common library: %s", dlerror());
      return false;
    }

    handle_i18n_ = ::dlopen("libicui18n.so", RTLD_LOCAL);
    if (!handle_i18n_) {
      LogError("Could not open system ICU i18n library: %s", dlerror());
      return false;
    }

    // If 'ucol_open_android' is defined, then the library uses a
    // platform-specific suffix of "_android".
    if (::dlsym(handle_i18n_, "ucol_open_android") != nullptr) {
      LogInfo("System ICU library uses the _android suffix!");
      strlcpy(icu_suffix_, "android", sizeof(icu_suffix_));
      return true;
    }

    // Otherwise, look for the data file and extract the version number
    // from its name.
    return FindIcuDataFileVersion();
  }

  virtual FunctionPointer GetIcuEntryPoint(const char* name) const override {
    if (!handle_i18n_) {
      LogFatal("Missing system ICU library!?");
    }

    // Append system suffix to symbol name before calling ::dlsym().
    char symbol[128];
    ::snprintf(symbol, sizeof(symbol), "%s_%s", name, icu_suffix_);
    FunctionPointer func = reinterpret_cast<FunctionPointer>(
        ::dlsym(handle_i18n_, symbol));
    if (!func) {
      LogError("Could not find symbol %s in system ICU library",
               symbol);
    }
    return func;
  }

 private:
  // Allow 2- or 3-digit version numbers.
  static constexpr int kIcuDataVersionMinLength = 2;
  static constexpr int kIcuDataVersionMaxLength = 3;

  // Don't allow any older version of the ICU data file.
  static constexpr int kIcuDataVersionMin = 44;

  // The ICU data file has a name like "icudt<version>l.dat"
  // Separate it into a prefix and suffix for comparisons.

  // NOTE: Using 'static const char [] here doesn't compile.
  // Using static constexpr char [] compiles but does not link !?
  // so use macros instead.
#define kDataPrefix "icudt"
#define kDataSuffix "l.dat"
//   static constexpr char kDataPrefix[] = "icudt";
//   static constexpr char kDataSuffix[] = "l.dat";

  static const int kDataPrefixLen = sizeof(kDataPrefix) - 1;
  static const int kDataSuffixLen = sizeof(kDataSuffix) - 1;

  // Returns 1 if |dirp| points to a file whose name matches the expected
  // name of an ICU data file. 0 otherwise. Passed as a callback to scandir().
  static int filterIcuDataFileName(const struct dirent* dirp) {
    const char* name = dirp->d_name;
    const int len = ::strlen(name);

    // Size of the ICU data file name without the embedded version number.
    // The generic format is 'icudt<version>l.dat', where <version> can be
    // a 2 or 3 digit version number.
    if (len < kDataPrefixLen + kDataSuffixLen + kIcuDataVersionMinLength ||
        len > kDataPrefixLen + kDataSuffixLen + kIcuDataVersionMaxLength) {
      return 0;
    }

    for (int i = kDataPrefixLen; i < len - kDataSuffixLen; ++i) {
      if (name[i] < '0' || name[i] > '9') {
        return 0;
      }
    }

    return !::strncmp(name, kDataPrefix, kDataPrefixLen) &&
           !::strncmp(name + len - kDataSuffixLen, kDataSuffix, kDataSuffixLen);
  }

  // Find the version of the system ICU library, and store it as a character
  // string in icu_suffix_[]. Return true on success, false otherwise.
  bool FindIcuDataFileVersion() {
    // Scan /system/usr/icu for ICU data files, and record the maximum
    // version found there.
    struct dirent** namelist = nullptr;
    int n = ::scandir("/system/usr/icu", &namelist, &filterIcuDataFileName,
                      ::alphasort);
    int max_version = -1;
    while (n--) {
      char* name = namelist[n]->d_name;
      const int len = ::strlen(name);
      const char* verp = &name[kDataPrefixLen];
      name[len - kDataSuffixLen] = '\0';

      char* endptr;
      int ver = (int)strtol(verp, &endptr, 10);

      // Use the latest version available.
      if (ver > max_version) {
        max_version = ver;
        strlcpy(icu_suffix_, verp, sizeof(icu_suffix_));
      }
      free(namelist[n]);
    }
    free(namelist);

    if (max_version < 0) {
      LogError("Could not find versioned system ICU data file!");
      return false;
    }
    if (max_version < kIcuDataVersionMin) {
      LogError("System ICU data file version is too old: %d"
               " (expected >= %d)", max_version, kIcuDataVersionMin);
      return false;
    }
    LogInfo("Found ICU data file version %d", max_version);
    return true;
  }

  void* handle_common_;
  void* handle_i18n_;
  char icu_suffix_[32];
};

}  // namespace

// static
SystemIcuLoader* SystemIcuLoader::CreateInstance() {
  AndroidSystemIcuLoader* loader = new AndroidSystemIcuLoader();
  if (!loader->Init()) {
    delete loader;
    return nullptr;
  }
  return loader;
}

}  // namespace icu
