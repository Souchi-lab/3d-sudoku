import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SoChi BLOCKS — Hyper-Cube Sudoku",
  description: "3D turn-based Sudoku puzzle game by SoChi BLOCKS",
};

// Covers notch / Dynamic Island and prevents iOS auto-zoom
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
