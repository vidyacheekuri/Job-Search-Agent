import React from 'react';

export const SkeletonCard: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
      <div className="flex gap-4">
        <div className="w-12 h-12 rounded-lg skeleton" />
        <div className="flex-1 space-y-3">
          <div className="h-5 skeleton rounded w-3/4" />
          <div className="h-4 skeleton rounded w-1/2" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <div className="flex gap-2">
          <div className="h-4 skeleton rounded w-24" />
          <div className="h-4 skeleton rounded w-20" />
        </div>
        <div className="h-4 skeleton rounded w-full" />
        <div className="h-4 skeleton rounded w-5/6" />
      </div>
      <div className="mt-4 flex justify-between">
        <div className="h-8 skeleton rounded w-24" />
        <div className="flex gap-2">
          <div className="h-8 w-8 skeleton rounded" />
          <div className="h-8 w-8 skeleton rounded" />
        </div>
      </div>
    </div>
  );
};

export const SkeletonList: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
};
