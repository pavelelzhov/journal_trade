import "./globals.css";
import { PropsWithChildren } from "react";
import { Providers } from "@/components/providers";
import { AccessPanel } from "@/components/access-panel";
import { ModeSwitch } from "@/components/mode-switch";
import { Nav } from "@/components/nav";

export const metadata = {
  title: "Top Journal UI v1",
};

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="mx-auto max-w-7xl space-y-4 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h1 className="text-xl font-bold">Top Journal UI v1</h1>
              <div className="flex items-center gap-2"><ModeSwitch /><AccessPanel /></div>
            </div>
            <Nav />
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
