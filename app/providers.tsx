"use client";
import { ThemeProvider } from "next-themes";
import { TabProvider } from "@/lib/tab-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <TabProvider>{children}</TabProvider>
    </ThemeProvider>
  );
}
