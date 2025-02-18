import React, { useState } from 'react';
import { Form, Input, DatePicker, Select, Button, Table, message } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import api from '../../services/api';

const StyledForm = styled(Form)`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;

  .ant-form-item {
    margin-bottom: 24px;
  }

  .items-table {
    margin-top: 32px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border-radius: 8px;
    overflow: hidden;
    
    .ant-table-thead > tr > th {
      background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
      font-weight: 600;
    }
  }

  .total-row {
    text-align: right;
    font-size: 18px;
    color: #1890ff;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    margin-top: 16px;
  }
`;

const OrderForm: React.FC = () => {
  const [form] = Form.useForm();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAddItem = () => {
    const newItems = [...items];
    newItems.push({
      name: '',
      quantity: 0,
      price: 0,
      total: 0
    });
    setItems(newItems);
  };

  const handleDeleteItem = (index: number) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const calculateTotal = (item: any) => {
    return item.quantity * item.price;
  };

  const columns = [
    {
      title: 'Наименование',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Количество',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'Сумма',
      dataIndex: 'total',
      key: 'total',
    },
    {
      title: '',
      key: 'action',
      render: (_, __, index) => (
        <Button 
          type="link" 
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteItem(index)}
        />
      ),
    },
  ];

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // Валидация итоговой суммы
      const total = values.items.reduce((sum: number, item: any) => 
        sum + (item.quantity * item.price), 0);
      
      if (total <= 0) {
        throw new Error('Сумма заказа должна быть больше 0');
      }

      await api.post('/orders', values);
      message.success('Заказ успешно создан');
      form.resetFields();
    } catch (error) {
      message.error('Ошибка при создании заказа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledForm form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item name="contractor_id" label="Контрагент" rules={[{ required: true }]}>
        <Select>
          {contractors.map(c => (
            <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item name="delivery_date" label="Дата сдачи" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>

      <div className="items-section">
        <Table
          dataSource={items}
          columns={columns}
          pagination={false}
          className="items-table"
        />
        
        <Button 
          type="dashed" 
          onClick={handleAddItem} 
          icon={<PlusOutlined />}
          style={{ marginTop: 16 }}
        >
          Добавить позицию
        </Button>
      </div>

      <div className="total-row">
        Итого: {items.reduce((sum, item) => sum + calculateTotal(item), 0)} ₽
      </div>

      <Form.Item style={{ marginTop: 24 }}>
        <Button type="primary" htmlType="submit" loading={loading}>
          Сохранить заказ
        </Button>
      </Form.Item>
    </StyledForm>
  );
};

export default OrderForm; 