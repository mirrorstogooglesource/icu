// Copyright 2020 The Chromium Authors. All rights reserved.

// Fuzzer for toLower/toUpper

#include <stddef.h>
#include <stdint.h>
#include <memory>
#include "third_party/icu/fuzzers/fuzzer_utils.h"
#include "third_party/icu/source/common/unicode/ustring.h"

IcuEnvironment* env = new IcuEnvironment();

template <typename T>
using deleted_unique_ptr = std::unique_ptr<T, std::function<void(T*)>>;

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  UErrorCode status = U_ZERO_ERROR;
  icu::UnicodeString str(UnicodeStringFromUtf32(data, size));

  auto rng = CreateRng(data, size);
  const icu::Locale& locale = GetRandomLocale(&rng);

  if (U_FAILURE(status))
    return 0;

  // Make the dest_size randomly fall in [0, strlen+3]
  int32_t dest_size = (rng() % (str.length() + 3));
  std::unique_ptr<UChar[]> dest(new UChar[dest_size]);

  switch (rng() % 2) {
    case 0:
      u_strToUpper(dest.get(), dest_size, (const UChar*)str.getBuffer(),
                   str.length(), locale.getName(), &status);
      break;
    case 1:
      u_strToLower(dest.get(), dest_size, (const UChar*)str.getBuffer(),
                   str.length(), locale.getName(), &status);
      break;
  }

  return 0;
}
