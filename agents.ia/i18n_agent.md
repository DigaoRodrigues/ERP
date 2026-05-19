# Internationalization (i18n) Agent

## Domain Overview

Expert in multi-language support, translation management, and internationalization patterns for the ERP Multi-Tenant System. Supports Portuguese (Brazil), English (US), and Spanish.

## Core Responsibilities

- Multi-language support implementation
- Translation file management
- Language switching functionality
- Date, number, and currency formatting
- RTL (Right-to-Left) support preparation

---

## Supported Languages

### Primary Languages

1. **Portuguese (Brazil)** - `pt-BR`
   - Primary language for Brazilian marketplace sellers
   - Default language for the application

2. **English (US)** - `en-US`
   - International users
   - Documentation and support

3. **Spanish** - `es`
   - Latin American marketplace expansion
   - Spanish-speaking sellers

---

## Frontend Implementation (Next.js)

### Setup next-intl

```bash
npm install next-intl
```

### Project Structure

```
frontend/
├── messages/
│   ├── pt-BR.json
│   ├── en-US.json
│   └── es.json
├── src/
│   ├── i18n/
│   │   ├── config.ts
│   │   └── request.ts
│   ├── middleware.ts
│   └── app/
│       └── [locale]/
│           ├── layout.tsx
│           └── page.tsx
```

### Configuration

```typescript
// src/i18n/config.ts
export const locales = ['pt-BR', 'en-US', 'es'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'pt-BR';

export const localeNames: Record<Locale, string> = {
  'pt-BR': 'Português (Brasil)',
  'en-US': 'English (US)',
  'es': 'Español'
};

export const localeFlags: Record<Locale, string> = {
  'pt-BR': '🇧🇷',
  'en-US': '🇺🇸',
  'es': '🇪🇸'
};
```

### Request Configuration

```typescript
// src/i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from './config';

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) notFound();

  return {
    messages: (await import(`../../messages/${locale}.json`)).default
  };
});
```

### Middleware

```typescript
// src/middleware.ts
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
```

### Root Layout

```typescript
// src/app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { notFound } from 'next/navigation';
import { locales } from '@/i18n/config';

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  // Validate locale
  if (!locales.includes(locale as any)) {
    notFound();
  }

  let messages;
  try {
    messages = (await import(`../../../messages/${locale}.json`)).default;
  } catch (error) {
    notFound();
  }

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

---

## Translation Files

### Structure

```json
// messages/pt-BR.json
{
  "common": {
    "save": "Salvar",
    "cancel": "Cancelar",
    "delete": "Excluir",
    "edit": "Editar",
    "search": "Pesquisar",
    "loading": "Carregando...",
    "error": "Erro",
    "success": "Sucesso"
  },
  "navigation": {
    "dashboard": "Painel",
    "inventory": "Estoque",
    "products": "Produtos",
    "sales": "Vendas",
    "financial": "Financeiro",
    "settings": "Configurações"
  },
  "inventory": {
    "title": "Gerenciamento de Estoque",
    "addProduct": "Adicionar Produto",
    "sku": "SKU",
    "name": "Nome",
    "quantity": "Quantidade",
    "lowStock": "Estoque Baixo",
    "outOfStock": "Sem Estoque"
  },
  "pricing": {
    "title": "Calculadora de Preços",
    "acquisitionCost": "Custo de Aquisição",
    "shippingCost": "Custo de Envio",
    "commission": "Comissão",
    "profitMargin": "Margem de Lucro",
    "minimumPrice": "Preço Mínimo",
    "calculate": "Calcular"
  },
  "validation": {
    "required": "Este campo é obrigatório",
    "email": "Email inválido",
    "minLength": "Mínimo de {min} caracteres",
    "maxLength": "Máximo de {max} caracteres",
    "positive": "Deve ser um número positivo"
  }
}
```

```json
// messages/en-US.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  },
  "navigation": {
    "dashboard": "Dashboard",
    "inventory": "Inventory",
    "products": "Products",
    "sales": "Sales",
    "financial": "Financial",
    "settings": "Settings"
  },
  "inventory": {
    "title": "Inventory Management",
    "addProduct": "Add Product",
    "sku": "SKU",
    "name": "Name",
    "quantity": "Quantity",
    "lowStock": "Low Stock",
    "outOfStock": "Out of Stock"
  },
  "pricing": {
    "title": "Price Calculator",
    "acquisitionCost": "Acquisition Cost",
    "shippingCost": "Shipping Cost",
    "commission": "Commission",
    "profitMargin": "Profit Margin",
    "minimumPrice": "Minimum Price",
    "calculate": "Calculate"
  },
  "validation": {
    "required": "This field is required",
    "email": "Invalid email",
    "minLength": "Minimum {min} characters",
    "maxLength": "Maximum {max} characters",
    "positive": "Must be a positive number"
  }
}
```

```json
// messages/es.json
{
  "common": {
    "save": "Guardar",
    "cancel": "Cancelar",
    "delete": "Eliminar",
    "edit": "Editar",
    "search": "Buscar",
    "loading": "Cargando...",
    "error": "Error",
    "success": "Éxito"
  },
  "navigation": {
    "dashboard": "Panel",
    "inventory": "Inventario",
    "products": "Productos",
    "sales": "Ventas",
    "financial": "Financiero",
    "settings": "Configuración"
  },
  "inventory": {
    "title": "Gestión de Inventario",
    "addProduct": "Agregar Producto",
    "sku": "SKU",
    "name": "Nombre",
    "quantity": "Cantidad",
    "lowStock": "Stock Bajo",
    "outOfStock": "Sin Stock"
  },
  "pricing": {
    "title": "Calculadora de Precios",
    "acquisitionCost": "Costo de Adquisición",
    "shippingCost": "Costo de Envío",
    "commission": "Comisión",
    "profitMargin": "Margen de Beneficio",
    "minimumPrice": "Precio Mínimo",
    "calculate": "Calcular"
  },
  "validation": {
    "required": "Este campo es obligatorio",
    "email": "Email inválido",
    "minLength": "Mínimo {min} caracteres",
    "maxLength": "Máximo {max} caracteres",
    "positive": "Debe ser un número positivo"
  }
}
```

---

## Using Translations

### In Server Components

```typescript
// app/[locale]/inventory/page.tsx
import { useTranslations } from 'next-intl';

