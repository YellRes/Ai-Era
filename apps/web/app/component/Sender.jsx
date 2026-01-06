'use client';

import { useState, useRef, useMemo } from 'react';
import { Sender, XProvider, Suggestion } from '@ant-design/x';
import {
  SearchOutlined,
  FileTextOutlined,
  BarChartOutlined,
  BulbOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { ConfigProvider, theme, Button, Tag, Space, Popover, Select } from 'antd';
import { useCompanyInfo } from '../hook';
import { EXCHANGE_CODE_MAP } from '../constant';

// 在组件外部定义常量，避免每次渲染创建新引用
const EMPTY_SLOT_CONFIG = [];

// 定义可用的技能列表
const SKILL_OPTIONS = [
  // { key: 'search', label: '智能搜索', icon: <SearchOutlined />, color: '#1677ff' },
  { key: 'report', label: '生成报告', icon: <FileTextOutlined />, color: '#52c41a' },
  // { key: 'chart', label: '数据可视化', icon: <BarChartOutlined />, color: '#fa8c16' },
  // { key: 'idea', label: '创意建议', icon: <BulbOutlined />, color: '#eb2f96' },
];

// 独立的公司选择组件，在内部管理搜索状态，避免影响外部 slotConfig
const CompanySelect = ({ value, onChange, disabled, readOnly }) => {
  const [searchValue, setSearchValue] = useState('');
  const { filterCompanyInfo } = useCompanyInfo(searchValue);

  return (
    <Select
      value={value}
      onChange={onChange}
      placeholder="选择公司"
      showSearch
      onSearch={(val) => {
        setSearchValue(val);
      }}
      filterOption={false}
      variant="borderless"
      size="small"
      style={{
        minWidth: 100,
        maxWidth: 180,
        height: 24,
        lineHeight: '22px',
        backgroundColor: 'rgba(82, 196, 26, 0.15)',
        borderRadius: 4,
        margin: '0 2px',
        verticalAlign: 'middle',
      }}
      popupMatchSelectWidth={false}
      options={filterCompanyInfo}
    />
  );
};

// 根据技能生成词槽配置
const generateSlotConfig = (skillKey) => {
  if (skillKey === 'report') {
    return [
      {
        type: 'text',
        value: '请选择'
      },
      {
        type: 'custom',
        key: 'company-select',
        props: {
          defaultValue: undefined,
        },
        formatResult: (value) => value || '',
        customRender: (value, onChange, { disabled, readOnly }) => (
          <CompanySelect
            value={value}
            onChange={onChange}
            disabled={disabled}
            readOnly={readOnly}
          />
        ),
      },
      {
        type: 'text',
        value: '公司，我来分析公司财报'
      },
    ];
  }
  return EMPTY_SLOT_CONFIG;
};

// 自定义技能按钮组件
const SkillButton = ({ skill, isActive, onClick }) => {
  return (
    <Button
      type={isActive ? 'primary' : 'default'}
      icon={skill.icon}
      onClick={() => onClick(skill)}
      style={{
        backgroundColor: isActive ? skill.color : 'rgba(255, 255, 255, 0.05)',
        borderColor: isActive ? skill.color : 'rgba(255, 255, 255, 0.1)',
        color: isActive ? '#fff' : '#a0a0a0',
        boxShadow: isActive ? `0 2px 8px ${skill.color}40` : 'none',
        transition: 'all 0.3s ease',
      }}
    >
      {skill.label}
    </Button>
  );
};

// 自定义技能选择器组件
const SkillSelector = ({ selectedSkill, onSelect, onClear }) => {
  return (
    <div style={skillStyles.container}>
      <Space size={8} wrap>
        {SKILL_OPTIONS.map((skill) => (
          <SkillButton
            key={skill.key}
            skill={skill}
            isActive={selectedSkill?.key === skill.key}
            onClick={onSelect}
          />
        ))}
      </Space>
      {/* {selectedSkill && (
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClear}
          style={{ color: '#a0a0a0', marginLeft: 8 }}
          size="small"
        >
          清除选择
        </Button>
      )} */}
    </div>
  );
};

// 已选择技能展示组件
const SelectedSkillTag = ({ skill, onClose }) => {
  if (!skill) return null;

  return (
    <Tag
      closable
      onClose={onClose}
      style={{
        backgroundColor: `${skill.color}20`,
        borderColor: skill.color,
        color: skill.color,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: '4px 8px',
        marginRight: 8,
      }}
    >
      {skill.icon}
      <span>{skill.label}</span>
    </Tag>
  );
};

const skillStyles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 0',
    flexWrap: 'wrap',
    gap: 8,
  },
};

