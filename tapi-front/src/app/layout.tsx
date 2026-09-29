import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TAPI - Sistema de Fidelización NFC",
  description: "Plataforma de fidelización y gestión de reseñas para tiendas físicas.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        {children}
      </body>
    </html>
  );
}
