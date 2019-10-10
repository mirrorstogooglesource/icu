// Copyright 2019 The Chromium Authors. All rights reserved.

#include <stddef.h>
#include <stdint.h>
#include <vector>
#include "third_party/icu/fuzzers/fuzzer_utils.h"
#include "third_party/icu/source/common/unicode/appendable.h"

IcuEnvironment* env = new IcuEnvironment();

constexpr size_t kMaxReserveSize = 4096;
constexpr size_t kMaxAdditionalDesiredSize = 4096;

constexpr size_t kScratchBufSize = 4096;
char16_t scratch_buf[kScratchBufSize];

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  icu::UnicodeString str(UnicodeStringFromUtf8(data, size));
  icu::UnicodeStringAppendable strAppendable(str);

  auto rng = CreateRng(data, size);

  switch (rng() % 5) {
    case 0:
      strAppendable.appendCodeUnit(rng());
      break;
    case 1:
      strAppendable.appendCodePoint(rng());
      break;
    case 2: {
      std::vector<char16_t> appendChrs;
      appendChrs.resize(rng() % size * sizeof(uint8_t) / sizeof(char16_t));
      memcpy(appendChrs.data(), data,
             appendChrs.size() * sizeof(char16_t) / sizeof(uint8_t));
      strAppendable.appendString(appendChrs.data(), appendChrs.size());
      break;
    }
    case 3:
      strAppendable.reserveAppendCapacity(rng() % kMaxReserveSize);
      break;
    case 4: {
      int32_t out_capacity;
      const int32_t min_capacity = rng() % (kScratchBufSize - 1) + 1;
      char16_t* out_buffer = strAppendable.getAppendBuffer(
          min_capacity, min_capacity + rng() % kMaxAdditionalDesiredSize,
          scratch_buf, kScratchBufSize, &out_capacity);
      if (out_buffer)
        out_buffer[out_capacity - 1] = 0xabcd;
      break;
    }
  }

  return 0;
}
