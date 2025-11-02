export default function HomePage() {
    return (
      <main className="flex flex-col min-h-screen items-center justify-center bg-gray-100">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Welcome to PineReel 🎬
        </h1>
        <div className="flex gap-4">
          <a
            href="/login"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Login
          </a>
          <a
            href="/register"
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Register
          </a>
        </div>
      </main>
    );
  }
  