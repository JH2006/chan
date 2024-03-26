#pragma once

#include <iostream>
#include <string>
#include <stdint.h>
#include <memory>
#include <list>
#include <fstream>
#include <vector>
#include <sstream>

namespace JH {

class LogEvent{
    public:
        typedef std::shared_ptr<LogEvent> ptr;
        LogEvent(const char *file, uint32_t line, uint32_t elapse, uint32_t threadId, uint32_t fiberId, uint64_t time, const std::string &contest);

        const char* getFile() const {return m_file;}
        uint32_t getLine() const {return m_line;}
        uint32_t getElapse() const {return m_elapse;}
        uint32_t getThreadId() const {return m_threadId;}
        uint32_t getFiberId() const {return m_fiberId;}
        uint64_t getTime() const {return m_time;}
        const std::string& getContent() const {return m_content;}

    private:
        const char *m_file = nullptr;
        int32_t m_line = 0;
        uint32_t m_elapse = 0;
        uint32_t m_threadId = 0;
        uint32_t m_fiberId = 0;
        uint64_t m_time = 0;
        std::string m_content;
};

class LogLevel{
    public:
        enum Level
        {
            DEBUG = 1,
            INFO = 2,
            WARN = 3,
            ERROR = 4,
            FATAL = 5
        };

    static std::string ToString(LogLevel::Level level){
        switch (level) {
            case LogLevel::Level::DEBUG:
                return "DEBUG";
                break;
            case LogLevel::Level::INFO:
                return "DEBUG";
                break;
            case LogLevel::Level::WARN:
                return "DEBUG";
                break;
            case LogLevel::Level::ERROR:
                return "DEBUG";
                break;
            case LogLevel::Level::FATAL:
                return "DEBUG";
                break;
            default:
                return "UNKOWN";
        }
    }
};

class LogFormatter{
public:
    typedef std::shared_ptr<LogFormatter> ptr;
    LogFormatter(const std::string& pattern);

    /// @brief 
    /// @param level 
    /// @param event 
    /// @return 
    std::string format(LogLevel::Level level, LogEvent::ptr event);

public:
    class FormatItem{
    public:
        typedef std::shared_ptr<FormatItem> ptr;

        FormatItem(const std::string &fmt = ""){};

        virtual ~FormatItem() {}

        virtual void format(LogLevel::Level level, std::ostream& os, LogEvent::ptr event) = 0;
    };
 
    void init();

private:
    std::string m_pattern;
    std::vector<FormatItem::ptr> m_items;
};

class LogAppender{
public:
    typedef std::shared_ptr<LogAppender> ptr; 
    LogAppender(const LogLevel::Level level) : m_level{level}{}
    virtual ~LogAppender(){};

    virtual void log(LogLevel::Level level, LogEvent::ptr event) = 0;

    void setFormatter(const LogFormatter::ptr formatter) { m_formatter = formatter; }
    LogFormatter::ptr getFormatter() const { return m_formatter; }

protected:
    LogLevel::Level m_level;
    LogFormatter::ptr m_formatter;
};

class Logger
{
public:
    typedef std::shared_ptr<Logger> ptr;
    Logger(const std::string &name = "root");
    void log(LogLevel::Level level, const LogEvent::ptr event);

    void debug(LogEvent::ptr event);
    void info(LogEvent::ptr event);
    void warn(LogEvent::ptr event);
    void error(LogEvent::ptr event);
    void fatal(LogEvent::ptr event);

    void addAppender(const LogAppender::ptr appender);
    void delAppender(LogAppender::ptr appender);

    LogLevel::Level getLevel() const { return m_level;};
    void setLevel(LogLevel::Level level) { m_level = level; };

    const std::string getName() const { return m_name; }

private:
    std::string m_name;
    LogLevel::Level m_level;
    std::list<LogAppender::ptr> m_appenders;
};

class StdoutLogAppender : public LogAppender{
public:
    typedef std::shared_ptr<StdoutLogAppender> ptr;

    StdoutLogAppender(const LogLevel::Level level) : LogAppender(level){}

    virtual void log(LogLevel::Level level, const LogEvent::ptr event);
};

class FileLogAppender : public LogAppender{
public:
    typedef std::shared_ptr<FileLogAppender> ptr;
    FileLogAppender(const std::string &filename, const LogLevel::Level level);

    virtual void log(LogLevel::Level level, LogEvent::ptr event);

    // 重新打开文件，文件打开成功返回true
    bool reopen();

private:
    std::string m_filename;
    std::ofstream m_filestream;
};
}
