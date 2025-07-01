'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { 
  AlertCircle, 
  ArrowLeft,
  Shield,
  RefreshCw
} from 'lucide-react';

const AuthErrorPage: React.FC = () => {
  const searchParams = useSearchParams();
  const error = searchParams?.get('error');

  const getErrorDetails = (error: string | null | undefined) => {
    switch (error) {
      case 'Configuration':
        return {
          title: 'Server Configuration Error',
          description: 'There is a problem with the server configuration. Please contact support.',
          suggestion: 'Try again later or contact our support team.',
        };
      case 'AccessDenied':
        return {
          title: 'Access Denied',
          description: 'You do not have permission to sign in with this account.',
          suggestion: 'Please contact your administrator or try a different account.',
        };
      case 'Verification':
        return {
          title: 'Email Verification Required',
          description: 'Your email address needs to be verified before you can sign in.',
          suggestion: 'Please check your email and click the verification link.',
        };
      case 'OAuthSignin':
      case 'OAuthCallback':
      case 'OAuthCreateAccount':
      case 'EmailCreateAccount':
      case 'Callback':
        return {
          title: 'Sign In Failed',
          description: 'There was an error during the sign in process.',
          suggestion: 'Please try signing in again.',
        };
      case 'OAuthAccountNotLinked':
        return {
          title: 'Account Not Linked',
          description: 'This account is not linked to your existing account.',
          suggestion: 'Try signing in with the method you used to create your account.',
        };
      case 'EmailSignin':
        return {
          title: 'Email Sign In Error',
          description: 'Unable to send the verification email.',
          suggestion: 'Please check your email address and try again.',
        };
      case 'CredentialsSignin':
        return {
          title: 'Invalid Credentials',
          description: 'The email or password you entered is incorrect.',
          suggestion: 'Please check your credentials and try again.',
        };
      case 'SessionRequired':
        return {
          title: 'Session Required',
          description: 'You must be signed in to view this page.',
          suggestion: 'Please sign in to continue.',
        };
      case 'Default':
      default:
        return {
          title: 'Authentication Error',
          description: 'An unexpected error occurred during authentication.',
          suggestion: 'Please try again or contact support if the problem persists.',
        };
    }
  };

  const errorDetails = getErrorDetails(error);

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-slate-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div 
        className="max-w-md w-full space-y-8"
        {...fadeInUp}
      >
        {/* Header */}
        <div className="text-center">
          <motion.div
            className="flex items-center justify-center space-x-2 mb-8"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Shield className="h-10 w-10 text-blue-600" />
            <h1 className="text-3xl font-bold text-slate-900">TradeMate</h1>
          </motion.div>
        </div>

        {/* Error Card */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-8 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="flex justify-center mb-6">
            <div className="bg-red-100 rounded-full p-3">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold text-slate-900 mb-4">
            {errorDetails.title}
          </h2>
          
          <p className="text-slate-600 mb-2">
            {errorDetails.description}
          </p>
          
          <p className="text-sm text-slate-500 mb-8">
            {errorDetails.suggestion}
          </p>
          
          {/* Error Code */}
          {error && (
            <div className="bg-slate-50 rounded-lg p-3 mb-6">
              <p className="text-xs font-mono text-slate-600">
                Error Code: {error}
              </p>
            </div>
          )}
          
          <div className="space-y-4">
            {/* Primary Action */}
            <Link 
              href="/auth/signin"
              className="w-full inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Try signing in again
            </Link>
            
            {/* Secondary Actions */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center justify-center px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Retry
              </button>
              
              <Link 
                href="/auth/signup"
                className="inline-flex items-center justify-center px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Sign up
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Help Section */}
        <motion.div 
          className="bg-white rounded-xl shadow-lg p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <h3 className="text-lg font-semibold text-slate-900 mb-4 text-center">
            Need Help?
          </h3>
          
          <div className="space-y-3 text-sm text-slate-600">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <p className="font-medium text-slate-700">Check Your Internet Connection</p>
                <p>Make sure you have a stable internet connection.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <p className="font-medium text-slate-700">Clear Browser Cache</p>
                <p>Try clearing your browser cache and cookies.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <p className="font-medium text-slate-700">Contact Support</p>
                <p>
                  If the problem persists, please{' '}
                  <Link 
                    href="/support" 
                    className="text-blue-600 hover:text-blue-800 transition-colors underline"
                  >
                    contact our support team
                  </Link>
                  .
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Back to Home */}
        <motion.div 
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          <Link 
            href="/" 
            className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
          >
            ← Back to homepage
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default AuthErrorPage;