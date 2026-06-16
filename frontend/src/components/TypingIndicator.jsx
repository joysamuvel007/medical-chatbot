
export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="text-xs text-gray-400 mb-2 font-medium">Healthcare Assistant</div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full dot-1" />
          <div className="w-2 h-2 bg-gray-400 rounded-full dot-2" />
          <div className="w-2 h-2 bg-gray-400 rounded-full dot-3" />
        </div>
      </div>
    </div>
  );
}