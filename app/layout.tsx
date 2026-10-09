import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'ScenarioLab — Explore what happens next', description: 'Run structured AI scenario simulations with distinct perspectives, risks and uncertainty.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
