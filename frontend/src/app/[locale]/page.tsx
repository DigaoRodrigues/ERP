import { useTranslations } from 'next-intl';

export default function Home() {
  const t = useTranslations('navigation');

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8">
          ERP Multi-Tenant System
        </h1>
        <p className="text-lg mb-4">
          {t('dashboard')}
        </p>
      </div>
    </main>
  );
}