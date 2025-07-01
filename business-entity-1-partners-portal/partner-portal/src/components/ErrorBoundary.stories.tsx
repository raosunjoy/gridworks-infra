import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import ErrorBoundary from './ErrorBoundary';
import React from 'react';

// Component that throws an error for testing
const ErrorThrowingComponent: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('This is a test error for Storybook demonstration');
  }
  return <div className="p-4 bg-green-100 text-green-800 rounded">Component is working correctly!</div>;
};

// Component that works normally
const WorkingComponent: React.FC = () => {
  return (
    <div className="p-8 space-y-4">
      <h2 className="text-2xl font-bold text-slate-900">Working Component</h2>
      <p className="text-slate-600">This component renders without any errors.</p>
      <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
        Click me
      </button>
    </div>
  );
};

const meta: Meta<typeof ErrorBoundary> = {
  title: 'Components/ErrorBoundary',
  component: ErrorBoundary,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'An error boundary component that catches JavaScript errors anywhere in the child component tree and displays a fallback UI.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    onError: {
      description: 'Callback function called when an error is caught',
      action: 'error-caught',
    },
    fallback: {
      description: 'Custom fallback component to render when an error occurs',
      control: false,
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Working component (no error)
export const NoError: Story = {
  args: {
    onError: action('error-caught'),
  },
  render: (args) => (
    <ErrorBoundary {...args}>
      <WorkingComponent />
    </ErrorBoundary>
  ),
};

// Component that throws an error
export const WithError: Story = {
  args: {
    onError: action('error-caught'),
  },
  render: (args) => (
    <ErrorBoundary {...args}>
      <ErrorThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
};

// Custom fallback UI
export const CustomFallback: Story = {
  args: {
    onError: action('error-caught'),
    fallback: (
      <div className="p-8 text-center bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-lg font-semibold text-red-800 mb-2">Custom Error Fallback</h3>
        <p className="text-red-600 mb-4">This is a custom fallback UI for when errors occur.</p>
        <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">
          Retry
        </button>
      </div>
    ),
  },
  render: (args) => (
    <ErrorBoundary {...args}>
      <ErrorThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
};

// Multiple components, one throws error
export const PartialError: Story = {
  args: {
    onError: action('error-caught'),
  },
  render: (args) => (
    <div className="space-y-4">
      <div className="p-4 bg-blue-50 rounded">
        <h3 className="font-semibold text-blue-800">Component 1 (Working)</h3>
        <WorkingComponent />
      </div>
      
      <div className="p-4 bg-red-50 rounded">
        <h3 className="font-semibold text-red-800">Component 2 (Error Boundary)</h3>
        <ErrorBoundary {...args}>
          <ErrorThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      </div>
      
      <div className="p-4 bg-green-50 rounded">
        <h3 className="font-semibold text-green-800">Component 3 (Working)</h3>
        <WorkingComponent />
      </div>
    </div>
  ),
};

// Dark theme
export const DarkTheme: Story = {
  args: {
    onError: action('error-caught'),
  },
  render: (args) => (
    <div className="bg-slate-900 p-8 rounded-lg">
      <ErrorBoundary {...args}>
        <ErrorThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    </div>
  ),
  parameters: {
    backgrounds: {
      default: 'dark',
    },
  },
};

// Mobile view
export const Mobile: Story = {
  args: {
    onError: action('error-caught'),
  },
  render: (args) => (
    <ErrorBoundary {...args}>
      <ErrorThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
  parameters: {
    viewport: {
      defaultViewport: 'mobile',
    },
  },
};