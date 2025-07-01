import type { Meta, StoryObj } from '@storybook/react';
import SignInForm from './SignInForm';

const meta: Meta<typeof SignInForm> = {
  title: 'Authentication/SignInForm',
  component: SignInForm,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A comprehensive sign-in form with email/password authentication and social login options.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    error: {
      description: 'Error message to display',
      control: 'text',
    },
    callbackUrl: {
      description: 'URL to redirect to after successful sign-in',
      control: 'text',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Default story
export const Default: Story = {
  args: {
    callbackUrl: '/dashboard',
  },
};

// With Error
export const WithError: Story = {
  args: {
    callbackUrl: '/dashboard',
    error: 'Invalid credentials. Please check your email and password.',
  },
};

// Custom Callback
export const CustomCallback: Story = {
  args: {
    callbackUrl: '/admin/dashboard',
  },
};