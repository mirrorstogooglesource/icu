// Copyright 2016 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <fuzzer/FuzzedDataProvider.h>
#include <stddef.h>
#include <stdint.h>

#include "base/memory/ptr_util.h"
#include "third_party/icu/fuzzers/fuzzer_utils.h"
#include "third_party/icu/source/common/unicode/unistr.h"
#include "third_party/icu/source/i18n/unicode/regex.h"

// Matches an arbitrary regex against an arbitrary haystack of data.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  auto regex_data_length = provider.ConsumeIntegralInRange(1, 128);
  auto regex_data = provider.ConsumeBytes<uint8_t>(regex_data_length);
  auto haystack_data = provider.ConsumeRemainingBytes<uint8_t>();

  auto regex = UnicodeStringFromUtf8(regex_data.data(), regex_data.size());
  UErrorCode status = U_ZERO_ERROR;
  std::unique_ptr<icu::RegexPattern> regex_pattern = base::WrapUnique(
      icu::RegexPattern::compile(regex, UREGEX_CASE_INSENSITIVE, status));
  if (status != U_ZERO_ERROR) {
    return -1;  // invalid regex, don't explore further
  }
  status = U_ZERO_ERROR;
  auto haystack =
      UnicodeStringFromUtf8(haystack_data.data(), haystack_data.size());
  std::unique_ptr<icu::RegexMatcher> regex_matcher =
      base::WrapUnique(regex_pattern->matcher(haystack, status));
  if (status == U_ZERO_ERROR) {
    regex_matcher->find(0, status);
  }
  return 0;
}
