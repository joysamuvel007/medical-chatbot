
export default function StatusBar({ healthStatus, onCheck }) {
  if (!healthStatus) {
    return (
      <button
        onClick={onCheck}
        className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
      >
        Check AI status
      </button>
    );
  }

  const isHealthy = healthStatus.ollama_running;

  return (
    <div className="flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-400'}`} />
      <span className={`text-xs font-medium ${isHealthy ? 'text-green-700' : 'text-red-600'}`}>
        {isHealthy
          ? `AI Ready (${healthStatus.available_models?.[0] || 'model loaded'})`
          : 'Ollama not running — run: ollama serve'
        }
      </span>
    </div>
  );
}