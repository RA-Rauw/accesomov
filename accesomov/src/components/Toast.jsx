import { useEffect } from 'react'

export default function Toast({ message, onClose }) {
  useEffect(() => {
    const id = setTimeout(onClose, 5000)
    return () => clearTimeout(id)
  }, [onClose])

  return (
    <div className="fixed bottom-5 right-5 z-50 max-w-sm animate-in">
      <div className="flex items-start gap-3 bg-gray-900 border border-red-800/70 text-white p-4 rounded-xl shadow-2xl">
        <span className="text-red-400 text-lg flex-shrink-0 mt-0.5">⚠</span>
        <p className="text-sm text-gray-200 flex-1 leading-snug">{message}</p>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-white flex-shrink-0 text-sm leading-none mt-0.5"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
