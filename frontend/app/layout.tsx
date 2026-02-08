import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dental.AI - Gestión de Consultorio Dental",
  description: "Sistema completo de gestión para consultorios dentales",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="antialiased bg-gray-50">
        {children}
      </body>
    </html>
  );
}
