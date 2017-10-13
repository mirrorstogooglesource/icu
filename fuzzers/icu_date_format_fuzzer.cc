// Copyright 2016 The Chromium Authors. All rights reserved.

#define V8_INTL_SUPPORT
//#define U_DISABLE_RENAMING true

#include <iostream>
#include <stddef.h>
#include <stdint.h>
#include <memory>
#include <list>
#include <map>
#include <regex>
#include "third_party/icu/fuzzers/fuzzer_utils.h"
#include "third_party/icu/source/i18n/unicode/datefmt.h"
#include "third_party/icu/source/i18n/unicode/coll.h"
#include "third_party/icu/fuzzers/intl-objects.h"

IcuEnvironment* env = new IcuEnvironment();

using namespace std;
using namespace fuzzer;


// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* pdata, size_t psize) {

    if(!psize) return 0;

    const uint8_t* data = pdata;
    size_t size = psize;

    string locale;
    bool ret = ExtractString((const char*&)data, size, locale);
    if(!ret) return 0;

#if DBLOG
    cout << "locale : " << locale.c_str() << endl;
#endif

    icu::SimpleDateFormat* date_format = DateFormat::InitializeDateTimeFormat(data, locale.c_str(), size);
    if(!date_format) return 0;

    icu::UnicodeString formatted;
    //icu::FieldPositionIterator fp_iter;
    //icu::FieldPosition fp;
    UDate date;
    if(size < sizeof(UDate)) {
        delete date_format;
        return 0;
    }

    date = ((UDate*)data)[0];
#if DBLOG
    cout << "date : " << date << "  ==  " << hex << ((unsigned long long*)data)[0] << endl;
#endif
    data += sizeof(UDate);
    size -= sizeof(UDate);
    date_format->format(date, formatted);//, &fp_iter, status
    delete date_format;


    // auto rng = CreateRng(data, size);
    // const icu::Locale& locale = GetRandomLocale(&rng);

    // unique_ptr<icu::DateFormat> fmt(
    //     icu::DateFormat::createDateTimeInstance(icu::DateFormat::kDefault, icu::DateFormat::kDefault, locale));
    // //if (U_FAILURE(status)) return 0;

    // //DateFormat* df = DateFormat::createDateInstance( DateFormat::SHORT, Locale::getFrance());
    // //UDate myDate = df->parse(myString, status);

    // icu::UnicodeString str(UnicodeStringFromUtf8(data, size));
    // fmt->parse(str, status);

    return 0;
}
