#pragma once

#include "../src/log.h"

void testLogger(){

   auto logformatter = std::make_shared<JH::LogFormatter>("test");
   logformatter->init();

   auto stdout = std::make_shared<JH::StdoutLogAppender>(JH::LogLevel::DEBUG);
   stdout->setFormatter(logformatter);


   auto logger = JH::Logger{};
   logger.setLevel(JH::LogLevel::DEBUG);
   logger.addAppender(stdout);

   auto logevent = std::make_shared<JH::LogEvent>(__FILE__, __LINE__, 0, 1, 2, time(0), "test");

   logger.log(JH::LogLevel::DEBUG, logevent);
}
  