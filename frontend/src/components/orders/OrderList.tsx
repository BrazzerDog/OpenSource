import React, { useState, useEffect } from 'react';
import { Table, DatePicker, Switch, Modal, Button, Space, Tag, message } from 'antd';
import { ExclamationCircleOutlined, EditOutlined, DeleteOutlined, PrinterOutlined } from '@ant-design/icons';
import type { RangePickerProps } from 'antd/es/date-picker';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import api from '../../services/api';
import moment from 'moment';

const { RangePicker } = DatePicker;
const { confirm } = Modal;

const StyledWrapper = styled.div`
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);

  .filters-section {
    margin-bottom: 24px;
    padding: 16px;
    background: #fafafa;
    border-radius: 6px;
    border: 1px solid #f0f0f0;
    
    .ant-space {
      width: 100%;
      justify-content: space-between;
    }
  }

  .ant-table-thead > tr > th {
    background: #f7f7f7;
    font-weight: 600;
  }

  .status-tag {
    min-width: 100px;
    text-align: center;
    
    &.delivered {
      background: #e6f7ff;
      color: #1890ff;
      border: 1px solid #91d5ff;
    }
    
    &.pending {
      background: #fff7e6;
      color: #fa8c16;
      border: 1px solid #ffd591;
    }
  }

  .actions-column {
    .ant-btn {
      padding: 4px 8px;
      height: 32px;
      
      &:hover {
        transform: translateY(-1px);
        transition: all 0.2s;
      }
    }
  }
`;

interface Contractor {
  id: number;
  name: string;
}

interface Order {
  id: number;
  date: string;
  delivery_date: string;
  is_delivered: boolean;
  contractor: Contractor;
  total: number;
  items: OrderItem[];
}

interface OrderItem {
  id: number;
  name: string;
  quantity: number;
  price: number;
  total: number;
}

const disabledDate: RangePickerProps['disabledDate'] = (current) => {
  return current && current > moment().endOf('day');
};

const OrderList: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[moment.Moment | null, moment.Moment | null]>([null, null]);
  const [isDelivered, setIsDelivered] = useState<boolean | null>(null);
  const navigate = useNavigate();

  const columns = [
    {
      title: '№',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: 'Дата',
      dataIndex: 'date',
      render: (date: string) => moment(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Контрагент',
      dataIndex: ['contractor', 'name'],
    },
    {
      title: 'Дата сдачи',
      dataIndex: 'delivery_date',
      render: (date: string) => moment(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Статус',
      dataIndex: 'is_delivered',
      render: (delivered: boolean) => (
        <Tag className={`status-tag ${delivered ? 'delivered' : 'pending'}`}>
          {delivered ? 'Сдан' : 'В работе'}
        </Tag>
      ),
    },
    {
      title: 'Сумма',
      dataIndex: 'total',
      align: 'right' as const,
      render: (total: number) => `${total.toLocaleString()} ₽`,
    },
    {
      title: 'Действия',
      key: 'actions',
      className: 'actions-column',
      render: (_: any, record: Order) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => navigate(`/orders/${record.id}/edit`)}
          />
          <Button 
            type="link" 
            icon={<PrinterOutlined />}
            onClick={() => handlePrint(record.id)}
          />
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />}
            onClick={() => showDeleteConfirm(record.id)}
          />
        </Space>
      ),
    },
  ] as const;

  const showDeleteConfirm = (id: number) => {
    confirm({
      title: 'Удаление заказа',
      icon: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
      content: 'Вы уверены, что хотите удалить этот заказ?',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk() {
        handleDelete(id);
      },
      className: 'delete-modal',
    });
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/orders/${id}`);
      setOrders(prev => prev.filter(order => order.id !== id));
      message.success('Заказ успешно удален');
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message);
      } else {
        message.error('Произошла ошибка при удалении заказа');
      }
    }
  };

  const handlePrint = async (id: number) => {
    window.open(`/api/orders/${id}/pdf`, '_blank');
  };

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const params = {
          date_from: dateRange[0]?.format('YYYY-MM-DD'),
          date_to: dateRange[1]?.format('YYYY-MM-DD'),
          is_delivered: isDelivered
        };

        const response = await api.get<Order[]>('/orders', { params });
        setOrders(response.data);
      } catch (error) {
        if (error instanceof Error) {
          message.error(error.message);
        } else {
          message.error('Ошибка при загрузке заказов');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [dateRange, isDelivered]);

  return (
    <StyledWrapper>
      <div className="filters-section">
        <Space>
          <RangePicker 
            value={dateRange}
            onChange={(dates: [moment.Moment | null, moment.Moment | null]) => setDateRange(dates)}
            placeholder={['Дата с', 'Дата по']}
            disabledDate={disabledDate}
          />
          <Switch
            checkedChildren="Сданные"
            unCheckedChildren="Все"
            checked={isDelivered || false}
            onChange={setIsDelivered}
          />
          <Button type="primary" onClick={() => navigate('/orders/new')}>
            Создать заказ
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={orders}
        rowKey="id"
        loading={loading}
        pagination={{
          total: orders.length,
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Всего ${total} записей`,
        }}
      />
    </StyledWrapper>
  );
};

export default OrderList; 