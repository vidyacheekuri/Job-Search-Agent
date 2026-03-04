import React from 'react';
import type { SearchHistoryItem } from '../types/job';

interface SearchHistoryProps {
  history: SearchHistoryItem[];
  onSelect: (item: SearchHistoryItem) => void;
  onClear: () => void;
  onRemove: (id: string) => void;
}

export const SearchHistory: React.FC<SearchHistoryProps> = ({ history, onSelect, onClear, onRemove }) => {
  if (history.length === 0) return null;

  return (
    <div className="mb-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Recent Searches
        </h3>
        <button
          onClick={onClear}
          className="text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
        >
          Clear all
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {history.slice(0, 8).map((item) => (
          <div
            key={item.id}
            className="group flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1.5 hover:bg-teal-50 dark:hover:bg-teal-900/30 transition-colors cursor-pointer"
            onClick={() => onSelect(item)}
          >
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {item.keyword}
            </span>
            {item.location && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                • {item.location}
              </span>
            )}
            <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">
              ({item.resultCount})
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(item.id);
              }}
              className="ml-1 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
