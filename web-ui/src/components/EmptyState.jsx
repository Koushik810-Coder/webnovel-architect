import { BookOpen, AlertCircle, Headphones, Search } from 'lucide-react';

const icons = {
  book: BookOpen,
  error: AlertCircle,
  audio: Headphones,
  search: Search,
};

export default function EmptyState({ icon = 'book', title, message, action, onAction }) {
  const Icon = icons[icon] || BookOpen;
  return (
    <div className="empty-state fade-in">
      <Icon size={64} />
      <h3>{title}</h3>
      <p>{message}</p>
      {action && onAction && (
        <button onClick={onAction}>{action}</button>
      )}
    </div>
  );
}
