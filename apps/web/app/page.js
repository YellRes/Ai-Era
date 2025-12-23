'use client';

import { useState } from 'react';
import { Sender, XProvider } from '@ant-design/x';
import { ArrowUpOutlined } from '@ant-design/icons';
import { ConfigProvider, theme, Button } from 'antd';

export default function Home() {
  const [value, setValue] = useState('');

  const handleSubmit = (val) => {
    console.log('Submit:', val);
    setValue('');
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#ffffff',
          colorBgContainer: '#2a2a2a',
          colorBgElevated: '#1a1a1a',
          colorText: '#ffffff',
          colorTextSecondary: '#a0a0a0',
          borderRadius: 24,
        },
      }}
    >
      <XProvider>
        <main style={styles.main}>
          {/* Logo */}
          <div style={styles.logoContainer}>
            <svg style={styles.logoIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M8 12l2 2 4-4" />
            </svg>
            <span style={styles.logoText}>Ai-Era</span>
          </div>

          {/* Input Box */}
          <div style={styles.inputContainer}>
            <Sender
              value={value}
              onChange={setValue}
              onSubmit={handleSubmit}
              placeholder="What do you want to know?"
              suffix={
                <div style={styles.suffixContainer} onClick={() => value && handleSubmit(value)}>
                  <ArrowUpOutlined style={{ fontSize: 18, color: '#fff', cursor: 'pointer' }} />
                </div>
              }
              style={styles.sender}
              styles={{
                input: {
                  backgroundColor: 'transparent',
                  color: '#fff',
                },
              }}
            />
            <div style={styles.buttonContainer}>
              <Button shape="round" size="large">查公司</Button>
              <Button shape="round" size="large">查财报</Button>
            </div>
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
    borderRadius: 28,
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
};