export default function InventoryPage() {
  const t = useTranslations('inventory');

  return (
    <div>
      <h1>{t('title')}</h1>
      <button>{t('addProduct')}</button>
    </div>
  );
}
```

### In Client Components

```typescript
'use client';

import { useTranslations } from 'next-intl';

export function ProductForm() {
  const t = useTranslations('inventory');
  const tCommon = useTranslations('common');

  return (
    <form>
      <label>{t('sku')}</label>
      <input type="text" />
      
      <button type="submit">{tCommon('save')}</button>
      <button type="button">{tCommon('cancel')}</button>
    </form>
  );
}
```

### With Parameters

```typescript
const t = useTranslations('validation');

// Usage: "Minimum 8 characters"
<p>{t('minLength', { min: 8 })}</p>
```

---

## Language Switcher Component

```typescript
// components/LanguageSwitcher.tsx
'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { locales, localeNames, localeFlags } from '@/i18n/config';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLanguageChange = (newLocale: string) => {
    // Remove current locale from pathname
    const pathnameWithoutLocale = pathname.replace(`/${locale}`, '');
    
    // Navigate to new locale
    router.push(`/${newLocale}${pathnameWithoutLocale}`);
  };

  return (
    <div className="relative">
      <select
        value={locale}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="px-4 py-2 border rounded-lg"
      >
        {locales.map((loc) => (
          <option key={loc} value={loc}>
            {localeFlags[loc]} {localeNames[loc]}
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## Formatting

### Numbers

```typescript
import { useFormatter } from 'next-intl';

export function PriceDisplay({ amount }: { amount: number }) {
  const format = useFormatter();

  return (
    <div>
      {/* Currency formatting */}
      <p>{format.number(amount, { style: 'currency', currency: 'BRL' })}</p>
      
      {/* Percentage */}
      <p>{format.number(0.15, { style: 'percent' })}</p>
      
      {/* Decimal */}
      <p>{format.number(1234.56, { minimumFractionDigits: 2 })}</p>
    </div>
  );
}
```

### Dates

```typescript
import { useFormatter } from 'next-intl';

export function DateDisplay({ date }: { date: Date }) {
  const format = useFormatter();

  return (
    <div>
      {/* Full date */}
      <p>{format.dateTime(date, { dateStyle: 'full' })}</p>
      
      {/* Short date */}
      <p>{format.dateTime(date, { dateStyle: 'short' })}</p>
      
      {/* Custom format */}
      <p>{format.dateTime(date, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })}</p>
    </div>
  );
}
```

### Relative Time

```typescript
import { useFormatter } from 'next-intl';

export function RelativeTime({ date }: { date: Date }) {
  const format = useFormatter();

  return (
    <p>{format.relativeTime(date)}</p>
    // Output: "2 days ago" / "há 2 dias" / "hace 2 días"
  );
}
```

---

## Backend API Localization

### Accept-Language Header

```python
from fastapi import Header, Request
from typing import Optional

SUPPORTED_LANGUAGES = ["pt-BR", "en-US", "es"]
DEFAULT_LANGUAGE = "pt-BR"

def get_user_language(
    accept_language: Optional[str] = Header(None)
) -> str:
    """Extract user's preferred language from Accept-Language header."""
    if not accept_language:
        return DEFAULT_LANGUAGE
    
    # Parse Accept-Language header
    # Format: "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    languages = []
    for lang in accept_language.split(','):
        parts = lang.strip().split(';')
        locale = parts[0]
        quality = 1.0
        
        if len(parts) > 1 and parts[1].startswith('q='):
            try:
                quality = float(parts[1][2:])
            except ValueError:
                quality = 0.0
        
        languages.append((locale, quality))
    
    # Sort by quality
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # Find first supported language
    for locale, _ in languages:
        if locale in SUPPORTED_LANGUAGES:
            return locale
        # Check base language (e.g., "pt" from "pt-BR")
        base = locale.split('-')[0]
        for supported in SUPPORTED_LANGUAGES:
            if supported.startswith(base):
                return supported
    
    return DEFAULT_LANGUAGE
```

### Localized Error Messages

```python
# app/core/i18n.py
from typing import Dict

ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "product_not_found": {
        "pt-BR": "Produto não encontrado",
        "en-US": "Product not found",
        "es": "Producto no encontrado"
    },
    "insufficient_stock": {
        "pt-BR": "Estoque insuficiente",
        "en-US": "Insufficient stock",
        "es": "Stock insuficiente"
    },
    "invalid_price": {
        "pt-BR": "Preço inválido",
        "en-US": "Invalid price",
        "es": "Precio inválido"
    }
}

def get_error_message(key: str, language: str = "pt-BR") -> str:
    """Get localized error message."""
    messages = ERROR_MESSAGES.get(key, {})
    return messages.get(language, messages.get("en-US", key))
```

### Usage in Endpoints

```python
@router.get("/products/{product_id}")
async def get_product(
    product_id: str,
    language: str = Depends(get_user_language),
    db: Session = Depends(get_db)
):
    """Get product with localized error messages."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail=get_error_message("product_not_found", language)
        )
    
    return product
```

---

## Database Localization

### Translatable Content

```python
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class ProductTranslation(Base):
    """Product translations for different languages."""
    __tablename__ = "product_translations"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False)
    language = Column(String(10), nullable=False)  # pt-BR, en-US, es
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    __table_args__ = (
        UniqueConstraint('product_id', 'language'),
    )
```

### Query with Fallback

```python
def get_product_with_translation(
    db: Session,
    product_id: str,
    language: str = "pt-BR"
) -> dict:
    """Get product with translation, fallback to default language."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return None
    
    # Try to get translation
    translation = db.query(ProductTranslation).filter(
        ProductTranslation.product_id == product_id,
        ProductTranslation.language == language
    ).first()
    
    # Fallback to default language
    if not translation:
        translation = db.query(ProductTranslation).filter(
            ProductTranslation.product_id == product_id,
            ProductTranslation.language == "pt-BR"
        ).first()
    
    return {
        "id": product.id,
        "sku": product.sku,
        "name": translation.name if translation else product.sku,
        "description": translation.description if translation else None,
        "language": language
    }
```

---

## Best Practices

### 1. Consistent Key Naming

```json
// ✅ GOOD: Hierarchical, descriptive keys
{
  "inventory": {
    "title": "Inventory Management",
    "addProduct": "Add Product"
  }
}

// ❌ BAD: Flat, unclear keys
{
  "inv_title": "Inventory Management",
  "add_prod": "Add Product"
}
```

### 2. Avoid Hardcoded Text

```typescript
// ❌ BAD
<button>Save</button>

// ✅ GOOD
<button>{t('common.save')}</button>
```

### 3. Use Parameters for Dynamic Content

```json
{
  "itemsFound": "{count} items found"
}
```

```typescript
t('itemsFound', { count: products.length })
```

### 4. Keep Translations Synchronized

- Use a translation management tool
- Review translations regularly
- Test all languages before deployment

---

## Testing

### Test Language Switching

```typescript
// __tests__/LanguageSwitcher.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

describe('LanguageSwitcher', () => {
  it('changes language when selected', () => {
    render(<LanguageSwitcher />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'en-US' } });
    
    expect(select.value).toBe('en-US');
  });
});
```

---

## Related Agents

- **Next.js & React Agent**: Frontend implementation patterns
- **API Design Agent**: Backend localization
- **Database Agent**: Translatable content storage

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
