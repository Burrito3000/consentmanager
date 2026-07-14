import AuthGuard from "@/components/auth-guard";
import AppLayout from "@/components/app-layout";

export default function AppRootLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AppLayout>{children}</AppLayout>
    </AuthGuard>
  );
}
