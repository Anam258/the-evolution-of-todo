import './globals.css';

export const metadata = {
  title: 'Nuralyx Flow',
  description: 'Nuralyx Flow — Intelligent task management with authentication',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
