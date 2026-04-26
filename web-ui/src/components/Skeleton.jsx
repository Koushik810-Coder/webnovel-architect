export function SkeletonCard() {
  return <div className="skeleton skeleton-card" />;
}

export function SkeletonLine({ width = '100%' }) {
  return <div className="skeleton skeleton-line" style={{ width }} />;
}

export function SkeletonTitle({ width = '60%' }) {
  return <div className="skeleton skeleton-title" style={{ width }} />;
}

export function LibrarySkeleton() {
  return (
    <div className="grid">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="card card--static" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="skeleton" style={{ height: 200 }} />
          <div style={{ padding: '1.25rem' }}>
            <SkeletonTitle />
            <SkeletonLine width="90%" />
            <SkeletonLine width="70%" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ChapterListSkeleton() {
  return (
    <div className="chapters-list">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="chapter-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="skeleton skeleton-avatar" style={{ width: 36, height: 36 }} />
            <SkeletonLine width="180px" />
          </div>
          <div className="skeleton" style={{ width: 80, height: 36, borderRadius: 'var(--radius-sm)' }} />
        </div>
      ))}
    </div>
  );
}
