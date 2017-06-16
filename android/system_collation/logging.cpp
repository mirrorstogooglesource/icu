#include "logging.h"

#include <android/log.h>

#include <stdio.h>
#include <stdlib.h>

namespace icu_system_collation {

static bool sSendLogToStderr = false;

// Generic and specialized logging functions.
static void LogGeneric(android_LogPriority prio,
                       const char* fmt, va_list args) {
  // Always send messages to the Android log.
  __android_log_vprint(prio, "IcuSystemCollation", fmt, args);

  // Optionally send them to stderr too.
  if (sSendLogToStderr) {
    fprintf(stderr, "IcuSystemCollation: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
  }
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
  abort();
}

void testing::SendLogToStderr() {
  sSendLogToStderr = true;
}

}  // namespace icu_system_collation