export default function SenderComponent({ onSubmit: onSubmitProp, loading = false }) {
  // 词槽模式下 value 无效，用 key 控制重置
  const [senderKey, setSenderKey] = useState(0);
  const [selectedButton, setSelectedButton] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(SKILL_OPTIONS[0]);
  const senderRef = useRef(null);

  // 用于 Suggestion 组件的公司信息映射
  const { filterCompanyCode2NameMap, originalCompanyInfo } = useCompanyInfo('');

  // 根据选中的技能生成词槽配置
  // CompanySelect 组件内部管理搜索状态，不影响这里的 slotConfig
  const currentSlotConfig = useMemo(() => {
    if (!selectedSkill) return EMPTY_SLOT_CONFIG;
    return generateSlotConfig(selectedSkill.key);
  }, [selectedSkill]);

  // 处理技能选择
  const handleSkillSelect = (skill) => {
    setSelectedSkill(skill);
    // 切换技能时重置 Sender
    setSenderKey(prev => prev + 1);
  };

  // 清除技能选择
  const handleSkillClear = () => {
    setSelectedSkill(null);
  };

  const handleSubmit = (message, slotConfig) => {
    console.log('提交文本:', message);
    console.log('词槽配置:', slotConfig);
    console.log('选中技能:', selectedSkill);

    // 调用外部回调
    if (onSubmitProp) {
      const res = senderRef.current?.getValue();

      let message = ''
      if (res.slotConfig) {
        let selectedCompany = res.slotConfig.find(item => item.key === 'company-select')?.value || ''
        let query = originalCompanyInfo.find(item => item.code === selectedCompany)
        message = {
          ...query,
          exchange_code: EXCHANGE_CODE_MAP[query.orgId.slice(0, 4)] || EXCHANGE_CODE_MAP[query.code.slice(0, 3)] || EXCHANGE_CODE_MAP[query.code.slice(0, 2)],
          stock_code: query.code,
          fiscal_year: new Date().getFullYear(),
          company_name: query.zwjc,
          // period_type: query.periodType
        }
      } else {
        message = value.value || ''
      }

      console.log(message)

      onSubmitProp({ query: message, message: res.value }, slotConfig);
    }

    // 重置输入框`
    setSenderKey(prev => prev + 1);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorBgContainer: '#2a2a2a',
          colorBgElevated: '#1a1a1a',
          colorText: '#ffffff',
          colorTextSecondary: '#a0a0a0',
          borderRadius: 16,
        },
      }}
    >
      <XProvider>
        <div style={styles.main}>
          <div style={styles.inputContainer}>

            <Suggestion
              block
              // items={() => filterCompanyInfo}
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
                    slotConfig={currentSlotConfig}
                    placeholder="输入 / 唤起快捷指令"
                    onSubmit={handleSubmit}
                    loading={loading}
                    disabled={loading}
                    onChange={(text, event, slotConfig) => {
                    }}
                    style={styles.sender}
                    styles={{
                      input: {
                        backgroundColor: 'transparent',
                        color: '#fff',
                      },
                    }}
                    // 自定义 header 展示技能选择器
                    header={
                      <div style={styles.skillHeader}>
                        <div style={styles.skillHeaderTitle}>选择技能</div>
                        <SkillSelector
                          selectedSkill={selectedSkill}
                          onSelect={handleSkillSelect}
                          onClear={handleSkillClear}
                        />
                      </div>
                    }
                    // 自定义 prefix 展示已选技能
                    prefix={
                      selectedSkill && (
                        <SelectedSkillTag
                          skill={selectedSkill}
                          onClose={handleSkillClear}
                        />
                      )
                    }
                  />
                )
              }
            </Suggestion>

          </div>
        </div>
      </XProvider>
    </ConfigProvider>
  );
}

const styles = {
  main: {
    width: '100%',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  skillHeader: {
    padding: '12px 16px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
  },
  skillHeaderTitle: {
    fontSize: 13,
    color: '#a0a0a0',
    marginBottom: 8,
    fontWeight: 500,
  },
  inputContainer: {
    width: '100%',
  },
  sender: {
    backgroundColor: '#2a2a2a',
    borderRadius: 16,
    border: '1px solid rgba(255, 255, 255, 0.08)',
    padding: '4px 16px',
  },
};
