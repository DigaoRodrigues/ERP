export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          ERP Multi-Tenant System
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Marketplace Seller Management Platform
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/docs"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            API Documentation
          </a>
          <a
            href="/login"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
          >
            Login
          </a>
        </div>
      </div>
    </main>
  )
}
