#ifndef USYSTEM_COLLATION_COLLATOR_H
#define USYSTEM_COLLATION_COLLATOR_H

// This header should be automatically included from i18n/unicode/coll.h
// when UCONFIG_SYSTEM_COLLATION is enabled. It provides an icu::Collator
// implementations that wraps an opaque C-based UCollator pointer.
// The implementation also uses the corresponding ucol_xxx() functions
// from the C API.
//
// NOTE: This is not a full re-implementation of icu::Collator, since
//       it only provides the methods required by the Chromium and
//       V8 source code.
//
// For more information, see android/system_collation/README

#include "unicode/ucol.h"
#include "unicode/locid.h"
#include "unicode/uversion.h"
#include "unicode/unistr.h"

#include <string>

#include <memory>
#include <string>
#include <stdint.h>

struct UCollator;

U_NAMESPACE_BEGIN

class U_I18N_API Collator {
public:
  // These definitions must match the ones from unicode/coll.h
  enum ECollationStrength {
    DEFAULT = UCOL_DEFAULT,
    PRIMARY = UCOL_PRIMARY,
    SECONDARY = UCOL_SECONDARY,
    TERTIARY = UCOL_TERTIARY,
    QUATERNARY = UCOL_QUATERNARY,
    IDENTICAL = UCOL_IDENTICAL,
  };

  // No default-construction. Use createInstance() instead.
  Collator() = delete;

  // No copy operations.
  Collator(const Collator&) = delete;
  Collator& operator=(const Collator&) = delete;

  // Move operations are supported.
  Collator(Collator&& other) = default;
  Collator& operator=(Collator&& other) = default;

  ~Collator();

  // Create an instance using the root locale.
  static Collator* createInstance(UErrorCode& error);

  // Create an instance from a specific locale.
  static Collator* createInstance(const icu::Locale& locale,
                                  UErrorCode& error);

  // Set the collation strength for this instance.
  void setStrength(ECollationStrength newStrength);

  UCollationResult compare(const UnicodeString& a,
                           const UnicodeString& b,
                           UErrorCode& error) const;

  // Compare two utf-16 strings, identified by |a| and |b|, with lengths
  // |a_len| and |b_len| in UChar units. |error| receives an error
  // on exit, and return the collation result.
  UCollationResult compare(const char16_t* a, int32_t a_len,
                           const char16_t* b, int32_t b_len) const;

  // Compare two utf-8 strings, identified by |a| and |b|. |error| receives
  // an error on exit, and return the collation result.
  UCollationResult compareUTF8(const std::string& a, const std::string& b,
                               UErrorCode& error) const;

  // Get the sort key as an array of bytes from a UnicodeString.
  int32_t getSortKey(const icu::UnicodeString& source, uint8_t* result,
                     int32_t resultLength) const;

  // Get the sort key as an array of bytes from a char16_t buffer.
  int32_t getSortKey(const char16_t* source, int32_t sourceLength,
                     uint8_t* result, int32_t resultLength) const;

  // Universal attribute setter.
  void setAttribute(UColAttribute attr, UColAttributeValue value,
                    UErrorCode& error);

  UColAttributeValue getAttribute(UColAttribute attr, UErrorCode& error) const;

  // Not part of icu::Collator method, but used by helper functions below.
  static Collator* createInstanceFromLocaleName(const char* locale,
                                                   UErrorCode& error);

  // Get the set of Locales for which Collations are installed.
  static const Locale* getAvailableLocales(int32_t& count);

  // For testing only.
  std::string getValidLocaleNameForTesting() const;

private:
  // hidden explicit constructor.
  explicit Collator(UCollator* collator) : collator_(collator) {}

  UCollator* collator_;
};

U_NAMESPACE_END

#endif  // USYSTEM_COLLATION_COLLATOR_H
