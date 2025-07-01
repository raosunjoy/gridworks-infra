import type { Meta, StoryObj } from '@storybook/react';
import { ToastProvider } from './ToastProvider';
import React from 'react';

const meta: Meta<typeof ToastProvider> = {
  title: 'UI/ToastProvider',
  component: ToastProvider,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Toast notification provider component that manages toast notifications globally.',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

// Basic story
export const Default: Story = {
  render: () => (
    <ToastProvider>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Toast Provider Example</h1>
        <p>This component provides toast notification functionality to the app.</p>
      </div>
    </ToastProvider>
  ),
};