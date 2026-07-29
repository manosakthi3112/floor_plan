import Link from 'next/link';

export default function MarketingPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white">
      <h1 className="text-5xl font-bold text-gray-900 mb-4">PlanCraft3D</h1>
      <p className="text-xl text-gray-600 mb-8 text-center max-w-md">
        Turn floor plans into 3D designs. Upload, edit, and customize in minutes.
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-lg bg-primary-600 px-6 py-3 text-white font-medium hover:bg-primary-700"
        >
          Get Started
        </Link>
        <Link
          href="/register"
          className="rounded-lg border border-gray-300 px-6 py-3 text-gray-700 font-medium hover:bg-gray-50"
        >
          Create Account
        </Link>
      </div>
    </div>
  );
}
