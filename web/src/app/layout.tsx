import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { LocaleProvider } from "@/context/LocaleContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pyre Code",
  description: "68 hands-on AI systems challenges — implement the internals of attention, RLHF, diffusion, and distributed training",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-surface`}>
        <LocaleProvider>{children}</LocaleProvider>
      </body>
    </html>
  );
}
