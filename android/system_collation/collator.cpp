// Undefined UCONFIG_NO_COLLATION to get the relevant declarations
// from "unicode/ucol.h".
#undef UCONFIG_NO_COLLATION

// To prevent a unicode/uconfig.h from complaining that
// UCONFIG_SYSTEM_COLLATION requires UCONFIG_NO_COLLATION too.
#undef UCONFIG_SYSTEM_COLLATION

#include "collator.h"

#include "unicode/unistr.h"
#include "unicode/locid.h"
#include "unicode/ucol.h"

#include <vector>

U_NAMESPACE_BEGIN

// Check ECollationStrength values.
#define CHECK_COLLATOR_ENUM(name) \
static_assert(\
    static_cast<int>(Collator:: name) == static_cast<int>(UCOL_ ## name), \
    "Invalid Collator::" #name " enum value");

CHECK_COLLATOR_ENUM(DEFAULT)
CHECK_COLLATOR_ENUM(PRIMARY)
CHECK_COLLATOR_ENUM(SECONDARY)
CHECK_COLLATOR_ENUM(TERTIARY)
CHECK_COLLATOR_ENUM(QUATERNARY)
CHECK_COLLATOR_ENUM(IDENTICAL)

// Retrieve the list of available locals, and return it as
// a vector of icu::Locale instances.
static std::vector<icu::Locale> GetAvailableLocales() {
  int32_t count = ucol_countAvailable();
  std::vector<icu::Locale> result;
  for (int32_t n = 0; n < count; ++n) {
    const char* locale_name = ucol_getAvailable(n);
    result.push_back(icu::Locale(locale_name));
  }
  return result;
}

Collator::~Collator() {
  ucol_close(collator_);
}

// static
Collator* Collator::createInstance(UErrorCode& error) {
  // NOTE: The empty string is used to name the root locale.
  return new Collator(ucol_open("", &error));
}

// static
Collator* Collator::createInstance(const icu::Locale& locale,
                                   UErrorCode& error) {
    return new Collator(ucol_open(locale.getName(), &error));
}

void Collator::setStrength(ECollationStrength newStrength) {
  ucol_setStrength(collator_, static_cast<UCollationStrength>(newStrength));
}

UCollationResult Collator::compare(const UnicodeString& source,
                                   const UnicodeString& target,
                                   UErrorCode& error) const {
  error = U_ZERO_ERROR;
  return ucol_strcoll(collator_,
                      source.getBuffer(), source.length(),
                      target.getBuffer(), target.length());
}

UCollationResult Collator::compare(const char16_t* a, int32_t a_len,
                                   const char16_t* b, int32_t b_len) const {
  return ucol_strcoll(collator_,
                      reinterpret_cast<const UChar*>(a), a_len,
                      reinterpret_cast<const UChar*>(b), b_len);
}

UCollationResult Collator::compareUTF8(const std::string& a,
                                       const std::string& b,
                                       UErrorCode& error) const {
  return ucol_strcollUTF8(collator_,
                          a.c_str(), static_cast<int32_t>(a.size()),
                          b.c_str(), static_cast<int32_t>(b.size()), &error);
}

int32_t Collator::getSortKey(const icu::UnicodeString& source,
                             uint8_t* result, int32_t resultLength) const {
    return getSortKey(source.getBuffer(), source.length(), result,
                      resultLength);
}

int32_t Collator::getSortKey(const char16_t* source, int32_t sourceLength,
                                uint8_t* result, int32_t resultLength) const {
    return ucol_getSortKey(collator_, reinterpret_cast<const UChar*>(source),
                           sourceLength, result, resultLength);
}

void Collator::setAttribute(UColAttribute attr, UColAttributeValue value,
                               UErrorCode& error) {
  ucol_setAttribute(collator_, attr, value, &error);
}

UColAttributeValue Collator::getAttribute(UColAttribute attr,
                                          UErrorCode& error) const {
  return ucol_getAttribute(collator_, attr, &error);
}

// static
const Locale* Collator::getAvailableLocales(int32_t& count) {
  // Use a static local var to guarantee thread-safe lazy initialization.
  static std::vector<icu::Locale> kAvailableLocales(GetAvailableLocales());
  count = static_cast<int32_t>(kAvailableLocales.size());
  return &kAvailableLocales[0];
}

U_NAMESPACE_END
