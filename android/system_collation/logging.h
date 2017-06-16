#pragma once

namespace icu_system_collation {

// Explicit logging functions. Only call directly if you want to always
// generate log messages. Otherwise, use the LOG_XXX() macros.
void LogInfo(const char* fmt, ...);
void LogError(const char* fmt, ...);
void LogFatal(const char* fmt, ...);

// LOG_VERBOSE() doesn't do anything in release builds.
#ifndef _NDEBUG
#define LOG_VERBOSE(...)  icu_system_collation::LogInfo(__VA_ARGS__)
#else
#define LOG_VERBOSE(...)  ((void)0)
#endif

#define LOG_INFO(...)  icu_system_collation::LogInfo(__VA_ARGS__)
#define LOG_ERROR(...)  icu_system_collation::LogInfo(__VA_ARGS__)
#define LOG_FATAL(...)  icu_system_collation::LogFatal(__VA_ARGS__)

#define LOG_IF(condition,...) \
  do { if (!!(condition)) icu_system_collation::LogInfo(__VA_ARGS__); } while (0)

namespace testing {

// Call this function to redirect logs to stderr. Useful when running
// unit-tests from the command-line.
void SendLogToStderr();

}  // namespace

}  // namespace icu_system_collation
