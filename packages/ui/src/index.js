export function Button({ children, onClick, style }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        borderRadius: '8px',
        border: 'none',
        backgroundColor: '#0070f3',
        color: 'white',
        cursor: 'pointer',
        ...style,
      }}
    >
      {children}
    </button>
  );
}

export function Card({ children, style }) {
  return (
    <div
      style={{
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        backgroundColor: 'white',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
