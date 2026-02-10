import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nuralyx Flow',
  description: 'Intelligent task management — Dual Interface (CUI + GUI)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen">{children}</body>
    </html>
  );
}
