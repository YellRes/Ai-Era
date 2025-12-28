'use client';
import { useState, useCallback } from 'react';
import { Sender, MessageList } from './component/index';

// 流式请求需要在客户端直接 fetch，不能通过 Server Action
const API_BASE = 'http://127.0.0.1:8000';

export default function Home() {
  const [messages, setMessages] = useState([]);
  
  // 是否有消息，决定布局模式
  const hasMessages = messages.length > 0;

  // 处理发送消息
  const handleSubmit = useCallback(async ({message, query}, slotValues) => {
    // if (!message.trim()) return;
    
    // 添加用户消息
    const userMessage = {
      content: message,
      role: 'user',
      key: `user_${Date.now()}`,
    };
    setMessages(prev => [...prev, userMessage]);

    // 添加 AI 消息占位
    const aiMessageKey = `ai_${Date.now()}`;
    setMessages(prev => [...prev, {
      content: '',
      role: 'assistant',
      key: aiMessageKey,
    }]);

    try {
      // 直接在客户端 fetch，处理流式响应
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: JSON.stringify(query),
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        fullText += chunk;
        
        // 实时更新 AI 消息内容
        setMessages(prev => prev.map(msg => 
          msg.key === aiMessageKey 
            ? { ...msg, content: fullText }
            : msg
        ));
      }
    } catch (error) {
      console.error('请求失败:', error);
      setMessages(prev => prev.map(msg => 
        msg.key === aiMessageKey 
          ? { ...msg, content: '请求失败，请重试' }
          : msg
      ));
    }
  }, []);

  return (
    <div style={styles.container}>
      {/* 欢迎界面 - 仅在没有消息时显示 */}
      {!hasMessages && (
        <div style={styles.welcomeSection}>
          <div style={styles.logoContainer}>
            <span style={styles.logoText}>Ai-Era</span>
          </div>
          <p style={styles.welcomeSubtitle}>智能财报分析助手</p>
        </div>
      )}

      {/* 消息列表 - 仅在有消息时显示 */}
      {hasMessages && (
        <div style={styles.messageSection}>
          <MessageList messages={messages} />
        </div>
      )}

      {/* 输入区域 */}
      <div style={{
        ...styles.inputSection,
        ...(hasMessages ? styles.inputSectionBottom : styles.inputSectionCenter)
      }}>
        <div style={styles.inputWrapper}>
          <Sender onSubmit={handleSubmit} />
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#1a1a1a',
    overflow: 'hidden',
    position: 'relative',
  },
  
  // 欢迎区域
  welcomeSection: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: '120px',
    animation: 'fadeIn 0.5s ease-out',
  },
  logoContainer: {
    marginBottom: 16,
  },
  logoText: {
    fontSize: 56,
    fontWeight: 300,
    color: '#fff',
    letterSpacing: '-2px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  welcomeSubtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.5)',
    fontWeight: 300,
    letterSpacing: '0.5px',
  },

  // 消息区域
  messageSection: {
    flex: 1,
    overflow: 'auto',
    padding: '24px 0',
    paddingBottom: '120px', // 给底部输入框留出空间
    animation: 'slideDown 0.3s ease-out',
  },

  // 输入区域 - 始终使用 absolute 定位，只改变垂直位置
  inputSection: {
    position: 'absolute',
    left: 0,
    right: 0,
    display: 'flex',
    justifyContent: 'center',
    transition: 'bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1), top 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  inputSectionCenter: {
    top: '55%',
    bottom: 'auto',
    transform: 'translateY(-50%)',
  },
  inputSectionBottom: {
    top: 'auto',
    bottom: 0,
    transform: 'translateY(0)',
    padding: '16px 0 24px',
    borderTop: '1px solid rgba(255, 255, 255, 0.06)',
    background: 'linear-gradient(to top, #1a1a1a 0%, rgba(26, 26, 26, 0.95) 100%)',
  },
  inputWrapper: {
    width: '100%',
    maxWidth: 800,
    padding: '0 24px',
  },
};
