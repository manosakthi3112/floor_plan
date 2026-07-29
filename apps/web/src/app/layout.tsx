import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PlanCraft3D',
  description: 'Turn floor plans into 3D designs',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="h-full">{children}</body>
    </html>
  );
}
