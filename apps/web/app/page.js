'use client';

import { useState } from 'react';
import { Sender, XProvider, Suggestion } from '@ant-design/x';
import { ArrowUpOutlined } from '@ant-design/icons';
import { ConfigProvider, theme, Button } from 'antd';
import { useCompanyInfo } from './hook';

export default function Home() {
  const [value, setValue] = useState('');
  const [selectedButton, setSelectedButton] = useState(null);

  const companyInfo = useCompanyInfo(value);

  const handleSubmit = (val) => {
    console.log('Submit:', val);
    setValue('');
  };

  const handleButtonClick = (buttonName) => {
    setSelectedButton(selectedButton === buttonName ? null : buttonName);
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

          {/* Input Box */}
          <div style={styles.inputContainer}>

            <Suggestion
              items={companyInfo}>
              {
                ({ onTrigger, onKeyDown, open }) => {
                  return <> <Sender
                    value={value}
                    onSubmit={handleSubmit}
                    placeholder="告诉我你要查询公司的信息?"
                    suffix={
                      <div style={styles.suffixContainer} onClick={() => value && handleSubmit(value)}>
                        <ArrowUpOutlined style={{ fontSize: 18, color: '#fff', cursor: 'pointer' }} />
                      </div>
                    }
                    onChange={(nextVal) => {
                      if (nextVal === '/') {
                        onTrigger();
                      } else if (!nextVal) {
                        onTrigger(false);
                      }
                      setValue(nextVal);
                    }}
                    style={styles.sender}
                    styles={{
                      input: {
                        backgroundColor: 'transparent',
                        color: '#fff',
                      },
                    }}
                  /></>
                }
              }
            </Suggestion>



            {/* <div style={styles.buttonContainer}>
              <Button 
                shape="round" 
                size="large"
                type={selectedButton === 'company' ? 'primary' : 'default'}
                onClick={() => handleButtonClick('company')}
                style={selectedButton === 'company' ? styles.primaryButton : styles.defaultButton}
              >
                查公司
              </Button>
              <Button 
                shape="round" 
                size="large"
                type={selectedButton === 'financial' ? 'primary' : 'default'}
                onClick={() => handleButtonClick('financial')}
                style={selectedButton === 'financial' ? styles.primaryButton : styles.defaultButton}
              >
                查财报
              </Button>
            </div> */}
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
