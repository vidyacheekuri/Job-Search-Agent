import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  const getErrorDetails = (msg: string): { title: string; description: string; icon: string } => {
    if (msg.includes('Network') || msg.includes('fetch') || msg.includes('Connection')) {
      return {
        title: 'Connection Error',
        description: 'Unable to connect to the server. Please check if the API is running.',
        icon: 'network'
      };
    }
    if (msg.includes('429') || msg.includes('rate limit')) {
      return {
        title: 'Too Many Requests',
        description: 'LinkedIn is rate limiting requests. Please wait a moment and try again.',
        icon: 'clock'
      };
    }
    if (msg.includes('403') || msg.includes('blocked')) {
      return {
        title: 'Access Blocked',
        description: 'LinkedIn may be blocking requests. Try again later or use different search terms.',
        icon: 'block'
      };
    }
    if (msg.includes('404')) {
      return {
        title: 'Not Found',
        description: 'No jobs found matching your criteria. Try different search terms.',
        icon: 'search'
      };
    }
    return {
      title: 'Something Went Wrong',
      description: msg,
      icon: 'error'
    };
  };

  const { title, description, icon } = getErrorDetails(message);

  const renderIcon = () => {
    const iconClass = "w-12 h-12 text-red-500 dark:text-red-400";
    switch (icon) {
      case 'network':
        return (
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
          </svg>
        );
      case 'clock':
        return (
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'block':
        return (
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
        );
      case 'search':
        return (
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        );
      default:
        return (
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="bg-red-50 dark:bg-red-900/20 rounded-full p-4 mb-4">
        {renderIcon()}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400 text-center max-w-md mb-4">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
