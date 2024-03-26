#include <unordered_map>
#include <functional>
# include "log.h"

namespace JH {
    class MessageFormatItem : public LogFormatter::FormatItem{
    public:
        MessageFormatItem(const std::string& fmt) : LogFormatter::FormatItem(fmt){
        }
        
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getContent() << ' ';
        }
    };

    class LevelFormatItem : public LogFormatter::FormatItem{
    public:
        LevelFormatItem(const std::string& fmt) : LogFormatter::FormatItem(fmt){
            }
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << LogLevel::ToString(level) << '\n';
        }
    };

    class ElapseFormatItem : public LogFormatter::FormatItem{
    public:
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getElapse();
        }
    };

    class ThreadIdFormatItem : public LogFormatter::FormatItem{
    public:
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getThreadId();
        }
    };

    class FiberIdFormatItem : public LogFormatter::FormatItem{
    public:
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getFiberId();
        }
    };

    class DateTimeFormatItem : public LogFormatter::FormatItem{
    public:
        DateTimeFormatItem(const std::string format = "%Y:%m:%d %H:%M:%S")
        {

        }
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getTime();
        }
    };

    class LineFormatItem : public LogFormatter::FormatItem{
    public:
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getLine();
        }
    };

    class FilenameFormatItem : public LogFormatter::FormatItem{
    public:
        void format(LogLevel::Level level, std::ostream &os, LogEvent::ptr event) override{
            os << event->getFile();
        }
    };


    LogEvent::LogEvent(const char *file, uint32_t line, uint32_t elapse, uint32_t threadId, uint32_t fiberId, uint64_t time, const std::string &content): m_file{file},
    m_line{line}, m_elapse{elapse}, m_threadId{threadId}, m_fiberId{fiberId}, m_time{time}, m_content{content}{}


    Logger::Logger(const std::string& name) : m_name{name}{}

    void Logger::log(LogLevel::Level level, const LogEvent::ptr event){
        if(level >= m_level){
            for(auto& i : m_appenders)
                i->log(level, event);
        }
    }

    void Logger::debug(LogEvent::ptr event){
        log(LogLevel::DEBUG, event);
    }

    void Logger::info(LogEvent::ptr event){
        log(LogLevel::INFO, event);
    }

    void Logger::warn(LogEvent::ptr event){
        log(LogLevel::WARN, event);
    }

    void Logger::error(LogEvent::ptr event){
        log(LogLevel::ERROR, event);
    }

    void Logger::fatal(LogEvent::ptr event){
        log(LogLevel::FATAL, event);
    }

    void Logger::addAppender(const LogAppender::ptr appender){
        m_appenders.emplace_back(appender);
    }


    void Logger::delAppender(const LogAppender::ptr appender){
        m_appenders.remove(appender);
    }

    FileLogAppender::FileLogAppender(const std::string& filename, const LogLevel::Level level) : LogAppender(level), m_filename{filename}{

    }

    void StdoutLogAppender::log(LogLevel::Level level, LogEvent::ptr event){
        if(level >= m_level){
            std::cout << m_formatter->format(level, event);
            // std::cout << "Calling form StdoutLogAppender" << std::endl;
        }
    }

    void FileLogAppender::log(LogLevel::Level level, LogEvent::ptr event){
        if(level >= m_level){
            m_filestream << m_formatter->format(level, event);
        } 
    }

    bool FileLogAppender::reopen(){
        if(m_filestream.is_open()){
            m_filestream.close();
        }

        m_filestream.open(m_filename);

        return !m_filestream;
    }

    LogFormatter::LogFormatter(const std::string &pattern) : m_pattern{pattern}{

    }


    void LogFormatter::init() {
        static std::unordered_map<std::string, std::function<FormatItem::ptr(const std::string &fmt)>> s_format_items = {
            {"m", [](const std::string &fmt)
             { return std::make_shared<MessageFormatItem>(fmt); }},
            {"p", [](const std::string &fmt)
             { return std::make_shared<LevelFormatItem>(fmt); }}};

        
        // Mock code
        m_items.push_back(s_format_items.find("m")->second("Message"));
        m_items.push_back(s_format_items.find("p")->second("Level"));
    }

    std::string LogFormatter::format(LogLevel::Level level, LogEvent::ptr event) {
        std::stringstream ss;

        for(auto i : m_items){
            i->format(level, ss, event);
        }

        return ss.str();
    }



}