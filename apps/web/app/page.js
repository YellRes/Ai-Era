'use client';

import { useState, useRef } from 'react';
import { Sender, XProvider, Suggestion } from '@ant-design/x';
import { ArrowUpOutlined } from '@ant-design/icons';
import { ConfigProvider, theme, Button } from 'antd';
import { useCompanyInfo } from './hook';

// 在组件外部定义常量，避免每次渲染创建新引用
const EMPTY_SLOT_CONFIG = [];

export default function Home() {
  // 词槽模式下 value 无效，用 key 控制重置
  const [senderKey, setSenderKey] = useState(0);
  const [selectedButton, setSelectedButton] = useState(null);
  const senderRef = useRef(null);

  // 词槽模式下不依赖 value 过滤，使用空字符串获取全部数据
  const {filterCompanyInfo, filterCompanyCode2NameMap} = useCompanyInfo('');

  const handleSubmit = (message, slotConfig) => {
    console.log('提交文本:', message);
    console.log('词槽配置:', slotConfig);
    // 重置输入框
    setSenderKey(prev => prev + 1);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          colorBgContainer: '#2a2a2a',
          colorBgElevated: '#1a1a1a',
          colorText: '#ffffff',
          colorTextSecondary: '#a0a0a0',
          borderRadius: 24,
        },
        components: {
          Button: {
            paddingInline: 24,
            defaultBg: 'rgba(255, 255, 255, 0.05)',
            defaultBorderColor: 'rgba(255, 255, 255, 0.1)',
            defaultColor: '#a0a0a0',
          },
        },
      }}
    >
      <XProvider>
        <main style={styles.main}>
          {/* Logo */}
          <div style={styles.logoContainer}>
            <span style={styles.logoText}>Ai-Era</span>
          </div>
     
          <div style={styles.inputContainer}>

            <Suggestion
              block
              items={() => filterCompanyInfo}
              onSelect={(item) => {
                if (senderRef.current?.insert) {
                  senderRef.current.insert([
                    { 
                      type: 'tag',
                      key: `tag-${item}-${Date.now()}`,  // ✅ 添加唯一 key
                      props: { 
                        label: filterCompanyCode2NameMap[item] || item,
                        value: item 
                      }  
                    }
                  ]);
                }
              }}
              >
              {
                ({ onTrigger }) => (
                  <Sender
                    key={senderKey}
                    ref={senderRef}
                    slotConfig={EMPTY_SLOT_CONFIG}
                    placeholder="输入 / 唤起快捷指令"
                    onSubmit={handleSubmit}
                    onChange={(text, event, slotConfig) => {
                      // 词槽模式下 text 是纯文本内容
                      if (text === '/') {
                        onTrigger();
                      } else if (!text) {
                        onTrigger(false);
                      }
                    }}
                    style={styles.sender}
                    styles={{
                      input: {
                        backgroundColor: 'transparent',
                        color: '#fff',
                      },
                    }}
                  />
                )
              }
            </Suggestion>

          </div>
        </main>
      </XProvider>
    </ConfigProvider>
  );
}

const styles = {
  main: {
    minHeight: '100vh',
    backgroundColor: '#1a1a1a',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 40,
  },
  logoIcon: {
    width: 48,
    height: 48,
    color: '#fff',
    marginRight: 12,
  },
  logoText: {
    fontSize: 48,
    fontWeight: 300,
    color: '#fff',
    letterSpacing: '-1px',
  },
  inputContainer: {
    width: '100%',
    maxWidth: 700,
  },
  sender: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    border: 'none',
    padding: '4px 16px',
  },

  suffixContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    padding: '8px',
    backgroundColor: '#444',
    borderRadius: '50%',
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'flex-start',
    marginTop: 20,
    gap: 12,
  },
  primaryButton: {
    background: 'linear-gradient(135deg, #1677ff 0%, #003eb3 100%)',
    border: 'none',
    boxShadow: '0 4px 12px rgba(22, 119, 255, 0.3)',
    color: '#fff',
  },
  defaultButton: {
    backdropFilter: 'blur(8px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    transition: 'all 0.3s ease',
  },
};
