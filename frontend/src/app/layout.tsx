import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/contexts/QueryProvider";
import { ToastProvider } from "@/contexts/ToastProvider";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Agents Management",
  description: "Gestiona tus agentes de inteligencia artificial y sus documentos",
  keywords: ["IA", "Agentes", "Documentos", "Gestión", "FastAPI", "Next.js"],
  authors: [{ name: "Emmanuel Valbuena" }],
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          <QueryProvider>
            {children}
            <ToastProvider />
          </QueryProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
