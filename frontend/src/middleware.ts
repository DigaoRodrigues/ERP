import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'always' // Always use locale prefix in URL
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(pt-BR|en-US|es)/:path*']
};
