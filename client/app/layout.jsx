import "./globals.css";

export const metadata = {
  title: "Pinecraft",
  description: "Reel creation assistant",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
