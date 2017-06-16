#include "system_icu_loader.h"

#include "unicode/utypes.h"

#include "logging.h"

#include <string>

#include <dirent.h>
#include <dlfcn.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Set to 1 to enable debug traces.
#define DEBUG 0

#define DBG(...)  LOG_IF(DEBUG, __VA_ARGS__)

namespace icu_system_collation {

namespace {

// A helper class used to temporarily undefine a given environment variable,
// and restore its definition (if any), on scope exit.
class ScopedEnvironmentVariable {
public:
  ScopedEnvironmentVariable(const char* name) : name_(name), value_() {
    const char* env = getenv(name);
    if (env && env[0] != '\0') {
      DBG("Undefining env variable %s = [%s]", name_, env);
      value_ = env;
    } else {
      DBG("Env variable %s is not defined", name_);
    }
  }

  void undefine() {
    DBG("Undefining env variable %s", name_);
    unsetenv(name_);
  }

  void reset(const char* newValue) {
    DBG("Resetting env variable %s to [%s]", name_, newValue);
    setenv(name_, newValue, 1);
  }

  ~ScopedEnvironmentVariable() {
    if (!value_.empty()) {
      DBG("Restoring env variable %s to [%s]", name_, value_.c_str());
      setenv(name_, value_.c_str(), 1);
    } else {
      DBG("Restoring env variable %s to undefined", name_);
      unsetenv(name_);
    }
  }

private:
  const char* name_;
  std::string value_;
};

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
  // Default constructor.
  AndroidSystemIcuLoader() : valid_(Init()) {}

  // Destructor.
  virtual ~AndroidSystemIcuLoader() {
    if (handle_i18n_) {
      ::dlclose(handle_i18n_);
    }
    if (handle_common_) {
      ::dlclose(handle_common_);
    }
  }

  // Returns true if this instance is valid, i.e. if the system library
  // was located and initialized properly.
  bool valid() const { return valid_; }

  // Try to load the system library and find the corresponding
  // version- or platform-specific suffix. Return true on success,
  // false otherwise.
  bool Init() {
    handle_common_ = ::dlopen("libicuuc.so", RTLD_LOCAL);
    if (!handle_common_) {
      LOG_ERROR("Could not open system ICU common library: %s", dlerror());
      return false;
    }

    handle_i18n_ = ::dlopen("libicui18n.so", RTLD_LOCAL);
    if (!handle_i18n_) {
      LOG_ERROR("Could not open system ICU i18n library: %s", dlerror());
      return false;
    }

    // If 'ucol_open_android' is defined, then the library uses a
    // platform-specific suffix of "_android".
    if (::dlsym(handle_i18n_, "ucol_open_android") != nullptr) {
      LOG_VERBOSE("System ICU library uses the _android suffix!");
      strlcpy(icu_suffix_, "android", sizeof(icu_suffix_));
    } else {
      // Otherwise, look for the data file and extract the version number
      // from its name.
      if (!FindIcuDataFileVersion()) {
        return false;
      }
    }

    // When this code is run from a stand-alone executable (e.g. a unit-test
    // program), we need to force-initialize the system ICU library here.
    // This requires setting ICU_DATA temporarily to /system/usr/icu, then
    // calling the 'u_init()' function.
    //
    // ICU_DATA should be restored to its previous value after that, to ensure
    // that the Chromium ICU library can be initialized properly after this
    // function run.
    //
    // Note that all of this is not necessary when running from a regular
    // Android application process, because it was started by forking a Zygote
    // process that already has the system ICU library initialized.
    ScopedEnvironmentVariable icu_data("ICU_DATA");
    icu_data.reset("/system/usr/icu");

    FunctionPointer func = GetIcuEntryPoint("u_init");
    if (!func) {
      LOG_ERROR("Cannot find u_init() function from system library!");
      return false;
    }

    auto u_init_ptr = reinterpret_cast<void(*)(UErrorCode*)>(func);
    UErrorCode error = U_ZERO_ERROR;
    (*u_init_ptr)(&error);
    if (U_FAILURE(error)) {
      LOG_ERROR("Could not initialize system ICU library: %d", error);
      return false;
    }

    LOG_VERBOSE("System ICU library initialized");
    return true;
  }

  virtual FunctionPointer GetIcuEntryPoint(const char* name) const override {
    if (!handle_i18n_) {
      LOG_FATAL("Missing system ICU library!?");
    }

    // Append system suffix to symbol name before calling ::dlsym().
    char symbol[128];
    ::snprintf(symbol, sizeof(symbol), "%s_%s", name, icu_suffix_);
    FunctionPointer func = reinterpret_cast<FunctionPointer>(
        ::dlsym(handle_i18n_, symbol));
    if (!func) {
      LOG_ERROR("Could not find symbol %s in system ICU library", symbol);
    }
    DBG("Found %s entry as %s at %p", name, symbol, func);
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
      LOG_ERROR("Could not find versioned system ICU data file!");
      return false;
    }
    if (max_version < kIcuDataVersionMin) {
      LOG_ERROR("System ICU data file version is too old: %d"
               " (expected >= %d)", max_version, kIcuDataVersionMin);
      return false;
    }
    LOG_VERBOSE("Found ICU data file version %d", max_version);
    return true;
  }

  void* handle_common_ = nullptr;
  void* handle_i18n_ = nullptr;
  bool valid_ = false;
  char icu_suffix_[32];
};

}  // namespace

// static
SystemIcuLoader* SystemIcuLoader::GetInstance() {
  static AndroidSystemIcuLoader* sLoader = new AndroidSystemIcuLoader();
  if (!sLoader->valid()) {
    return nullptr;
  }
  return sLoader;
}

}  // namespace icu_system_collation
