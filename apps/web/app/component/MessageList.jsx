import React from 'react';
import { Bubble } from '@ant-design/x';
import { ConfigProvider, theme } from 'antd';
import { XMarkdown } from '@ant-design/x-markdown';

const MessageList = ({ messages = [] }) => {
  // 将消息转换为 Bubble.List 需要的格式
  const bubbleItems = messages.map((msg) => ({
    content: <XMarkdown>{msg.content}</XMarkdown>,
    placement: msg.role === 'user' ? 'end' : 'start',
    key: msg.key,
    styles: {
      content: {
        backgroundColor: msg.role === 'user'
          ? 'rgba(102, 126, 234, 0.15)'
          : 'rgba(255, 255, 255, 0.08)',
        color: '#fff',
        borderRadius: 16,
        padding: '12px 16px',
        maxWidth: '70%',
      },
    },
  }));

  if (messages.length === 0) {
    return null;
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorBgContainer: 'transparent',
        },
      }}
    >
      <div style={styles.container}>
        <div style={styles.listWrapper}>
          <Bubble.List
            items={bubbleItems}
            style={styles.bubbleList}
            autoScroll
          />
        </div>
      </div>
    </ConfigProvider>
  );
};

const styles = {
  container: {
    width: '100%',
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
  listWrapper: {
    width: '100%',
    maxWidth: 800,
    padding: '0 24px',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  bubbleList: {
    background: 'transparent',
    flex: 1,
    minHeight: 0, // 关键：允许 flex 子元素收缩
    overflow: 'auto', // 让 Bubble.List 成为滚动容器，autoScroll 才能生效
  },
};

export default MessageList;
