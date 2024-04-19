// Copyright 2016 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stddef.h>
#include <stdint.h>

#include "base/memory/ptr_util.h"
#include "third_party/icu/fuzzers/fuzzer_utils.h"
#include "third_party/icu/source/common/unicode/unistr.h"
#include "third_party/icu/source/i18n/unicode/regex.h"

struct Env {
  Env() {
    const std::string regex_str = "^[^0-9+]*(?:\\+|00)\\s*([1-9]\\d{0,3})\\D*$";
    auto regex = UnicodeStringFromUtf8(
        reinterpret_cast<const uint8_t*>(regex_str.data()), regex_str.length());
    UErrorCode status = U_ZERO_ERROR;
    regex_pattern = base::WrapUnique(
        icu::RegexPattern::compile(regex, UREGEX_CASE_INSENSITIVE, status));
  }

  std::unique_ptr<icu::RegexPattern> regex_pattern;
};

Env env;

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  auto str = UnicodeStringFromUtf8(data, size);
  UErrorCode status = U_ZERO_ERROR;
  std::unique_ptr<icu::RegexMatcher> regex_matcher =
      base::WrapUnique(env.regex_pattern->matcher(str, status));
  if (status == U_ZERO_ERROR) {
    regex_matcher->find(0, status);
  }
  return 0;
}
