
import React from 'react';
import { List, Avatar, Typography, theme } from 'antd';
import { BankOutlined, RightOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

export default function CompanyList({ data = [], loading = false }) {
  const { token } = theme.useToken();

  return (
    <List
      loading={loading}
      itemLayout="horizontal"
      dataSource={data}
      split={false}
      renderItem={(item, index) => (
        <List.Item
          style={{
            padding: '12px 16px',
            marginBottom: 8,
            background: 'rgba(255, 255, 255, 0.04)',
            borderRadius: 12,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
          }}
          className="company-list-item"
          actions={[
            <RightOutlined key="arrow" style={{ color: 'rgba(255, 255, 255, 0.3)' }} />
          ]}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <List.Item.Meta
            avatar={
              <Avatar 
                shape="square" 
                size={48} 
                icon={<BankOutlined />} 
                src={item.category}
                style={{ 
                    backgroundColor: item.color || token.colorPrimary,
                    borderRadius: 8
                }} 
              />
            }
            title={
                <Text style={{ color: '#fff', fontSize: 16, fontWeight: 500 }}>
                    {item.zwjc}
                </Text>
            }
          />
        </List.Item>
      )}
    />
  );
};
